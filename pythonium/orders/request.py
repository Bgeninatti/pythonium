from uuid import UUID

import attr


@attr.s
class OrderRequest:

    name: str = attr.ib()
    id: UUID = attr.ib()
    kwargs: dict = attr.ib()


class ShipOrderRequest(OrderRequest):
    ...


class PlanetOrderRequest(OrderRequest):
    ...
