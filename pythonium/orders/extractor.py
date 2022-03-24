from collections import defaultdict
from itertools import groupby

import attr
import logging

from pythonium import GameMode

logger = logging.getLogger("game")


@attr.s(auto_attribs=True)
class OrdersExtractor:
    """
        :param game_mode: Class that define some game rules
        :type game_mode: :class:GameMode
        :param _raise_exceptions: If ``True`` stop the game if an exception is raised when
            computing player actions. Useful for debuging players.
        :type _raise_exceptions: bool
    """
    game_mode: GameMode = attr.ib()
    _raise_exceptions: bool = attr.ib(default=False)

    @staticmethod
    def _validate_galaxy(galaxy, player_galaxy):
        # The player `next_turn` method must return the mutated galaxy

        if id(galaxy) != id(player_galaxy):
            raise ValueError(
                "The `run_player` method must return a mutated galaxy"
            )

    def extract_player_orders(self, player, galaxy, context):
        player_galaxy = player.next_turn(galaxy, context)
        self._validate_galaxy(galaxy, player_galaxy)

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
                "turn": galaxy.turn,
                "player": player.name,
                "orders": len(orders),
            },
        )

        grouped_actions = groupby(orders, lambda o: o[0])
        return grouped_actions

    def __call__(self, galaxy, players, context, raise_exceptions=False):
        orders = defaultdict(lambda: [])
        for player in players:
            # Filtra cosas que ve el player según las reglas del juego
            galaxy = self.game_mode.galaxy_for_player(galaxy, player)
            try:
                logger.info(
                    "Computing orders for player",
                    extra={
                        "turn": galaxy.turn,
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
                        "turn": galaxy.turn,
                        "player": player.name,
                        "reason": str(e),
                    },
                )
                logger.info(
                    "Player orders computed",
                    extra={
                        "turn": galaxy.turn,
                        "player": player.name,
                        "orders": 0,
                    },
                )
                if self._raise_exceptions:
                    raise e
                continue

        # Sort orders by object id
        for o in orders.values():
            o.sort(key=lambda x: x[1][0])

        return orders
