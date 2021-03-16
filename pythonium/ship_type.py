import attr

from .vectors import Transfer


@attr.s
class ShipType:
    """
    Defines the attributes of a ship that the player can built.
    """

    name: str = attr.ib()
    """
    A descriptive name for the ship type. i.e: 'war', 'carrier'
    """

    cost: Transfer = attr.ib()
    """
    :class:`Transfer` instance that represents the cost of a ship of this type.
    """

    max_cargo: int = attr.ib()
    """
    Max cargo of clans and pythonium (together) for this ship.

    In other words, you should always expect this:

    >>> ship.megacredits + ship.clans <= ship.max_cargo
    True

    Megacredits do not take up physical space in the ship so are not considered
    for ``max_cargo`` limit.
    """

    max_mc: int = attr.ib()
    """
    Max amount of megacredits that can be loaded to the ship.

    In other words, you should always expect this:

    >>> ship.megacredits <= ship.max_mc
    True
    """

    attack: int = attr.ib()
    """
    Attack of the ship. It will be used to resolve conflicts.
    """

    def __repr__(self):
        return self.name
