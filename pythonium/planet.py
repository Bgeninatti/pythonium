import attr

from . import cfg, validators
from .core import Position, StellarThing
from .orders.request import PlanetOrderRequest
from .ship_type import ShipType
from .vectors import Transfer


@attr.s(auto_attribs=True, repr=False)
class Planet(StellarThing):
    """
    A planet that belongs to a :class:`Galaxy`

    Represent a planet that can be colonized.

    The ``temperature`` on the planet will determine how happy the ``clans`` can be
    (temperature defines the ``max_happypoints`` for the planet).

    Each planet has some amount of ``pythonium`` on the surface that can be used by the
    colonizer race, and some ``underground_pythonium`` (with a certain ``concentration``)
    that needs to be extracted with ``mines``.

    The higher the ``taxes`` are over ``cfg.tolerable_taxes``, the faster the
    ``happypoints`` decay.

    The lower the ``happypoints`` are over ``cfg.happypoints_tolerance``, the lower the
    planet production of ``clans``, ``pythonium``, and ``megacredits`` will be
    (in proportion of ``rioting_index``).
    """

    thing_type = "planet"

    temperature: int = attr.ib(
        validator=validators.number_between_zero_100, kw_only=True
    )
    """
    The temperature of the planet. It is always between zero and 100.
    """

    underground_pythonium: int = attr.ib(
        validator=[attr.validators.instance_of(int)], kw_only=True
    )
    """
    Amount of pythonium under the surface of the planet, that needs to be extracted with
    mines.
    """

    concentration: float = attr.ib(
        validator=[validators.is_valid_ratio], kw_only=True
    )
    """
    Indicates how much pythonium extract one mine. It is always between zero and 1.
    """

    pythonium: int = attr.ib(
        validator=[attr.validators.instance_of(int)], kw_only=True
    )
    """
    Pythonium in the surface of the planet. The available resource to build things.
    """

    mine_cost: Transfer = attr.ib(
        validator=[attr.validators.instance_of(Transfer)], kw_only=True
    )
    """
    Indicates the cost of building one mine.
    """

    # State in turn
    player: str = attr.ib(default=None, kw_only=True)
    """
    The owner of the planet or ``None`` if no one owns it.
    """

    megacredits: int = attr.ib(converter=int, default=0, kw_only=True)
    """
    Amount of megacredits on the planet
    """

    clans: int = attr.ib(converter=int, default=0, kw_only=True)
    """
    Amount of clans on the planet
    """

    mines: int = attr.ib(converter=int, default=0, kw_only=True)
    """
    Amount of mines on the planet
    """

    max_happypoints: int = attr.ib(converter=int, default=0, kw_only=True)
    """
    The maximum level of happypoints that the population of this planet can reach.

    It is based on the planet's temperature.

    Its maximum value (100) is reached when the planet's temperature is equal \
    to ``cfg.optimal_temperature``
    """

    happypoints: int = attr.ib(converter=int, default=0, kw_only=True)
    """
    The level of happyness on the planet.

    This has influence on ``rioting_index``
    """

    # User controls
    new_mines: int = attr.ib(
        validator=[attr.validators.instance_of(int)], default=0, kw_only=True
    )
    """
    **Attribute that can be modified by the player**

    New mines that the player order to build in the current turn. This value is set to
    zero when the player orders are executed.
    """

    new_ship: ShipType = attr.ib(
        default=None,
        validator=[attr.validators.instance_of((ShipType, type(None)))],
        kw_only=True,
    )
    """
    **Attribute that can be modified by the player**

    The new ship that the player order to build in the current turn.

    This value is set to ``None`` when the player orders are executed
    """

    taxes: int = attr.ib(
        converter=int,
        default=0,
        validator=[validators.is_valid_ratio],
        kw_only=True,
    )
    """
    **Attribute that can be modified by the player**

    Taxes set by the player. Must be between zero and 100.

    The level of taxes defines how much megacredits will be collected in the current turn.

    If the taxes are higher than ``cfg.tolerable_taxes`` the planet's happypoints will
    decay ``planet.taxes - cfg.tolerable_taxes`` per turn.

    See :attr:`dmegacredits`
    """
    taxes_collection_factor: int = attr.ib(
        default=cfg.taxes_collection_factor,
        validator=[validators.is_valid_ratio],
    )

    def __attrs_post_init__(self):
        # `max_happypoints` will decay as long as `temperature` differ from
        # `cfg.optimal_temperature`. `max_happypoints` can't be less than
        # `cfg.happypoints_tolerance`
        self.max_happypoints = max(
            100 - abs(self.temperature - cfg.optimal_temperature),
            cfg.optimal_temperature,
        )
        self.happypoints = self.max_happypoints

    def __str__(self):
        return f"Planet(id={self.id}, position={self.position}, player={self.player})"

    def __repr__(self):
        return self.__str__()

    @property
    def max_mines(self) -> int:
        """
        The maximum number of mines that can be build in the planet
        """
        return min(self.clans, cfg.planet_max_mines)

    @property
    def rioting_index(self) -> float:
        """
        If the ``happypoints`` are less than ``cfg.happypoints_tolerance`` this \
        property indicates how much this unhappiness will affect the planet's economy.

        i.e: if ``rioting_index`` is 0.5 pythonium production, and megacredits \
        recollection will be %50 less than its standard level.
        """
        return min(self.happypoints / cfg.happypoints_tolerance, 1)

    @property
    def dpythonium(self) -> int:
        """
        Absolute change in pythonium for the next turn considering:

        * ``mines``: Positive influence,
        * ``concentration``: Positive influence,
        * ``rioting_index``: Positive  influence.

        Do not consider ``new_mines`` and ``new_ship`` cost, or ship transfers.
        """
        mines_extraction = self.mines * self.concentration * self.rioting_index

        return max(int(mines_extraction), -self.pythonium)

    @property
    def dmegacredits(self) -> int:
        """
        Absolute change in megacredits for the next turn considering:

        * ``taxes``: Positive influence
        * ``rioting_index``: Negative influence,
        * ``clans``: Positive influence,
        * ``taxes_collection_factor``: Positive influence

        Do not consider ``new_mines`` and ``new_ship`` cost, or ship transfers.
        """
        taxes = (
            self.taxes_collection_factor
            * self.clans
            * self.taxes
            / 100
            * self.rioting_index
        )

        return int(taxes)

    @property
    def dhappypoints(self) -> int:
        """
        Absolute change on happypoints for the next turn
        """
        unbounded_dhappypoints = cfg.tolerable_taxes - self.taxes
        if unbounded_dhappypoints < 0:
            return max(unbounded_dhappypoints, -self.happypoints)
        else:
            return min(
                unbounded_dhappypoints, self.max_happypoints - self.happypoints
            )

    @property
    def dclans(self) -> int:
        """
        Aditional clans for the next turn. The absolute change
        in the population considering:

        * ``rioting_index``: Negative influence,
        * ``cfg.max_population_rate``: Positive influence,
        * ``cfg.max_clans_in_planet``: Positive influence,
        * ``clans``: Positive influence
        """
        growth_rate = cfg.max_population_rate * self.rioting_index
        return min(
            cfg.max_clans_in_planet - self.clans,
            max(int(self.clans * growth_rate), -self.clans),
        )

    def get_orders(self):
        """
        Compute orders based on player control attributes: ``new_mines``, \
        ``new_ship`` and ``taxes``
        """
        orders = [
            PlanetOrderRequest(
                name="planet_set_taxes",
                id=self.id,
                kwargs={'taxes': self.taxes}
            )
        ]

        if self.new_ship is not None:
            orders.append(
                PlanetOrderRequest(
                    name="planet_build_ship",
                    id=self.id,
                    kwargs={'new_ship': self.new_ship}
                )
            )

        if self.new_mines > 0:
            orders.append(
                PlanetOrderRequest(
                    name="planet_build_mines",
                    id=self.id,
                    kwargs={'new_mines': self.new_mines}
                )
            )

        return orders

    def can_build_mines(self) -> int:
        """
        Computes the number of mines that can be built on the planet based \
        on available resources and ``max_mines``
        """
        return int(
            min(
                self.pythonium / self.mine_cost.pythonium,
                self.megacredits / self.mine_cost.megacredits,
                self.max_mines - self.mines,
            )
        )

    def can_build_ship(self, ship_type: ShipType) -> bool:
        """
        Indicates whether ``ship_type`` can be built on this planet \
        with the available resources
        """
        return (
            self.megacredits >= ship_type.cost.megacredits
            and self.pythonium >= ship_type.cost.pythonium
        )

    def move(self, position: Position) -> None:
        return

    @classmethod
    def deserialize(cls, data):
        mine_cost_data = data.pop("mine_cost")
        mine_cost = Transfer(**mine_cost_data)
        return cls(**data, mine_cost=mine_cost)
