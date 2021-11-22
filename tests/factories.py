import random
from typing import List, Optional, Set, Tuple

from factory import Factory, Faker, SubFactory

from pythonium import Explosion, Galaxy, Planet, Ship
from pythonium.core import Position
from pythonium.ship_type import ShipType
from pythonium.vectors import Transfer

fake = Faker._get_faker()
MAP_SIZE = (fake.pyint(min_value=10), fake.pyint(min_value=10))


def fake_positions(
    map_size: Tuple[int, int],
    amount: int = 1,
    exclude: Optional[List[Position]] = None,
):
    exclude = exclude or []

    def get_available_points(size: int, excluded: Set):
        all_points = set(range(size))
        all_points.discard(excluded)
        return list(all_points)

    excluded_x = [p[0] for p in exclude]
    excluded_y = [p[1] for p in exclude]
    x_coordinates = get_available_points(map_size[0], set(excluded_x))
    y_coordinates = get_available_points(map_size[1], set(excluded_y))
    random.shuffle(x_coordinates)
    random.shuffle(y_coordinates)
    for _ in range(amount):
        yield Position((x_coordinates.pop(), y_coordinates.pop()))


class TransferVectorFactory(Factory):
    class Meta:
        model = Transfer

    megacredits = Faker("pyint")
    pythonium = Faker("pyint")
    clans = Faker("pyint")


class PositiveTransferVectorFactory(Factory):
    class Meta:
        model = Transfer

    megacredits = Faker("pyint", min_value=0)
    pythonium = Faker("pyint", min_value=0)
    clans = Faker("pyint", min_value=0)


class NegativeTransferVectorFactory(Factory):
    class Meta:
        model = Transfer

    megacredits = Faker("pyint", max_value=0)
    pythonium = Faker("pyint", max_value=0)
    clans = Faker("pyint", max_value=0)


class ShipTypeFactory(Factory):
    class Meta:
        model = ShipType

    name = Faker("word")
    cost = SubFactory(PositiveTransferVectorFactory, clans=0)
    max_cargo = Faker("pyint", min_value=0)
    max_mc = Faker("pyint", min_value=0)
    attack = Faker("pyint", min_value=0)
    speed = Faker("pyint", min_value=0)


class ShipFactory(Factory):
    class Meta:
        model = Ship

    type = SubFactory(ShipTypeFactory)
    max_cargo = Faker("pyint", min_value=0)
    max_mc = Faker("pyint", min_value=0)
    attack = Faker("pyint", min_value=0)
    speed = Faker("pyint", min_value=0)


class PlanetFactory(Factory):
    class Meta:
        model = Planet

    position = next(fake_positions(MAP_SIZE))
    temperature = Faker("pyint", min_value=0, max_value=100)
    underground_pythonium = Faker("pyint", min_value=0)
    concentration = Faker("pyfloat", min_value=0, max_value=1)
    pythonium = Faker("pyint", min_value=0)
    mine_cost = SubFactory(PositiveTransferVectorFactory)


class ExplosionFactory(Factory):
    class Meta:
        model = Explosion

    ship = SubFactory(ShipFactory)
    ships_involved = Faker("pyint", min_value=2)
    total_attack = Faker("pyint", min_value=100)


class GalaxyFactory(Factory):
    class Meta:
        model = Galaxy

    name = Faker("word")
    size = MAP_SIZE
    things = [
        PlanetFactory(position=next(fake_positions(MAP_SIZE)))
        for _ in range(10)
    ]
