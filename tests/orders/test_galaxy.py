import random

import pytest

from pythonium.orders.galaxy import (
    ProduceResources,
    ResolvePlanetsConflicts,
    ResolveShipsConflicts,
)


class TestProduceResources:
    @pytest.fixture()
    def player_planets_count(self, galaxy, faker):
        return len(list(galaxy.get_ocuped_planets()))

    @pytest.fixture()
    def order(self, galaxy):
        return ProduceResources(galaxy=galaxy)

    def test_produce_in_occuped_planets(
        self, order, mocker, galaxy, player_planets_count
    ):
        spy = mocker.spy(order, "_produce_resources")
        order.execute()
        assert spy.call_count == player_planets_count

    def test_produce_happypoints(
        self, order, colonized_planet, happypoints_tolerance
    ):
        dhappypoints = colonized_planet.dhappypoints
        happypoints = colonized_planet.happypoints
        order._produce_resources(colonized_planet)
        assert colonized_planet.happypoints == happypoints + dhappypoints
        assert colonized_planet.happypoints > happypoints_tolerance

    def test_produce_megacredits(
        self, order, colonized_planet, happypoints_tolerance
    ):
        dmegacredits = colonized_planet.dmegacredits
        megacredits = colonized_planet.megacredits
        order._produce_resources(colonized_planet)
        assert colonized_planet.megacredits == megacredits + dmegacredits
        assert colonized_planet.happypoints > happypoints_tolerance

    def test_produce_pythonium(
        self, order, colonized_planet, happypoints_tolerance
    ):
        dpythonium = colonized_planet.dpythonium
        pythonium = colonized_planet.pythonium
        order._produce_resources(colonized_planet)
        assert colonized_planet.pythonium == pythonium + dpythonium
        assert colonized_planet.happypoints > happypoints_tolerance

    def test_produce_clans(
        self, order, colonized_planet, happypoints_tolerance
    ):
        dclans = colonized_planet.dclans
        clans = colonized_planet.clans
        order._produce_resources(colonized_planet)
        assert colonized_planet.clans == clans + dclans
        assert colonized_planet.happypoints > happypoints_tolerance


class TestResolveShipsConflicts:
    @pytest.fixture()
    def winner_ships(self, ships_in_conflict, winner):
        return [s for s in ships_in_conflict if s.player == winner]

    @pytest.fixture()
    def spy_remove_destroyed_ships(self, mocker, ships_in_conflict_galaxy):
        return mocker.spy(ships_in_conflict_galaxy, "remove_destroyed_ships")

    @pytest.fixture
    def expected_destroyed_ships(self, winner, ships_in_conflict):
        return [s for s in ships_in_conflict if s.player != winner]

    @pytest.fixture(autouse=True)
    def execute_order(
        self,
        spy_remove_destroyed_ships,
        ships_in_conflict_galaxy,
        tenacity,
        winner,
    ):
        order = ResolveShipsConflicts(ships_in_conflict_galaxy, tenacity)
        assert not ships_in_conflict_galaxy.explosions
        order.execute()
        return order

    @pytest.fixture
    def winner(self, ships_in_conflict_galaxy, mocker):
        winner = random.choice(list(ships_in_conflict_galaxy.known_races))
        mocker.patch(
            "pythonium.orders.galaxy.ResolveShipsConflicts._compute_winner",
            return_value=winner,
        )
        return winner

    def test_destroyed_ships_for_loosers(
        self, ships_in_conflict_galaxy, expected_destroyed_ships
    ):
        exploded_ships = [e.ship for e in ships_in_conflict_galaxy.explosions]
        assert exploded_ships == expected_destroyed_ships

    def test_remove_destroyed_ships(self, spy_remove_destroyed_ships):
        assert spy_remove_destroyed_ships.call_count == 1

    def test_winner_ships_still_exist(
        self, winner_ships, ships_in_conflict_galaxy
    ):
        assert all(s in ships_in_conflict_galaxy.ships for s in winner_ships)


class TestResolvePlanetsConflicts:
    @pytest.fixture()
    def winner(self, planet_conflict_galaxy):
        planet, ships = next(planet_conflict_galaxy.get_planets_conflicts())
        return ships[0].player

    @pytest.fixture()
    def conquered_planet_id(self, planet_conflict_galaxy):
        planet, ships = next(planet_conflict_galaxy.get_planets_conflicts())
        return planet.id

    def test_ship_without_attack_do_nothing(
        self, mocker, planet_pasive_conflict_galaxy
    ):
        order = ResolvePlanetsConflicts(planet_pasive_conflict_galaxy)
        spy_resolve_conflict = mocker.spy(order, "_resolve_planets_conflicts")
        order.execute()
        assert spy_resolve_conflict.call_count == 0

    def test_enemy_ships_conquer_planet(
        self, conquered_planet_id, winner, planet_conflict_galaxy
    ):
        order = ResolvePlanetsConflicts(planet_conflict_galaxy)
        order.execute()
        conquered_planet = planet_conflict_galaxy.search_planet(
            conquered_planet_id
        )
        assert conquered_planet.player == winner

    def test_conquered_planet_state(
        self, planet_conflict_galaxy, conquered_planet_id
    ):
        order = ResolvePlanetsConflicts(planet_conflict_galaxy)
        order.execute()
        conquered_planet = planet_conflict_galaxy.search_planet(
            conquered_planet_id
        )
        assert conquered_planet.clans == 1
        assert conquered_planet.mines == 0
        assert conquered_planet.taxes == 0
