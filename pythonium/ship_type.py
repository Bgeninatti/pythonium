import attr
from .vectors import CostVector

@attr.s
class ShipType:
    """
    Define the attributes of a ship that
    can be built by a player
    """

    name: str = attr.ib()
    cost: tuple = attr.ib()
    max_cargo: int = attr.ib()
    max_mc: int = attr.ib()
    attack: int = attr.ib()

    def __repr__(self):
        return self.name
