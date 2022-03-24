import math
import random

import pytest

from pythonium import Galaxy
from tests.factories import ExplosionFactory, ShipFactory, fake_positions


class TestGalaxyBasics:
    @pytest.fixture
    def expected_repr(self, galaxy):
        return f"Galaxy(size={galaxy.size}, planets={len(galaxy.planets)})"

    @pytest.fixture
    def another_random_position(self, galaxy_size):
        return next(fake_positions(galaxy_size))

    @pytest.fixture
    def expected_distance_between_positions(
        self, random_position, another_random_position
    ):
        a = random_position[0] - another_random_position[0]
        b = random_position[1] - another_random_position[1]
        return math.sqrt(a**2 + b**2)

    def test_repr(self, galaxy, expected_repr):
        assert str(galaxy) == expected_repr
        assert str(galaxy) == galaxy.__repr__()

    def test_planet_index(self, planets, galaxy):
        for planet in planets:
            assert galaxy.planets[planet.position] is planet

    def test_ship_index(self, ships, galaxy):
        assert galaxy.ships == ships

    def test_compute_distance(
        self,
        galaxy,
        random_position,
        another_random_position,
        expected_distance_between_positions,
    ):
        distance = galaxy.compute_distance(
            random_position, another_random_position
        )
        assert distance == expected_distance_between_positions

    def test_known_races(self, expected_players, galaxy):
        assert all(player in galaxy.known_races for player in expected_players)


class TestDistancesToPlanets:
    @pytest.fixture
    def expected_distances(self, faker, when, random_position, planets):
        expected_distances = {}
        for planet in planets:
            random_distance = faker.pyint(min_value=0)
            when(Galaxy).compute_distance(
                planet.position,
                random_position,
            ).thenReturn(random_distance)
            expected_distances[planet.position] = random_distance
        return expected_distances

    def test_distances_to_planets(
        self, expected_distances, random_position, galaxy
    ):
        assert expected_distances == galaxy.distances_to_planets(
            random_position
        )


class TestNearbyPlanets:
    @pytest.fixture
    def speed(self, faker):
        return faker.pyint(min_value=50, max_value=200)

    @pytest.mark.parametrize("turns", list(range(1, 6)))
    def test_nearby_planets(self, galaxy, random_position, turns, speed):
        nearby_planets = galaxy.nearby_planets(
            point=random_position, neighborhood=turns * speed
        )
        for planet in nearby_planets:
            assert (
                galaxy.compute_distance(planet.position, random_position)
                <= turns * speed
            )


class TestGetPlayerPlanets:
    @pytest.fixture
    def expected_planets(self, planets, random_player):
        return list(filter(lambda p: p.player == random_player, planets))

    def test_get_player_planets(self, galaxy, expected_planets, random_player):
        assert (
            list(galaxy.get_player_planets(random_player)) == expected_planets
        )

    def test_get_player_planets_fake_player(self, galaxy, faker):
        assert not list(galaxy.get_player_planets(faker.word()))


class TestSearchPlanet:
    def test_search_planet(self, galaxy, random_planet):
        assert galaxy.search_planet(random_planet.id) is random_planet

    def test_planet_not_found(self, galaxy, fake_id):
        assert galaxy.search_planet(fake_id) is None


class TestOcupedPlanets:
    @pytest.fixture
    def expected_ocuped_planets(self, planets):
        return [planet for planet in planets if planet.player is not None]

    def test_ocuped_planets(self, galaxy, expected_ocuped_planets):
        assert list(galaxy.get_ocuped_planets()) == expected_ocuped_planets


class TestAddShip:
    @pytest.fixture
    def new_ship(self, galaxy_size, expected_players, random_position):
        return ShipFactory(
            position=random_position,
            player=random.choice(expected_players),
        )

    def test_add_ship(self, galaxy, new_ship):
        assert new_ship not in galaxy.ships
        galaxy.add_ship(new_ship)
        assert new_ship in galaxy.ships


