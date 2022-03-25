import attr


@attr.s
class OrderRequest:

    name: str = attr.ib()
    id: str = attr.ib()
    player: str = attr.ib()
    kwargs: dict = attr.ib()


class ShipOrderRequest(OrderRequest):
    ...


class PlanetOrderRequest(OrderRequest):
    ...
