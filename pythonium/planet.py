
from .ship import Ship
from . import cfg


class Planet:
    """
    A planet that belong to a :class:`Galaxy`

    Represent a planet that can be colonized.

    The `temperature` of the planet will determine how happy the `clans` can be
    (temperature define the `max_happypoints` for the planet).
    Each planet has some amount of `pythonium` in the surface that can be used by the
    colonizer race and some `underground_pythonium` (with a certain `concentration`) that
    needs to be extracted with `mines` to be used.
    """


    def __init__(self,
                 pid,
                 position: tuple,
                 temperature: int,
                 underground_pythonium: int,
                 concentration: float,
                 pythonium: int,
                 player=None):
        """
        :param pid: Planet unique ID
        :type pid: *int*
        :param position: Position of the planet in the galaxy.
        :type position: tuple of `(x, y)` where `x` and `y` are both *int*.
        :param temperature: Temperature of the planet. Max temperature
         is 100 and min temperature is 0.
        :type temperature: *int*
        :param underground_pythonium: Amount of pythonium that can be extracted with
         mines.
        :type underground_pythonium: positive *int*
        """

        # Initial conditions
        self.pid = pid
        self.position = position
        self.temperature = max(min(temperature, 100), 0)
        self.underground_pythonium = underground_pythonium
        self.concentration = max(min(temperature, 1.0), 0.0)
        self.pythonium = pythonium

        # State in turn
        self.player = player
        self.megacredits = 0

        # `max_happypoints` will decay as long as `temperature` differ from
        # `cfg.optimal_temperature`. `max_happypoints` can't be less than
        # `cfg.happypoints_tolerance`
        self.max_happypoints = max(100 - abs(self.temperature - cfg.optimal_temperature),
                                   cfg.optimal_temperature)
        self.happypoints = self.max_happypoints
        self.clans = 0
        self.mines = 0

        # User controls
        self.new_mines = 0
        self.new_ship = None
        self.taxes = 0.0

        # Restrictions
        self._dpythonium = 0.0
        self._dmegacredits = 0.0
        self._dhappypoints = 0.0
        self._dclans = 0

    def __repr__(self):
        return f"Planet #{self.pid} <player={self.player}>"

    @property
    def max_mines(self):
        return min(self.clans, cfg.planet_max_mines)

    @property
    def rioting_index(self):
        """
        If the `happypoints` are less than `cfg.happypoints_tolerance` this
        property indicates how much this un unhappiness affect to planet's economy.
        """
        return min(self.happypoints / cfg.happypoints_tolerance, 1)

    @property
    def dpythonium(self):
        """
        Change in pythonium for the next turn considering
        mines extraction, mines construction and `rioting_index`.
        """
        mines_extraction = self.mines * self.concentration * self.rioting_index

        return max(int(mines_extraction), -self.pythonium)

    @property
    def dmegacredits(self):
        """
        Change in megacredits for the next turn considering
        taxes, ship construction, mine construction and `rioting_index`.
        """
        taxes = cfg.taxes_collection_factor * self.clans * self.taxes / 100 \
            * self.rioting_index

        return min(cfg.max_mc_in_turn, max(int(taxes), -self.megacredits))

    @property
    def dhappypoints(self):
        """
        Absolute change of happypoints in the next turn
        """
        return max(
            min(cfg.tolerable_taxes - self.taxes,
                self.max_happypoints - self.happypoints),
            -self.happypoints)

    @property
    def dclans(self):
        """
        Aditional clans in the next turn. Is the absolute change
        in the population.
        """
        growth_rate = cfg.max_population_rate * self.rioting_index
        return min(cfg.max_clans_in_planet - self.clans,
                   max(int(self.clans * growth_rate), -self.clans))

    def get_orders(self):
        """
        Compute orders based on player control attributes: ``new_mines``, ``new_ship``
        and ``taxes``
        """
        orders = [('planet_set_taxes', self.pid, self.taxes)]

        if self.new_ship is not None:
            orders.append(('planet_build_ship', self.pid, self.new_ship))

        if self.new_mines > 0:
            orders.append(('planet_build_mines', self.pid, self.new_mines))

        return orders

    def can_build_mines(self):
        return int(min(
            self.pythonium / cfg.mine_cost[1],
            self.megacredits / cfg.mine_cost[0],
            self.max_mines - self.mines))

    def can_build_ship(self, ship_type):
        ship_cost = Ship.COSTS[ship_type]
        return self.megacredits >= ship_cost[0] and self.pythonium >= ship_cost[1]
