from abc import ABC

import attr

from ..galaxy import Galaxy
from ..planet import Planet
from ..ship import Ship


@attr.s()
class ShipRule(ABC):

    name: str = attr.ib(init=False)
    ship: Ship = attr.ib()

    def execute(self, galaxy) -> None:
        raise NotImplementedError


@attr.s()
class PlanetRule(ABC):

    name: str = attr.ib(init=False)
    planet: Planet = attr.ib()

    def execute(self, galaxy) -> None:
        raise NotImplementedError


@attr.s()
class GalaxyRule(ABC):

    name: str = attr.ib(init=False)
    galaxy: Galaxy = attr.ib()

    def execute(self) -> None:
        raise NotImplementedError
