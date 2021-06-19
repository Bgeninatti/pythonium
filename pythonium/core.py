import uuid
from abc import ABC
from typing import NewType, Tuple

import attr

Position = NewType("Position", Tuple[int, int])


@attr.s
class StellarThing(ABC):
    position: Position = attr.ib(converter=Position)
    """
    Position of the `StellarThing` in (x, y) coordinates.
    """

    id: uuid = attr.ib(factory=uuid.uuid4)
    """
    Unique identifier for the `StellarThing`
    """

    player: str = attr.ib(default=None)
    """
    The owner of the ``StellarThing`` or ``None`` if no one owns it.
    """

    def move(self, position: Position) -> None:
        raise NotImplementedError
