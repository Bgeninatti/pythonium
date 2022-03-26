import numpy as np
import pytest

from pythonium.core import Position
from pythonium.rules.ship import ShipMoveRule


class TestShipMoveRule:
    @pytest.fixture
    def short_target(self, faker, random_ship, random_direction):
        magnitude = faker.pyint(max_value=random_ship.speed)
        return Position(
            (
                random_ship.position[0] + int(random_direction[0] * magnitude),
                random_ship.position[1] + int(random_direction[1] * magnitude),
            )
        )

    @pytest.fixture
    def long_target(self, faker, random_ship, random_direction):
        magnitude = faker.pyint(
            min_value=random_ship.speed + 1, max_value=random_ship.speed * 2
        )
        return Position(
            (
                random_ship.position[0] + int(random_direction[0] * magnitude),
                random_ship.position[1] + int(random_direction[1] * magnitude),
            )
        )

    @pytest.fixture
    def long_movement_expected_stop(
        self, long_target, random_ship, random_direction
    ):
        return Position(
            (
                random_ship.position[0]
                + int(random_direction[0] * random_ship.speed),
                random_ship.position[1]
                + int(random_direction[1] * random_ship.speed),
            )
        )

    def test_ship_short_move_rule(self, galaxy, random_ship, short_target):
        rule = ShipMoveRule(ship=random_ship, target=short_target)
        rule.execute(galaxy)
        assert random_ship.position == short_target
        assert random_ship.target is None

    def test_ship_long_move_rule(
        self, galaxy, random_ship, long_target, long_movement_expected_stop
    ):
        rule = ShipMoveRule(ship=random_ship, target=long_target)
        rule.execute(galaxy)
        assert random_ship.target == long_target
        assert np.all(
            np.isclose(
                random_ship.position, long_movement_expected_stop, atol=1
            )
        )
