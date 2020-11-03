
import pytest
from pythonium import Planet, cfg


@pytest.mark.parametrize('clans_in_planet', [
    10, 100, 200, 300, 400, 500, 600, 700
])
def test_mines_proportional_to_clans_until_max(dummy_planet, clans_in_planet):
    dummy_planet.clans = clans_in_planet

    if dummy_planet.clans <= cfg.planet_max_mines:
        assert dummy_planet.max_mines == dummy_planet.clans
    else:
        assert dummy_planet.max_mines == cfg.planet_max_mines


@pytest.mark.parametrize('happypoints', range(100))
def test_rioting_index(dummy_planet, happypoints):
    dummy_planet.happypoints = happypoints

    if dummy_planet.happypoints >= cfg.happypoints_tolerance:
        assert dummy_planet.rioting_index == 1
    else:
        assert dummy_planet.rioting_index < 1


@pytest.mark.parametrize('temperature', range(1, 100))
def test_max_happypoints(temperature):
    planet = Planet(1, (0, 0), temperature, 0, 0, 0, (10, 20))

    if not temperature or temperature == 100:
        assert planet.max_happypoints == cfg.happypoints_tolerance
    elif temperature == cfg.optimal_temperature:
        assert planet.max_happypoints == 100
    else:
        assert planet.max_happypoints < 100 \
            and planet.max_happypoints > cfg.happypoints_tolerance
