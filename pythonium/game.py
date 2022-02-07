import logging

from . import cfg
from .orders import galaxy as galaxy_orders
from .orders import planet as planet_orders
from .orders import ship as ship_orders
from .orders.request import PlanetOrderRequest, ShipOrderRequest

logger = logging.getLogger("game")


class Game:
    def __init__(
        self,
        name,
        players,
        game_mode,
        output_handler,
        orders_extractor,
    ):
        """
        :param name: Name for the galaxy. Also used as game identifier.
        :type name: str
        :param players: Players for the game. Supports one or two players.
        :type players: list of instances of classes that extends
            from :class:`AbstractPlayer`
        :param game_mode: Class that define some game rules
        :type game_mode: :class:GameMode
        """
        if len(players) != len({p.name for p in players}):
            raise ValueError("Player names must be unique")

        self.game_mode = game_mode
        self.players = players
        self.output_handler = output_handler
        self._extract_orders = orders_extractor
        logger.info(
            "Initializing galaxy",
            extra={"players": len(self.players), "galaxy_name": name},
        )
        self.galaxy = self.game_mode.build_galaxy(name, self.players)
        logger.info("Galaxy initialized")
        self.output_handler.start(self.galaxy)

    def play(self):
        while True:

            logger.info("Turn started", extra={"turn": self.galaxy.turn})

            context = self.game_mode.get_context(
                self.galaxy, self.players, self.galaxy.turn
            )

            self.output_handler.step(self.galaxy, context)

            # log current score
            for player_score in context["score"]:
                logger.info("Current score", extra=player_score)

            orders = self._extract_orders(
                players=self.players,
                context=context,
                galaxy=self.galaxy,
            )

            if self.game_mode.has_ended(self.galaxy, self.galaxy.turn):
                self.end_game()
                break
            self.run_turn(orders)

    def end_game(self):
        logger.info(
            "Game ended",
            extra={
                "turn": self.galaxy.turn,
                "winner": self.game_mode.winner,
            },
        )
        self.output_handler.finish(self.galaxy, self.game_mode.winner)

    def run_turn(self, orders):
        """
        Execute turn orders in the following order.
        1. Ships download transfers :func:`action_ship_transfer`
        2. Ships upload transfers :func:`action_ship_transfer`
        3. Mines construction :func:`action_planet_build_mines`
        4. Taxes changes
        5. Ships movements :func:`action_ship_move`
        6. Resolve ship to ship combats :func:`resolve_ship_to_ship`
        7. Resolve ship to planet combats :func:`resolve_planet_to_ship`
        8. Ships construction :func:`action_planet_build_ship`
        9. Population changes
        10. Happypoints changes
        11. Taxes recollection
        12. Pythonium extraction
        """
        # Reset explosions
        self.galaxy.explosions = []
        # 1. Ships download transfers
        # 2. Ships upload transfers
        self.run_player_action(
            "ship_transfer", orders.get("ship_transfer", [])
        )

        # 3. Mines construction
        self.run_player_action(
            "planet_build_mines", orders.get("planet_build_mines", [])
        )

        # 4. Taxes changes
        self.run_player_action(
            "planet_set_taxes", orders.get("planet_set_taxes", [])
        )

        # 5. Ship movements
        self.run_player_action("ship_move", orders.get("ship_move", []))

        # 6. Resolve ship to ship combats
        self.resolve_ships_conflicts()

        # 7. Resolve ship to planet combats
        self.resolve_planets_conflicts()

        # 8. Ship construction
        self.run_player_action(
            "planet_build_ship", orders.get("planet_build_ship", [])
        )

        # 9. Population change
        # 10. Happypoints changes
        # 11. Taxes recollection
        # 12. Pythonium extraction
        self.produce_resources()

        self.galaxy.turn += 1

    def produce_resources(self):
        order = galaxy_orders.ProduceResources(self.galaxy)
        order.execute()

    def resolve_ships_conflicts(self):
        order = galaxy_orders.ResolveShipsConflicts(self.galaxy, cfg.tenacity)
        order.execute()

    def resolve_planets_conflicts(self):
        order = galaxy_orders.ResolvePlanetsConflicts(self.galaxy)
        order.execute()

    def run_player_action(self, name, orders):
        """
        :param name: name del player que ejecuta la params
        :type name: str
        :param orders: Una tupla que indica la params a ejecutar y los parámetros
            de la misma. ('name', *params)
        :type orders: tuple
        """
        func = getattr(self, f"action_{name}", None)
        for order in orders:
            kwargs = order.kwargs
            if isinstance(order, ShipOrderRequest):
                obj = self.galaxy.search_ship(order.id)
            elif isinstance(order, PlanetOrderRequest):
                obj = self.galaxy.search_planet(order.id)
            else:
                logger.warning(
                    "Unknown params",
                    extra={
                        "turn": self.galaxy.turn,
                        "player": order.player,
                        "kwargs": kwargs,
                    },
                )
                continue

            if not obj:
                logger.warning(
                    "Object not found",
                    extra={
                        "turn": self.galaxy.turn,
                        "player": order.name,
                        "kwargs": kwargs,
                        "name": name,
                    },
                )
                continue

            logger.debug(
                "Running action for player",
                extra={
                    "turn": self.galaxy.turn,
                    "player": obj.player,
                    "action": name,
                    "obj": type(obj),
                    "kwargs": kwargs,
                },
            )

            try:
                func(obj, **kwargs)
            except Exception as e:
                logger.error(
                    "Unexpected error running player params",
                    extra={
                        "turn": self.galaxy.turn,
                        "player": obj.player,
                        "action": name,
                        "obj": type(obj),
                        "kwargs": kwargs,
                        "reason": e,
                    },
                )

    def action_ship_move(self, ship, target):
        order = ship_orders.ShipMoveOrder(ship, target)
        order.execute(self.galaxy)

    def action_ship_transfer(self, ship, transfer):
        order = ship_orders.ShipTransferOrder(ship, transfer)
        order.execute(self.galaxy)

    def action_planet_build_mines(self, planet, new_mines):
        order = planet_orders.PlanetBuildMinesOrder(planet, new_mines)
        order.execute(self.galaxy)

    def action_planet_build_ship(self, planet, ship_type):

        ships_count = len(list(self.galaxy.get_player_ships(planet.player)))
        if ships_count >= self.game_mode.max_ships:
            logger.warning(
                "Ships limit reached",
                extra={
                    "turn": self.galaxy.turn,
                    "player": planet.player,
                    "ships_count": ships_count,
                },
            )
            return
        order = planet_orders.PlanetBuildShipOrder(planet, ship_type)
        order.execute(self.galaxy)

    def action_planet_set_taxes(self, planet, taxes):
        order = planet_orders.PlanetSetTaxesOrder(planet, taxes)
        order.execute(self.galaxy)
