from typing import Tuple

import attr

from . import validators
from .ship_type import ShipType
from .vectors import Transfer


@attr.s
class Ship:
    """
    A ship that belongs to a race.

    It can be moved from one point to another, it can be used to move any resource, \
    and in some cases can be used to attack planets or ships.
    """

    # Initial conditions
    # The id is set when the ship is added to the galaxy
    nid: int = attr.ib(init=False, default=None)
    """
    Unique identifier for the ship. It is assigned by the galaxy.
    """

    player: str = attr.ib()
    """
    Name of the ship's owner.
    """

    type: int = attr.ib(
        validator=[attr.validators.instance_of((ShipType, type(None)))]
    )
    """
    Name of the :class:`ShipType`
    """

    position: Tuple[int, int] = attr.ib(
        converter=tuple, validator=[validators.is_valid_position]
    )
    """
    Position of the ship in (x, y) coordinates
    """

    max_cargo: int = attr.ib(converter=int)
    """
    Indicates how much pythonium and clans (together) can carry the ship.
    See :attr:`ShipType.max_cargo`
    """

    max_mc: int = attr.ib(converter=int)
    """
    Indicates how much megacredits can carry the ship.
    See :attr:`ShipType.max_mc`
    """

    attack: int = attr.ib(converter=int)
    """
    Indicates how much attack the ship has.
    See :attr:`ShipType.attack`
    """

    speed: int = attr.ib(converter=int)
    """
    Ship's speed in ly per turn
    """

    # State in turn
    megacredits: int = attr.ib(converter=int, default=0, init=False)
    """
    Amount of megacredits on the ship
    """

    pythonium: int = attr.ib(converter=int, default=0, init=False)
    """
    Amount of pythonium on the ship
    """

    clans: int = attr.ib(converter=int, default=0, init=False)
    """
    Amount of clans on the ship
    """

    # User controls
    target: Tuple[int, int] = attr.ib(
        default=None, init=False, validator=[validators.is_valid_position]
    )
    """
    **Attribute that can be modified by the player**

    Indicates where the ship is going, or ``None`` if it is stoped.
    """

    transfer: Transfer = attr.ib(default=Transfer(), init=False)
    """
    **Attribute that can be modified by the player**

    Indicates what resources will be transferred by the ship in the current turn.

    If no transfer is made this is an empty transfer.

    See :class:`Transfer` bool conversion.
    """

    def __repr__(self):
        return f"Ship #{self.nid} <player={self.player}>"

    def get_orders(self):
        """
        Compute orders based on player control attributes: ``transfer`` and ``target``
        """
        orders = []
        if self.transfer:
            orders.append(("ship_transfer", self.nid, self.transfer))

        if self.target is not None:
            orders.append(("ship_move", self.nid, self.target))

        return orders
