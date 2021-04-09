from faker import Faker

from pythonium import Planet
from pythonium.ship_type import ShipType
from pythonium.vectors import Transfer


class TransferVectorFactory:

    faker = Faker()

    @classmethod
    def build_transfer_vector(cls):
        return Transfer(
            megacredits=cls.faker.pyint(min_value=1),
            pythonium=cls.faker.pyint(min_value=1),
        )


class ShipTypeFactory:

    faker = Faker()

    @classmethod
    def build(cls, **kwargs):
        ship_cost = TransferVectorFactory.build_transfer_vector()
        return ShipType(
            name=cls.faker.pystr(),
            cost=ship_cost,
            max_cargo=cls.faker.pyint(),
            max_mc=cls.faker.pyint(),
            attack=cls.faker.pyint(),
            speed=cls.faker.pyint(),
        )


class PlanetFactory:

    faker = Faker()

    @classmethod
    def build_planet(cls, **kwargs):
        mine_cost = TransferVectorFactory.build_transfer_vector()
        return Planet(
            pid=cls.faker.pyint(),
            position=(cls.faker.pyint(), cls.faker.pyint()),
            temperature=kwargs.get("temperature", cls.faker.pyint()),
            underground_pythonium=cls.faker.pyint(),
            concentration=kwargs.get(
                "concentration", cls.faker.pyfloat(min_value=0, max_value=1)
            ),
            pythonium=cls.faker.pyint(),
            mine_cost=mine_cost,
        )
