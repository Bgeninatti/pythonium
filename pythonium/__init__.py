from . import bots, core, debugger, logger
from .explosion import Explosion
from .galaxy import Galaxy
from .game import Game
from .planet import Planet
from .player import AbstractPlayer
from .ship import Ship
from .ship_type import ShipType
from .vectors import Transfer

__all__ = [
    "__version__",
    "core",
    "Planet",
    "Galaxy",
    "Ship",
    "ShipType",
    "Explosion",
    "Game",
    "AbstractPlayer",
    "Transfer",
    "bots",
    "logger",
    "debugger",
]

__version__ = "0.2.0b0"
