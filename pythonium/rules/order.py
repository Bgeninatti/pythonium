import attr


@attr.s
class Order:

    name: str = attr.ib()
    id: str = attr.ib()
    player: str = attr.ib()
    kwargs: dict = attr.ib()


class ShipOrder(Order):
    ...


class PlanetOrder(Order):
    ...