class TestGetPlayerShips:
    @pytest.fixture
    def expected_ships(self, ships, random_player):
        return [ship for ship in ships if ship.player == random_player]

    def test_get_player_ships(self, galaxy, expected_ships, random_player):
        assert list(galaxy.get_player_ships(random_player)) == expected_ships

    def test_get_player_ships_fake_player(self, galaxy, faker):
        assert not list(galaxy.get_player_ships(faker.word()))


class TestSearchShip:
    def test_search_ship(self, galaxy, random_ship):
        assert galaxy.search_ship(random_ship.id) is random_ship

    def test_ship_not_found(self, galaxy, fake_id):
        assert galaxy.search_ship(fake_id) is None


class TestRemoveDestroyedShips:
    @pytest.fixture
    def explosions(self, random_ship, faker):
        return [ExplosionFactory(ship=random_ship)]

    def test_remove_destroyed_ships(self, galaxy, random_ship, explosions):
        galaxy.explosions = explosions
        assert random_ship in galaxy.ships
        galaxy.remove_destroyed_ships()
        assert random_ship not in galaxy.ships
        galaxy.add_ship(random_ship)


class TestGetPlanetsConflicts:
    @pytest.fixture
    def expected_ships_in_conflict(self, ships_in_planets_galaxy):
        return ships_in_planets_galaxy.get_ships_by_position()

    def test_planets_conflicts(
        self, expected_ships_in_conflict, ships_in_planets_galaxy
    ):
        conflicts = ships_in_planets_galaxy.get_planets_conflicts()
        for planet, ships in conflicts:
            assert ships == expected_ships_in_conflict[planet.position]


class TestGetShipsConflicts:
    def test_ships_conflicts(
        self, ships_in_conflict_galaxy, ships_in_conflict
    ):
        conflicts = ships_in_conflict_galaxy.get_ships_conflicts()
        assert [ships_in_conflict] == list(conflicts)


class TestGetShipsInPlanets:
    @pytest.fixture
    def expected_ships_in_planets(self, ships_in_planets_galaxy):
        return ships_in_planets_galaxy.get_ships_by_position()

    def test_ships_in_planets(
        self, ships_in_planets_galaxy, expected_ships_in_planets
    ):
        result = ships_in_planets_galaxy.get_ships_in_planets()
        for planet, ships in result:
            assert ships == expected_ships_in_planets[planet.position]


class TestGetShipsByPosition:
    @pytest.fixture
    def ships_by_position(self, galaxy):
        return galaxy.get_ships_by_position()

    def test_all_ships_in_ships_by_position(self, ships_by_position, galaxy):
        all_ships = [
            s
            for ships_group in ships_by_position.values()
            for s in ships_group
        ]
        assert all_ships == galaxy.ships

    def test_ships_by_position(self, ships_by_position):
        for position, ships in ships_by_position.items():
            for ship in ships:
                assert ship.position == position


class TestGetShipsInPosition:
    @pytest.fixture
    def position(self, random_ship):
        return random_ship.position

    @pytest.fixture
    def another_ship_in_position(self, position, galaxy):
        ship = ShipFactory(position=position)
        galaxy.add_ship(ship)
        return ship

    @pytest.fixture
    def ships_in_position(self, random_ship, another_ship_in_position):
        return [random_ship, another_ship_in_position]

    def test_ships_in_position(self, galaxy, position, ships_in_position):
        assert (
            list(galaxy.get_ships_in_position(position)) == ships_in_position
        )


class TestGetShipsInDeepSpace:
    def test_ships_in_deep_space(self, galaxy, ships):
        assert list(galaxy.get_ships_in_deep_space()) == ships


class TestGalaxySerialization:

    def test_serialize(self, galaxy):
        serialized_galaxy = galaxy.serialize()
        assert isinstance(serialized_galaxy, dict)
        assert 'things' in serialized_galaxy
        assert 'turn' in serialized_galaxy
        assert 'explosions' in serialized_galaxy
        assert 'size' in serialized_galaxy

    def test_deserialize(self, galaxy):
        serialized_galaxy = galaxy.serialize()
        deserialized_galaxy = Galaxy.deserialize(serialized_galaxy)
        assert galaxy == deserialized_galaxy
