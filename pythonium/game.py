import logging
from .rules.executor import OrdersExecutor

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
        self._execute_orders = OrdersExecutor(galaxy=self.galaxy, rules=self.game_mode.rules)
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
            self.galaxy.explosions = []
            self._execute_orders(orders)
            self.galaxy.turn += 1

    def end_game(self):
        logger.info(
            "Game ended",
            extra={
                "turn": self.galaxy.turn,
                "winner": self.game_mode.winner,
            },
        )
        self.output_handler.finish(self.galaxy, self.game_mode.winner)
