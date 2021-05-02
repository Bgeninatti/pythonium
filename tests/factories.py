from factory import Factory, Faker, SubFactory

from pythonium import Planet
from pythonium.ship_type import ShipType
from pythonium.vectors import Transfer


class TransferFectorFactory(Factory):
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


class PlanetFactory(Factory):
    class Meta:
        model = Planet

    position = (Faker("pyint", min_value=0), Faker("pyint", min_value=0))
    temperature = Faker("pyint", min_value=0, max_value=100)
    underground_pythonium = Faker("pyint", min_value=0)
    concentration = Faker("pyfloat", min_value=0, max_value=1)
    pythonium = Faker("pyint", min_value=0)
    mine_cost = SubFactory(PositiveTransferVectorFactory)
