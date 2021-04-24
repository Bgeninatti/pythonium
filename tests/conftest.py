import math
import random
import uuid

import pytest

from pythonium import AbstractPlayer, Game
from pythonium.logger import setup_logger
from tests.factories import (
    GalaxyFactory,
    PlanetFactory,
    ShipFactory,
    fake_position,
)

from .game_modes import SandboxGameMode


@pytest.fixture
def galaxy_size(faker):
    return 200, 200


@pytest.fixture
def expected_players(faker):
    return [faker.word(), faker.word()]


@pytest.fixture
def planets(faker, expected_players, galaxy_size):
    planets = []
    positions = []
    for _ in range(faker.pyint(min_value=10, max_value=20)):
        position = fake_position(galaxy_size)
        if position in positions:
            continue
        planet = PlanetFactory(
            position=fake_position(galaxy_size),
            player=random.choice(expected_players + [None]),
        )
        planets.append(planet)
        positions.append(position)
    return planets


@pytest.fixture
def ships(faker, expected_players, galaxy_size, planets):
    ships = []
    positions = [p.position for p in planets]
    for _ in range(faker.pyint(min_value=5, max_value=20)):
        position = fake_position(galaxy_size)
        if position in positions:
            continue
        ship = ShipFactory(
            position=position,
            player=random.choice(expected_players),
        )
        ships.append(ship)
        positions.append(position)
    return ships


@pytest.fixture
def ships_in_planets(faker, galaxy_size, planets):
    ships = []
    positions = [p.position for p in planets]
    for _ in range(faker.pyint(min_value=5, max_value=10)):
        position = random.choice(positions)
        ship = ShipFactory(
            position=position,
            player=faker.word(),
        )
        ships.append(ship)
        positions.append(position)
    return ships


@pytest.fixture
def ships_in_conflict(expected_players, galaxy_size):
    position = fake_position(galaxy_size)
    ships = []
    for player in expected_players:
        ship = ShipFactory(position=position, player=player)
        ships.append(ship)
    return ships


@pytest.fixture
def galaxy(planets, ships, galaxy_size):
    return GalaxyFactory(
        size=galaxy_size,
        things=planets + ships,
    )


@pytest.fixture
def ships_in_planets_galaxy(planets, ships_in_planets, galaxy_size):
    return GalaxyFactory(
        size=galaxy_size,
        things=planets + ships_in_planets,
    )


@pytest.fixture
def ships_in_conflict_galaxy(planets, ships_in_conflict, galaxy_size):
    return GalaxyFactory(
        size=galaxy_size,
        things=planets + ships_in_conflict,
    )


@pytest.fixture
def random_position(galaxy_size):
    return fake_position(galaxy_size)


@pytest.fixture
def fake_id():
    return uuid.uuid4()


@pytest.fixture
def random_player(expected_players):
    return random.choice(expected_players)


@pytest.fixture
def random_ship(ships):
    return random.choice(ships)


@pytest.fixture
def random_planet(planets):
    return random.choice(planets)


@pytest.fixture
def random_direction(planets):
    angle = random.random() * math.pi
    yield math.cos(angle), math.sin(angle)


#  fixtures for test_run_turn


class TestPlayer(AbstractPlayer):

    name = "Test Player"

    def next_turn(self, galaxy, context):
        return galaxy


@pytest.fixture
def logfile(tmp_path):
    return tmp_path / "tests.log"


@pytest.fixture(autouse=True)
def logger_setup(logfile):
    setup_logger(logfile)


@pytest.fixture
def test_player():
    """
    This don'tn return the same instance that is used in the game, but is useful to
    have a reference of `player.name`
    """
    return TestPlayer()


@pytest.fixture
def game():
    """
    Return an instance of the game
    """
    game_mode = SandboxGameMode()
    player = TestPlayer()
    return Game("test_sector", [player], game_mode)
