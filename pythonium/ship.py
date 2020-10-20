from . import cfg


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

    CARRIER, WAR = range(2)

    # (max_cargo, max_mc, attack)
    TYPES = {
        CARRIER: (1200, 10000, 0),
        WAR: (100, 10000, 100),
    }

    # Cost format (mc, p)
    COSTS = {
        CARRIER: (600, 300),
        WAR: (1000, 500)
    }
    def __init__(self,
                 player: int,
                 ship_type: int,
                 position: tuple,
                 max_cargo: int,
                 max_mc: int,
                 attack: int):
        """
        :param player: Race ID of the ship owner
        :type player: int
        :param ship_type: Ship type
        :type ship_type: int
        :param position: Ship initial position. Is always the position of the planet
          where the ship has been built.
        :type position: tuple of `(x, y)` where `x` and `y` are both *int*.
        :param max_cargo: Define how much `pythonium` and `clans` can be carried into
          the ship. The cargo space will be shared by this two resources.
        :type max_cargo: int
        :param max_mc: Define the max amount of `megacredits` can be carried into the
          ship.
        :type max_mc: int
        :param attack: Define the ship attack capabilites. The more attack the ship has
          the higher are the probabilities of win a conflict.
        """
        # Initial conditions
        self.nid = None # The id is set when the ship is added to the galaxy
        self.max_cargo = max_cargo
        self.max_mc = max_mc
        self.attack = attack
        self.type = ship_type
        self.player = player

        # State in turn
        self.position = position
        self.megacredits = 0
        self.pythonium = 0
        self.clans = 0

        # User controls
        self.target = None
        self.transfer = (0, 0, 0) # transfer format (clans, mc, pythonium)

    def __repr__(self):
        return f"Ship #{self.nid} <player={self.player}>"

    @classmethod
    def get_type(cls, ship_type):
        """
        Return the specs of a given ship type or ``None`` if the type don't exist.
        """
        return cls.TYPES.get(ship_type)

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
