import pytest

from pythonium import Planet, Transfer, cfg

from .factories import PlanetFactory


def is_monotonic_increasing(sample):
    return all(sample[i] <= sample[i + 1] for i in range(len(sample) - 1))


def is_monotonic_decreasing(sample):
    return all(sample[i] >= sample[i + 1] for i in range(len(sample) - 1))


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


class TestPlanet:
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

    @pytest.mark.parametrize("clans", range(0, cfg.planet_max_mines))
    def test_max_mines_depends_on_clans(self, planet_with_clans):
        assert planet_with_clans.max_mines == planet_with_clans.clans

    @pytest.mark.parametrize(
        "clans",
        range(cfg.planet_max_mines, cfg.max_clans_in_planet, 100),
    )
    def test_planet_max_mines_depends_on_config(self, planet_with_clans):
        assert planet_with_clans.max_mines == cfg.planet_max_mines

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

    @pytest.mark.parametrize("mines_range", (range(0, cfg.planet_max_mines),))
    def test_dpythonium_increases_with_mines(self, planets_group_with_mines):
        dpythonium_range = [
            planet.dpythonium for planet in planets_group_with_mines
        ]
        assert is_monotonic_increasing(dpythonium_range)

    @pytest.mark.parametrize("concentrations_range", (range(0, 100, 5),))
    def test_dpythonium_increases_with_concentration(
        self, planets_group_with_concentration
    ):
        dpythonium_range = [
            planet.dpythonium for planet in planets_group_with_concentration
        ]
        assert is_monotonic_increasing(dpythonium_range)
