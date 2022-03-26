import logging

import attr

from ..ship import Ship
from ..ship_type import ShipType
from .core import PlanetRule

logger = logging.getLogger("game")


@attr.s()
class PlanetBuildMinesRule(PlanetRule):

    name = "build_mines"
    new_mines: int = attr.ib()

    def execute(self, galaxy):
        new_mines = int(min(self.new_mines, self.planet.can_build_mines()))

        if not new_mines:
            logger.warning(
                "No mines to build",
                extra={
                    "turn": galaxy.turn,
                    "planet": self.planet.id,
                    "pythonium": self.planet.pythonium,
                    "megacredits": self.planet.megacredits,
                    "mines": self.planet.mines,
                    "max_mines": self.planet.max_mines,
                    "new_mines": self.new_mines,
                },
            )
            return

        self.planet.mines += new_mines
        self.planet.megacredits -= (
            new_mines * self.planet.mine_cost.megacredits
        )
        self.planet.pythonium -= new_mines * self.planet.mine_cost.pythonium

        logger.info(
            "New mines",
            extra={
                "turn": galaxy.turn,
                "player": self.planet.player,
                "planet": self.planet.id,
                "new_mines": new_mines,
            },
        )


@attr.s()
class PlanetBuildShipRule(PlanetRule):

    name = "build_ship"
    ship_type: ShipType = attr.ib()

    def execute(self, galaxy):
        if not self.planet.can_build_ship(self.ship_type):
            logger.warning(
                "Missing resources",
                extra={
                    "turn": galaxy.turn,
                    "planet": self.planet.id,
                    "ship_type": self.ship_type.name,
                    "megacredits": self.planet.megacredits,
                    "pythonium": self.planet.pythonium,
                },
            )
            return

        ship = Ship(
            player=self.planet.player,
            type=self.ship_type,
            position=self.planet.position,
            max_cargo=self.ship_type.max_cargo,
            max_mc=self.ship_type.max_mc,
            attack=self.ship_type.attack,
            speed=self.ship_type.speed,
        )

        self.planet.megacredits -= self.ship_type.cost.megacredits
        self.planet.pythonium -= self.ship_type.cost.pythonium

        galaxy.add_ship(ship)

        logger.info(
            "New ship built",
            extra={
                "turn": galaxy.turn,
                "player": self.planet.player,
                "planet": self.planet.id,
                "ship_type": self.ship_type.name,
            },
        )


@attr.s()
class PlanetSetTaxesRule(PlanetRule):

    name = "set_taxes"
    taxes: int = attr.ib()

    def execute(self, galaxy):
        if self.planet.taxes == self.taxes:
            return

        self.planet.taxes = min(max(0, self.taxes), 100)
        logger.info(
            "Taxes updated",
            extra={
                "turn": galaxy.turn,
                "player": self.planet.player,
                "planet": self.planet.id,
                "taxes": self.taxes,
            },
        )
