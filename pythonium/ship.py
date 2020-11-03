
import attr
from .vectors import TransferVector
from . import validators

@attr.s
class Ship:
    """
    A ship that belong to a race.

    Represent a ship that will be used to acomplish the race missions. A ship has
    certain attributes that define what is its purpose or best use.

    The specs and cost of the available ships are stored in the ``Ship.TYPES`` and
    ``Ship.COSTS`` class attributes.

    As default, there are two types of ship `Ship.WAR` and `Ship.CARRIER` with the
    following specs:

    ============================================================
    Type     Max Cargo  Max Mc  Attack  Pythonium Cost  Mc Cost
    ============================================================
    War      100        10000   500     1000            500
    Carrier  1200       10000   0       600             300
    ============================================================
    """

    # Initial conditions
    # The id is set when the ship is added to the galaxy
    nid: int = attr.ib(init=False, default=None)
    player: str = attr.ib()
    type: int = attr.ib(converter=str)
    position: tuple = attr.ib(converter=tuple,
                              validator=[validators.is_valid_position])
    max_cargo: int = attr.ib(converter=int)
    max_mc: int = attr.ib(converter=int)
    attack: int = attr.ib(converter=int)

    # State in turn
    megacredits: int = attr.ib(converter=int, default=0, init=False)
    pythonium: int = attr.ib(converter=int, default=0, init=False)
    clans: int = attr.ib(converter=int, default=0, init=False)

    # User controls
    target: tuple = attr.ib(default=None,
                            init=False,
                            validator=[validators.is_valid_position])
    transfer: TransferVector = attr.ib(default=TransferVector(), init=False)

    def __repr__(self):
        return f"Ship #{self.nid} <player={self.player}>"

    def get_orders(self):
        """
        Compute orders based on player control attributes: ``transfer`` and ``target``
        """
        orders = []
        if any(self.transfer):
            orders.append(('ship_transfer', self.nid, self.transfer))

        if self.target is not None:
            orders.append(('ship_move', self.nid, self.target))

        return orders
