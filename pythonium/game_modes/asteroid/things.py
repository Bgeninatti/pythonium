import math
import random
from typing import Tuple

import attr

from pythonium.core import StellarThing


def random_direction():
    angle = random.random() * math.pi
    return math.cos(angle), math.sin(angle)


@attr.s(auto_attribs=True, repr=False)
class Asteroid(StellarThing):
    thing_type = "planet"
    direction: Tuple[float, float] = attr.ib(factory=random_direction)
