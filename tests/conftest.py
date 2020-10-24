
import pytest
from pythonium import cfg, Game, Player, Planet

from .game_modes import SandboxGameMode

class TestPlayer(Player):

    name = 'Test Player'

    def next_turn(self, galaxy, context, t):
        return []

@pytest.fixture
def game():
    game_mode = SandboxGameMode()
    player = TestPlayer()
    return Game([player], game_mode)

@pytest.fixture
def dummy_planet():
    return Planet(1, (0, 0), cfg.optimal_temperature, 0, 0, 0)
