from typing import List, Tuple

from factory import Factory, Faker, SubFactory

from pythonium import Explosion, Galaxy, Planet, Ship
from pythonium.core import Position
from pythonium.ship_type import ShipType
from pythonium.vectors import Transfer

fake = Faker._get_faker()


def fake_position(map_size: Tuple[int, int]):
    max_x, max_y = map_size
    return Position(
        (
            fake.pyint(min_value=0, max_value=max_x),
            fake.pyint(min_value=0, max_value=max_y),
        )
    )


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
    cost = SubFactory(PositiveTransferVectorFactory)
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

    position = (Faker("pyint", min_value=0), Faker("pyint", min_value=0))
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


MAP_SIZE = (fake.pyint(min_value=10), fake.pyint(min_value=10))


class GalaxyFactory(Factory):
    class Meta:
        model = Galaxy

    name = Faker("word")
    size = MAP_SIZE
    things = [
        PlanetFactory(position=fake_position(MAP_SIZE)) for _ in range(10)
    ]
