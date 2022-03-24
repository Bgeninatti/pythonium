import logging
import sys

from collections import defaultdict
from itertools import groupby
from . import cfg
from .explosion import Explosion
from .orders import galaxy as galaxy_orders
from .orders import planet as planet_orders
from .orders import ship as ship_orders

logger = logging.getLogger("game")


class Game:
    def __init__(
        self,
        name,
        players,
        gmode,
        *,
        raise_exceptions=False,
        stream_state=False
    ):
        """
        :param name: Name for the galaxy. Also used as game identifier.
        :type name: str
        :param players: Players for the game. Supports one or two players.
        :type players: list of instances of classes that extends
            from :class:`AbstractPlayer`
        :param gmode: Class that define some game rules
        :type gmode: :class:GameMode
        :param raise_exceptions: If ``True`` stop the game if an exception is raised when
            computing player actions. Useful for debuging players.
        :type raise_exceptions: bool
        :param stream_state: Default ``False``. If ``True`` each step in the 
            simulation will be serialized & printed to standard output.
        :type stream_state: bool
        """
        if len(players) != len({p.name for p in players}):
            raise ValueError("Player names must be unique")

        sys.stdout.write("** Pythonium **\n")
        self.gmode = gmode
        self.players = players
        self.raise_exceptions = raise_exceptions
        self._stream_state = stream_state
        logger.info(
            "Initializing galaxy",
            extra={"players": len(self.players), "galaxy_name": name},
        )
        self.galaxy = self.gmode.build_galaxy(name, self.players)
        logger.info("Galaxy initialized")
        sys.stdout.write(f"Running battle in galaxy #{name}\n")

    def extract_player_orders(self, player, galaxy, context):
        player_galaxy = player.next_turn(galaxy, context)

        # The function must return the mutated galaxy

        if id(galaxy) != id(player_galaxy):
            raise ValueError(
                "The `run_player` method must return a mutated galaxy"
            )

        planets_orders = [
            p.get_orders()
            for p in player_galaxy.planets.values()
            if p.player == player.name
        ]
        ships_orders = [
            s.get_orders()
            for s in player_galaxy.ships
            if s.player == player.name
        ]

        orders = [
            o for orders in ships_orders + planets_orders for o in orders
        ]
        logger.info(
            "Player orders computed",
            extra={
                "turn": self.galaxy.turn,
                "player": player.name,
                "orders": len(orders),
            },
        )

        grouped_actions = groupby(orders, lambda o: o[0])
        return grouped_actions

    def play(self):
        while True:

            sys.stdout.write(f"\rPlaying game{'.' * int(self.galaxy.turn/4)}")
            sys.stdout.flush()

            logger.info("Turn started", extra={"turn": self.galaxy.turn})
            orders = defaultdict(lambda: [])
            context = self.gmode.get_context(
                self.galaxy, self.players, self.galaxy.turn
            )

            # Should I record the state?  Litox dejó acá...
            if self._stream_state:
                logger.info("*** Acá el estado serializado...")

            # log current score
            for player_score in context["score"]:
                logger.info("Current score", extra=player_score)

            for player in self.players:
                # Filtra cosas que ve el player según las reglas del juego
                galaxy = self.gmode.galaxy_for_player(self.galaxy, player)
                try:
                    logger.info(
                        "Computing orders for player",
                        extra={
                            "turn": self.galaxy.turn,
                            "player": player.name,
                        },
                    )

                    player_orders = self.extract_player_orders(
                        player, galaxy, context
                    )
                    for name, player_orders in player_orders:
                        for order in player_orders:
                            orders[name].append((player, order[1:]))

                except Exception as e:
                    logger.error(
                        "Player lost turn",
                        extra={
                            "turn": self.galaxy.turn,
                            "player": player.name,
                            "reason": str(e),
                        },
                    )
                    logger.info(
                        "Player orders computed",
                        extra={
                            "turn": self.galaxy.turn,
                            "player": player.name,
                            "orders": 0,
                        },
                    )
                    if self.raise_exceptions:
                        raise e
                    continue

            if self.gmode.has_ended(self.galaxy, self.galaxy.turn):
                if self.gmode.winner:
                    logger.info(
                        "Winner!",
                        extra={
                            "turn": self.galaxy.turn,
                            "winner": self.gmode.winner,
                        },
                    )
                    message = f"Player {self.gmode.winner} wins\n"
                else:
                    logger.info("Nobody won", extra={"turn": self.galaxy.turn})
                    message = "Nobody won\n"

                sys.stdout.write("\n")
                sys.stdout.write(message)

                break

            # Reset explosions
            self.galaxy.explosions = []

            # Sort orders by object id
            for o in orders.values():
                o.sort(key=lambda x: x[1][0])

            self.run_turn(orders)

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
        for player, params in orders:
            if name.startswith("ship"):
                nid = params[0]
                args = params[1:]

                obj = self.galaxy.search_ship(nid)
            elif name.startswith("planet"):
                pid = params[0]
                args = params[1:]

                obj = self.galaxy.search_planet(pid)
            else:
                logger.warning(
                    "Unknown params",
                    extra={
                        "turn": self.galaxy.turn,
                        "player": player.name,
                        "params": params,
                    },
                )
                continue

            if not obj:
                logger.warning(
                    "Object not found",
                    extra={
                        "turn": self.galaxy.turn,
                        "player": player.name,
                        "params": params,
                        "name": name,
                    },
                )
                continue

            if obj.player != player.name:
                logger.warning(
                    "This is not yours",
                    extra={
                        "turn": self.galaxy.turn,
                        "player": player.name,
                        "owner": obj.player,
                        "obj": type(obj),
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
                    "args": args,
                },
            )

            try:
                func(obj, *args)
            except Exception as e:
                logger.error(
                    "Unexpected error running player params",
                    extra={
                        "turn": self.galaxy.turn,
                        "player": obj.player,
                        "action": name,
                        "obj": type(obj),
                        "args": args,
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
        if ships_count >= self.gmode.max_ships:
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
