import pytest

from pythonium import Transfer, cfg
from pythonium.orders.request import PlanetOrderRequest

from .factories import PlanetFactory, ShipTypeFactory


def is_monotonic_increasing(sample):
    return all(sample[i] <= sample[i + 1] for i in range(len(sample) - 1))


def is_monotonic_decreasing(sample):
    return all(sample[i] >= sample[i + 1] for i in range(len(sample) - 1))


@pytest.fixture
def planet():
    return PlanetFactory()


@pytest.fixture
def ship_type():
    return ShipTypeFactory()


@pytest.fixture
def colonized_planet(faker):
    return PlanetFactory(clans=faker.pyint(), megacredits=faker.pyint())


@pytest.fixture
def optimal_temperature_planet():
    return PlanetFactory(temperature=cfg.optimal_temperature)


@pytest.fixture
def temperatured_planet(temperature):
    return PlanetFactory(temperature=temperature)


@pytest.fixture
def planet_with_clans(clans):
    return PlanetFactory(clans=clans)


@pytest.fixture
def planet_with_hp(happypoints):
    planet = PlanetFactory()
    planet.happypoints = happypoints
    return planet


@pytest.fixture
def planets_group_with_mines(mines_range):
    planets = []
    for mines in mines_range:
        planet = PlanetFactory(concentration=1.0, mines=mines)
        planets.append(planet)
    return planets


@pytest.fixture
def planets_group_with_concentration(concentrations_range):
    planets = []
    for concentration in concentrations_range:
        planet = PlanetFactory(concentration=concentration / 100, mines=100)
        planets.append(planet)
    return planets


@pytest.fixture
def planets_group_with_happypoints(happypoints_range):
    planets = []
    for happypoints in happypoints_range:
        planet = PlanetFactory(mines=100, concentration=1.0)
        planet.happypoints = happypoints
        planets.append(planet)
    return planets


@pytest.fixture
def planets_group_with_collection_factor(taxes_collection_factor):
    planets = []
    for collection_factor in taxes_collection_factor:
        planet = PlanetFactory(clans=100, taxes=cfg.tolerable_taxes)
        planet.taxes_collection_factor = collection_factor
        planets.append(planet)
    return planets


@pytest.fixture
def planets_group_with_clans(clans_range):
    planets = []
    for clans in clans_range:
        planet = PlanetFactory(clans=clans)
        planets.append(planet)
    return planets


@pytest.fixture
def planets_group_with_taxes(taxes_range):
    planets = []
    for taxes in taxes_range:
        planet = PlanetFactory(
            temperature=cfg.optimal_temperature, taxes=taxes
        )
        planets.append(planet)
    return planets


@pytest.fixture
def planets_group_with_temperature(temperatures_range):
    planets = []
    for temperature in temperatures_range:
        planet = PlanetFactory(temperature=temperature)
        planets.append(planet)
    return planets


class TestPlanet:
    @pytest.fixture
    def expected_repr(self, planet):
        return f"Planet(id={planet.id}, position={planet.position}, player={planet.player})"

    def test_repr(self, planet, expected_repr):
        assert str(planet) == expected_repr
        assert str(planet) == planet.__repr__()


class TestPlanetHappyPoints:
    def test_max_hp_in_optimal_temperature(self, optimal_temperature_planet):
        assert optimal_temperature_planet.max_happypoints == 100

    @pytest.mark.parametrize("temperature", range(0, cfg.optimal_temperature))
    def test_max_hp_below_optimal_temperature(self, temperatured_planet):
        assert temperatured_planet.max_happypoints < 100

    @pytest.mark.parametrize(
        "temperature", range(cfg.optimal_temperature + 1, 101)
    )
    def test_max_hp_above_optimal_temperature(self, temperatured_planet):
        assert temperatured_planet.max_happypoints < 100

    @pytest.mark.parametrize(
        "temperatures_range",
        (
            range(100, cfg.optimal_temperature, -1),
            range(0, cfg.optimal_temperature),
        ),
    )
    def test_max_hp_monotonicity_with_temperature(
        self, planets_group_with_temperature
    ):
        max_happypoints_range = [
            planet.max_happypoints for planet in planets_group_with_temperature
        ]
        assert is_monotonic_increasing(max_happypoints_range)

    @pytest.mark.parametrize("temperature", range(0, 101))
    def test_init_hp_are_max(self, temperatured_planet):
        assert (
            temperatured_planet.max_happypoints
            == temperatured_planet.happypoints
        )

    @pytest.mark.parametrize(
        "taxes_range",
        (
            range(0, cfg.tolerable_taxes),
            range(100, cfg.tolerable_taxes, -1),
        ),
    )
    def test_dhappypoints_monotonicity_with_taxes(
        self, planets_group_with_taxes
    ):
        dhappypoints_range = [
            planet.dhappypoints for planet in planets_group_with_taxes
        ]
        assert is_monotonic_increasing(dhappypoints_range)

    def test_dhappypoints_are_zero_when_hp_are_max(self, planet):
        planet.taxes = 0
        assert planet.happypoints == planet.max_happypoints
        assert not planet.dhappypoints

    def test_dhappypoints_is_int(self, planet):
        assert type(planet.dhappypoints) is int


