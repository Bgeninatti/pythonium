import math
import random
import uuid

import attr
import pytest

from pythonium import AbstractPlayer, Game, cfg
from pythonium.logger import setup_logger
from tests.factories import (
    GalaxyFactory,
    PlanetFactory,
    ShipFactory,
    ShipTypeFactory,
    fake_positions,
)

from .game_modes import SandboxGameMode


@pytest.fixture
def galaxy_size():
    return 200, 200


@pytest.fixture
def expected_players(faker):
    return [faker.word(), faker.word()]


@pytest.fixture
def planets(faker, expected_players, galaxy_size):
    amount_of_planets = faker.pyint(min_value=2, max_value=20)
    planets = []
    for position in fake_positions(galaxy_size, amount_of_planets):
        planet = PlanetFactory(
            position=position,
            player=random.choice(expected_players + [None]),
        )
        planets.append(planet)
    return planets


@pytest.fixture
def ships(faker, expected_players, galaxy_size, planets):
    ships = []
    amount_of_ships = faker.pyint(min_value=2, max_value=20)
    positions = [p.position for p in planets]
    for position in fake_positions(galaxy_size, amount_of_ships, positions):
        ship = ShipFactory(
            position=position,
            player=random.choice(expected_players),
        )
        ships.append(ship)
    return ships


@pytest.fixture
def ships_in_planets(faker, galaxy_size, planets):
    ships = []
    amount_of_ships = faker.pyint(min_value=2, max_value=20)
    positions = [p.position for p in planets]
    for _ in range(amount_of_ships):
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
    position = next(fake_positions(galaxy_size))
    ships = []
    for player in expected_players:
        ship = ShipFactory(position=position, player=player)
        ships.append(ship)
    return ships


@pytest.fixture
def planet_pasive_conflict_galaxy(expected_players, galaxy_size):
    position = next(fake_positions(galaxy_size))
    planet = PlanetFactory(position=position, player=expected_players[0])
    ship = ShipFactory(position=position, player=expected_players[1], attack=0)
    return GalaxyFactory(size=galaxy_size, things=[planet, ship])


@pytest.fixture
def planet_conflict_galaxy(expected_players, galaxy_size):
    position = next(fake_positions(galaxy_size))
    planet = PlanetFactory(position=position, player=expected_players[0])
    no_attack_ship_type = ShipTypeFactory(attack=100)
    ship = ShipFactory(
        position=position, player=expected_players[1], type=no_attack_ship_type
    )
    return GalaxyFactory(size=galaxy_size, things=[planet, ship])


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
    return next(fake_positions(galaxy_size))


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


@pytest.fixture()
def colonized_planets(planets):
    return [p for p in planets if p.player is not None]


@pytest.fixture()
def colonized_planet(colonized_planets):
    return random.choice(colonized_planets)


@pytest.fixture
def random_direction(planets):
    angle = random.random() * math.pi
    yield math.cos(angle), math.sin(angle)


@pytest.fixture
def happypoints_tolerance():
    return cfg.happypoints_tolerance


@pytest.fixture
def tenacity():
    return cfg.tenacity


#  fixtures for test_run_turn


@attr.s
class TestPlayer(AbstractPlayer):

    name = attr.ib()

    def next_turn(self, galaxy, context):
        return galaxy


@pytest.fixture
def logfile(tmp_path):
    return tmp_path / "tests.log"


@pytest.fixture(autouse=True)
def logger_setup(logfile):
    setup_logger(logfile)


@pytest.fixture
def player(faker):
    return TestPlayer(faker.name())


@pytest.fixture
def another_player(faker):
    return TestPlayer(faker.name())


@pytest.fixture
def game_mode():
    return SandboxGameMode()


@pytest.fixture
def game(game_mode):
    """
    Return an instance of the game
    """
    player = TestPlayer()
    return Game("test_sector", [player], game_mode)
