from abc import ABC

import attr

from ..galaxy import Galaxy
from ..planet import Planet
from ..ship import Ship


@attr.s()
class ShipOrder(ABC):

    name: str = attr.ib(init=False)
    ship: Ship = attr.ib()

    def execute(self, galaxy) -> None:
        raise NotImplementedError


@attr.s()
class PlanetOrder(ABC):

    name: str = attr.ib(init=False)
    planet: Planet = attr.ib()

    def execute(self, galaxy) -> None:
        raise NotImplementedError


@attr.s()
class GalaxyOrder(ABC):

    name: str = attr.ib(init=False)
    galaxy: Galaxy = attr.ib()

    def execute(self) -> None:
        raise NotImplementedError