class TestPlanetMines:
    @pytest.mark.parametrize("clans", range(0, cfg.planet_max_mines))
    def test_max_mines_depends_on_clans(self, planet_with_clans):
        assert planet_with_clans.max_mines == planet_with_clans.clans

    @pytest.mark.parametrize(
        "clans",
        range(cfg.planet_max_mines, cfg.max_clans_in_planet, 100),
    )
    def test_planet_max_mines_depends_on_config(self, planet_with_clans):
        assert planet_with_clans.max_mines == cfg.planet_max_mines

    def test_can_build_mines_return_zero_if_max_mines(self, colonized_planet):
        colonized_planet.pythonium = colonized_planet.mine_cost.pythonium
        colonized_planet.megacredits = colonized_planet.mine_cost.megacredits
        colonized_planet.mines = colonized_planet.max_mines
        assert not colonized_planet.can_build_mines()

    def test_can_build_mines_return_zero_if_no_mc(self, colonized_planet):
        colonized_planet.megacredits = 0
        assert not colonized_planet.can_build_mines()

    def test_can_build_mines_return_zero_if_no_pythonium(
        self, colonized_planet
    ):
        colonized_planet.pythonium = 0
        assert not colonized_planet.can_build_mines()

    def test_can_build_mines_depends_on_minimum_pythonium(
        self, colonized_planet
    ):
        colonized_planet.pythonium = colonized_planet.mine_cost.pythonium
        colonized_planet.megacredits = (
            colonized_planet.mine_cost.megacredits * 2
        )
        assert colonized_planet.can_build_mines() == 1

    def test_can_build_mines_depends_on_minimum_megacredits(
        self, colonized_planet
    ):
        colonized_planet.pythonium = colonized_planet.mine_cost.pythonium * 2
        colonized_planet.megacredits = colonized_planet.mine_cost.megacredits
        assert colonized_planet.can_build_mines() == 1

    def test_can_build_mines_is_int(self, planet):
        assert type(planet.can_build_mines()) is int

    def test_mine_cost_is_transfer(self, planet):
        assert type(planet.mine_cost) is Transfer

    def test_mines_init_is_zero(self, planet):
        assert not planet.mines


class TestPlanetPythonium:
    @pytest.mark.parametrize("mines_range", (range(0, cfg.planet_max_mines),))
    def test_dpythonium_increases_with_mines(self, planets_group_with_mines):
        dpythonium_range = [
            planet.dpythonium for planet in planets_group_with_mines
        ]
        assert is_monotonic_increasing(dpythonium_range)

    @pytest.mark.parametrize("concentrations_range", (range(0, 100),))
    def test_dpythonium_increases_with_concentration(
        self, planets_group_with_concentration
    ):
        dpythonium_range = [
            planet.dpythonium for planet in planets_group_with_concentration
        ]
        assert is_monotonic_increasing(dpythonium_range)

    @pytest.mark.parametrize(
        "happypoints_range", (range(0, cfg.happypoints_tolerance),)
    )
    def test_dpythonium_decreases_with_rioting_index(
        self, planets_group_with_happypoints
    ):
        dpythonium_range = [
            planet.dpythonium for planet in planets_group_with_happypoints
        ]
        assert is_monotonic_increasing(dpythonium_range)

    def test_dpythonium_is_int(self, planet):
        assert type(planet.dpythonium) is int

    def test_underground_dpythonium_is_int(self, planet):
        assert type(planet.underground_pythonium) is int

    def test_concentration_is_float(self, planet):
        assert type(planet.concentration) is float

    def test_concentration_is_ratio(self, planet):
        assert 0 <= planet.concentration <= 1


