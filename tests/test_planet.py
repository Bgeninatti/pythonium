import pytest

from pythonium import Planet, Transfer, cfg

from .factories import PlanetFactory


def is_monotonic_increasing(sample):
    return all(sample[i] <= sample[i + 1] for i in range(len(sample) - 1))


def is_monotonic_decreasing(sample):
    return all(sample[i] >= sample[i + 1] for i in range(len(sample) - 1))


@pytest.fixture
def planet():
    return PlanetFactory.build_planet()


@pytest.fixture
def optimal_temperature_planet():
    return PlanetFactory.build_planet(temperature=cfg.optimal_temperature)


@pytest.fixture
def temperatured_planet(temperature):
    return PlanetFactory.build_planet(temperature=temperature)


@pytest.fixture
def planet_with_clans(clans):
    planet = PlanetFactory.build_planet()
    planet.clans = clans
    return planet


@pytest.fixture
def planet_with_hp(happypoints):
    planet = PlanetFactory.build_planet()
    planet.happypoints = happypoints
    return planet


@pytest.fixture
def planets_group_with_mines(mines_range):
    planets = []
    for mines in mines_range:
        planet = PlanetFactory.build_planet(concentration=1.0)
        planet.mines = mines
        planets.append(planet)
    return planets


@pytest.fixture
def planets_group_with_concentration(concentrations_range):
    planets = []
    for concentration in concentrations_range:
        planet = PlanetFactory.build_planet(mines=100)
        planet.concentration = concentration / 100
        planets.append(planet)
    return planets


@pytest.fixture
def planets_group_with_happypoints(happypoints_range):
    planets = []
    for happypoints in happypoints_range:
        planet = PlanetFactory.build_planet(happypoints=happypoints, mines=100)
        planets.append(planet)
    return planets


@pytest.fixture
def planets_group_with_collection_factor(taxes_collection_factor):
    planets = []
    for collection_factor in taxes_collection_factor:
        planet = PlanetFactory.build_planet(clans=100)
        planet.taxes = cfg.tolerable_taxes
        planets.append(planet)
    return planets


@pytest.fixture
def planets_group_with_clans(clans_range):
    planets = []
    for clans in clans_range:
        planet = PlanetFactory.build_planet(clans=clans)
        planets.append(planet)
    return planets


@pytest.fixture
def planets_group_with_taxes(taxes_range):
    planets = []
    for taxes in taxes_range:
        planet = PlanetFactory.build_planet()
        planet.taxes = taxes
        planets.append(planet)
    return planets


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

    @pytest.mark.parametrize("temperature", range(0, 101))
    def test_init_hp_are_max(self, temperatured_planet):
        assert (
            temperatured_planet.max_happypoints
            == temperatured_planet.happypoints
        )

    @pytest.mark.parametrize("taxes_range", (range(0, cfg.tolerable_taxes),))
    def test_dhappypoints_increases_with_taxes_less_than_tolerable(
        self, planets_group_with_taxes
    ):
        dhappypoints_range = [
            planet.dhappypoints for planet in planets_group_with_taxes
        ]
        assert is_monotonic_increasing(dhappypoints_range)

    @pytest.mark.parametrize("taxes_range", (range(cfg.tolerable_taxes, 100),))
    def test_dhappypoints_decreases_with_taxes_more_than_tolerable(
        self, planets_group_with_taxes
    ):
        dhappypoints_range = [
            planet.dhappypoints for planet in planets_group_with_taxes
        ]
        assert is_monotonic_decreasing(dhappypoints_range)

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

    def test_can_build_mines_return_zero_if_max_mines(self, planet):
        planet.mines = planet.max_mines
        assert not planet.can_build_mines()

    def test_can_build_mines_return_zero_if_no_mc(self, faker, planet):
        planet.megacredits = 0
        planet.pythonium = faker.pyint(min_value=planet.mine_cost.pythonium)
        assert not planet.can_build_mines()

    def test_can_build_mines_return_zero_if_no_pythonium(self, faker, planet):
        planet.pythonium = 0
        planet.megacredits = faker.pyint(
            min_value=planet.mine_cost.megacredits
        )
        assert not planet.can_build_mines()

    def test_can_build_mines_is_int(self, planet):
        assert type(planet.can_build_mines()) is int

    def test_mine_cost_is_transfer(self, planet):
        assert type(planet.mine_cost) is Transfer


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

    @pytest.mark.parametrize("happypoints_range", (range(0, 100),))
    def test_dpythonium_decreases_with_rioting_index(
        self, planets_group_with_happypoints
    ):
        dpythonium_range = [
            planet.dpythonium for planet in planets_group_with_happypoints
        ]
        assert is_monotonic_decreasing(dpythonium_range)

    def test_dpythonium_is_int(self, planet):
        assert type(planet.dpythonium) is int


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
