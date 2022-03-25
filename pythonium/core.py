import uuid
from abc import ABC
from typing import NewType, Tuple

import attr

Position = NewType("Position", Tuple[int, int])


@attr.s
class StellarThing(ABC):
    thing_type: str = attr.ib(init=False)
    """
    A reference of what kind of thing is this
    """

    position: Position = attr.ib(converter=tuple)
    """
    Position of the `StellarThing` in (x, y) coordinates.
    """

    id: str = attr.ib(factory=lambda: str(uuid.uuid4()))
    """
    Unique identifier for the `StellarThing`
    """

    player: str = attr.ib(default=None)
    """
    The owner of the ``StellarThing`` or ``None`` if no one owns it.
    """

    def move(self, position: Position) -> None:
        raise NotImplementedError
