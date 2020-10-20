from .explosion import Explosion
from .galaxy import Galaxy
from .game import Game
from .game_modes import ClassicMode, GameMode
from .planet import Planet
from .ship import Ship
from .renderer import GifRenderer
from . import bots

__all__ = ['Planet', 'Galaxy', 'Ship', 'Explosion', 'ClassicMode', 'GameMode',
           'Game', 'GifRenderer', 'bots']


__version__ = '0.1.0a'