class TestPlanetMegacredits:
    @pytest.mark.parametrize("taxes_collection_factor", (range(0, 100),))
    def test_dmegacredits_increases_with_taxes_collection_factor(
        self, planets_group_with_collection_factor
    ):
        dmegacredits_range = [
            planet.dmegacredits
            for planet in planets_group_with_collection_factor
        ]
        assert is_monotonic_increasing(dmegacredits_range)

    @pytest.mark.parametrize(
        "clans_range", (range(0, cfg.max_clans_in_planet, 100),)
    )
    def test_dmegacredits_increases_with_clans(self, planets_group_with_clans):
        dmegacredits_range = [
            planet.dmegacredits for planet in planets_group_with_clans
        ]
        assert is_monotonic_increasing(dmegacredits_range)

    @pytest.mark.parametrize("taxes_range", (range(0, cfg.tolerable_taxes),))
    def test_dmegacredits_increases_with_taxes(self, planets_group_with_taxes):
        dmegacredits_range = [
            planet.dmegacredits for planet in planets_group_with_taxes
        ]
        assert is_monotonic_increasing(dmegacredits_range)

    @pytest.mark.parametrize("happypoints_range", (range(0, 100),))
    def test_dmegacredits_decreases_with_rioting_index(
        self, planets_group_with_happypoints
    ):
        dmegacredits_range = [
            planet.dmegacredits for planet in planets_group_with_happypoints
        ]
        assert is_monotonic_decreasing(dmegacredits_range)

    def test_dmegacredits_is_int(self, planet):
        assert type(planet.dmegacredits) is int

    def test_megacredits_init_is_zero(self, planet):
        assert not planet.megacredits

    def test_taxes_init_is_zero(self, planet):
        assert not planet.taxes


class TestPlanetRiotingIndex:
    @pytest.mark.parametrize(
        "happypoints",
        range(0, cfg.happypoints_tolerance),
    )
    def test_rioting_index_decrease_with_happypoints_below_tolerance(
        self, planet_with_hp
    ):
        assert planet_with_hp.rioting_index < 1

    @pytest.mark.parametrize(
        "happypoints",
        range(cfg.happypoints_tolerance, 100),
    )
    def test_rioting_index_no_effect_with_happypoints_above_tolerance(
        self, planet_with_hp
    ):
        assert planet_with_hp.rioting_index == 1


class TestPlanetClans:
    @pytest.mark.parametrize("happypoints_range", (range(0, 100),))
    def test_dclans_decreases_with_rioting_index(
        self, planets_group_with_happypoints
    ):
        dclans_range = [
            planet.dclans for planet in planets_group_with_happypoints
        ]
        assert is_monotonic_decreasing(dclans_range)

    def test_dclans_is_int(self, planet):
        assert type(planet.dclans) is int

    def test_clans_init_is_zero(self, planet):
        assert not planet.clans

    def test_dclans_zero_on_max_clans_in_planet_is_reached(
        self, optimal_temperature_planet
    ):
        optimal_temperature_planet.clans = cfg.max_clans_in_planet
        assert not optimal_temperature_planet.dclans

    def test_dclans_in_optimal_temperature_is_pisitive(
        self, optimal_temperature_planet
    ):
        optimal_temperature_planet.clans = 100
        assert optimal_temperature_planet.dclans > 0


class TestPlanetOrders:
    def test_get_orders_return_list(self, colonized_planet):
        orders = colonized_planet.get_orders()
        assert isinstance(orders, list)
        assert all([
            isinstance(order, PlanetOrderRequest)
            for order in orders
        ])

    @pytest.mark.parametrize("taxes", range(0, 101))
    def test_set_taxes_order(self, taxes, colonized_planet):
        colonized_planet.taxes = taxes
        orders = colonized_planet.get_orders()
        taxes_order = next(o for o in orders if o.name == "planet_set_taxes")
        assert taxes_order.id == colonized_planet.id
        assert 'taxes' in taxes_order.kwargs
        assert taxes_order.kwargs['taxes'] == taxes

    @pytest.mark.parametrize("new_mines", range(1, 101))
    def test_build_mines_order(self, new_mines, colonized_planet):
        colonized_planet.new_mines = new_mines
        orders = colonized_planet.get_orders()
        build_mines_order = next(
            o for o in orders if o.name == "planet_build_mines"
        )
        assert build_mines_order.id == colonized_planet.id
        assert 'new_mines' in  build_mines_order.kwargs
        assert build_mines_order.kwargs['new_mines'] == new_mines

    def test_no_mines_order_if_new_mines_is_zero(self, colonized_planet):
        orders = colonized_planet.get_orders()
        order_names = [o.name for o in orders]
        assert "planet_build_mines" not in order_names

    def test_build_ship_order(self, ship_type, colonized_planet):
        colonized_planet.new_ship = ship_type
        orders = colonized_planet.get_orders()
        build_ship_order = next(
            o for o in orders if o.name == "planet_build_ship"
        )
        assert build_ship_order.id == colonized_planet.id
        assert 'new_ship' in build_ship_order.kwargs
        assert build_ship_order.kwargs['new_ship'] is ship_type

    def test_no_ship_order_if_new_ship_is_none(self, colonized_planet):
        orders = colonized_planet.get_orders()
        order_names = [o.name for o in orders]
        assert "planet_build_ship" not in order_names
