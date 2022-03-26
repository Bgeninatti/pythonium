import logging
from itertools import groupby

import attr
import numpy as np

from .. import cfg
from ..explosion import Explosion
from .core import GalaxyRule

logger = logging.getLogger("game")


@attr.s()
class ProduceResources(GalaxyRule):

    name = "produce_resources"

    def execute(self) -> None:
        for planet in self.galaxy.get_ocuped_planets():
            self._produce_resources(planet)

    def _produce_resources(self, planet):
        dhappypoints = planet.dhappypoints
        if dhappypoints:
            planet.happypoints += dhappypoints
            logger.info(
                "Happypoints change",
                extra={
                    "turn": self.galaxy.turn,
                    "player": planet.player,
                    "planet": planet.id,
                    "dhappypoints": dhappypoints,
                    "happypoints": planet.happypoints,
                },
            )

        dmegacredits = planet.dmegacredits
        if dmegacredits:
            planet.megacredits += dmegacredits
            logger.info(
                "Megacredits change",
                extra={
                    "turn": self.galaxy.turn,
                    "player": planet.player,
                    "planet": planet.id,
                    "dmegacredits": dmegacredits,
                    "megacredits": planet.megacredits,
                },
            )

        dpythonium = planet.dpythonium
        if dpythonium:
            planet.pythonium += dpythonium
            logger.info(
                "Pythonium change",
                extra={
                    "turn": self.galaxy.turn,
                    "player": planet.player,
                    "planet": planet.id,
                    "dpythonium": dpythonium,
                    "pythonium": planet.pythonium,
                },
            )

        dclans = planet.dclans
        if dclans:
            planet.clans += dclans
            logger.info(
                "Population change",
                extra={
                    "turn": self.galaxy.turn,
                    "player": planet.player,
                    "planet": planet.id,
                    "dclans": dclans,
                    "clans": planet.clans,
                },
            )


@attr.s()
class ResolveShipsConflicts(GalaxyRule):

    name = "resolve_ships_conflicts"
    tenacity: float = attr.ib(default=cfg.tenacity)

    def execute(self) -> None:
        ships_in_conflict = self.galaxy.get_ships_conflicts()
        for ships in ships_in_conflict:
            self._resolve_ships_conflicts(ships)
        self.galaxy.remove_destroyed_ships()

    def _compute_winner(self, ships, total_attack):
        """
        Due to the randomness of the fighting process, this method is not tested
        """
        groups = groupby(ships, lambda s: s.player)

        max_score = 0
        winner = None
        for player, player_ships in groups:
            player_attack = sum((s.attack for s in player_ships))
            attack_fraction = player_attack / total_attack

            # Compute score probability distribution
            shape = 100 * attack_fraction
            score = np.random.normal(shape, self.tenacity)

            logger.info(
                "Score in conflict",
                extra={
                    "turn": self.galaxy.turn,
                    "player": player,
                    "player_attack": player_attack,
                    "attack_fraction": attack_fraction,
                    "score": score,
                },
            )
            if score > max_score:
                winner = player
                max_score = score

        logger.info(
            "Conflict resolved",
            extra={
                "turn": self.galaxy.turn,
                "winner": winner,
                "max_score": max_score,
                "total_attack": total_attack,
                "total_ships": len(ships),
            },
        )
        return winner

    def _resolve_ships_conflicts(self, ships):
        total_attack = sum(s.attack for s in ships)
        winner = self._compute_winner(ships, total_attack)
        # Destroy defeated ships
        for ship in ships:
            if ship.player == winner:
                continue
            logger.info(
                "Explosion",
                extra={
                    "turn": self.galaxy.turn,
                    "player": ship.player,
                    "ship": ship.id,
                    "ship_type": ship.type.name,
                    "position": ship.position,
                },
            )
            self.galaxy.explosions.append(
                Explosion(
                    ship=ship,
                    ships_involved=len(ships),
                    total_attack=total_attack,
                )
            )


@attr.s()
class ResolvePlanetsConflicts(GalaxyRule):

    name = "resolve_planets_conflicts"

    def execute(self) -> None:
        planets_in_conflict = self.galaxy.get_planets_conflicts()
        for planet, ships in planets_in_conflict:
            if not sum((s.attack for s in ships)):
                continue
            self._resolve_planets_conflicts(planet, ships)

    def _resolve_planets_conflicts(self, planet, ships):
        enemies = {s.player for s in ships if s.player != planet.player}

        if not enemies:
            raise ValueError(
                "Ok, I don't know what's going on. This is not a conflict."
            )

        if len(enemies) != 1:
            raise ValueError(
                "Run :meth:`resolve_ships_to_ship_conflict` first"
            )

        winner = enemies.pop()

        # If is not of his own, the winner conquer the planet.
        if planet.player != winner:
            logger.info(
                "Planet conquered by force",
                extra={
                    "turn": self.galaxy.turn,
                    "player": winner,
                    "planet": planet.id,
                    "clans": planet.clans,
                },
            )
            planet.player = winner
            planet.clans = 1
            planet.mines = 0
            planet.taxes = 0
