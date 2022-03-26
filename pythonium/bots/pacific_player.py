import random

import attr

from ..player import AbstractPlayer
from ..ship import Ship
from .standard_player import Player as StandardPlayer


class Player(StandardPlayer):
    """
    Same as :class:`standard_player.Player` but always build carriers
    """

    class_fantasy_name = "Nofight Ink."
    tenacity = 0
