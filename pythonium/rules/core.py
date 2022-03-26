from abc import ABC

import attr

from ..galaxy import Galaxy
from ..planet import Planet
from ..ship import Ship


@attr.s()
class Rule(ABC):
    name: str = attr.ib(init=False)

    def execute(self, galaxy) -> None:
        raise NotImplementedError


@attr.s()
class ShipRule(Rule, ABC):
    ship: Ship = attr.ib()


@attr.s()
class PlanetRule(Rule, ABC):
    planet: Planet = attr.ib()


@attr.s()
class GalaxyRule(Rule, ABC):
    galaxy: Galaxy = attr.ib()

    def execute(self) -> None:
        raise NotImplementedError
