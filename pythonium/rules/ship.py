import logging
from typing import Tuple

import attr

from ..vectors import Transfer
from .core import ShipRule

logger = logging.getLogger("game")


@attr.s()
class ShipMoveRule(ShipRule):

    name = "ship_move"
    target: Tuple[int, int] = attr.ib()

    def execute(self, galaxy):

        _from = self.ship.position
        distance_to_target = galaxy.compute_distance(
            self.ship.position, self.target
        )

        if distance_to_target <= self.ship.speed:
            to = self.target
            new_target = None
        else:

            direction = (
                (self.target[0] - self.ship.position[0]) / distance_to_target,
                (self.target[1] - self.ship.position[1]) / distance_to_target,
            )
            to = (
                int(self.ship.position[0] + direction[0] * self.ship.speed),
                int(self.ship.position[1] + direction[1] * self.ship.speed),
            )
            new_target = self.target

        self.ship.position = to
        self.ship.target = new_target
        logger.info(
            "Ship moved",
            extra={
                "turn": galaxy.turn,
                "player": self.ship.player,
                "ship": self.ship.id,
                "from": _from,
                "to": self.ship.position,
                "target": self.ship.target,
            },
        )


@attr.s()
class ShipTransferRule(ShipRule):

    name = "ship_transfer"
    transfer: Transfer = attr.ib()

    def execute(self, galaxy):
        planet = galaxy.planets.get(self.ship.position)

        logger.info(
            "Attempt to transfer",
            extra={
                "ship": self.ship.id,
                "clans": self.transfer.clans,
                "pythonium": self.transfer.pythonium,
                "megacredits": self.transfer.megacredits,
            },
        )

        if not planet:
            logger.warning(
                "Can not transfer in deep space",
                extra={"turn": galaxy.turn, "ship": self.ship.id},
            )
            return

        if planet.player is not None and planet.player != self.ship.player:
            logger.warning(
                "Can not transfer to an enemy planet",
                extra={
                    "turn": galaxy.turn,
                    "ship": self.ship.id,
                    "planet": planet.id,
                },
            )
            return

        # Check if transfers + existences are grather than capacity on clans and pythonium
        available_cargo = self.ship.max_cargo - (
            self.ship.pythonium + self.ship.clans
        )

        # Adjust transfers to real availability in planet and ship
        self.transfer.clans = (
            min(self.transfer.clans, planet.clans, available_cargo)
            if self.transfer.clans > 0
            else max(self.transfer.clans, -self.ship.clans)
        )
        self.transfer.pythonium = (
            min(
                self.transfer.pythonium,
                planet.pythonium,
                available_cargo - self.transfer.clans,
            )
            if self.transfer.pythonium > 0
            else max(self.transfer.pythonium, -self.ship.pythonium)
        )
        self.transfer.megacredits = (
            min(
                self.transfer.megacredits,
                planet.megacredits,
                self.ship.max_mc - self.ship.megacredits,
            )
            if self.transfer.megacredits > 0
            else max(self.transfer.megacredits, -self.ship.megacredits)
        )

        # Do transfers
        self.ship.clans += self.transfer.clans
        self.ship.pythonium += self.transfer.pythonium
        self.ship.megacredits += self.transfer.megacredits

        logger.info(
            "Ship transfer to planet",
            extra={
                "turn": galaxy.turn,
                "player": self.ship.player,
                "ship": self.ship.id,
                "clans": self.transfer.clans,
                "pythonium": self.transfer.pythonium,
                "megacredits": self.transfer.megacredits,
            },
        )

        planet.clans -= self.transfer.clans
        planet.pythonium -= self.transfer.pythonium
        planet.megacredits -= self.transfer.megacredits

        if not planet.clans:
            # If nobody stays in the planet the player doesn't own it anymore
            planet.player = None
            logger.info(
                "Planet abandoned",
                extra={
                    "turn": galaxy.turn,
                    "player": self.ship.player,
                    "planet": planet.id,
                },
            )
        elif planet.player is None and planet.clans > 0:
            # If nobody owns the planet and the ship download clans the player
            # conquer the planet
            planet.player = self.ship.player
            logger.info(
                "Planet conquered",
                extra={
                    "turn": galaxy.turn,
                    "player": self.ship.player,
                    "planet": planet.id,
                },
            )

        return
