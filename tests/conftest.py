
import pytest
from pythonium import cfg, Game, Player, Planet

from .game_modes import SandboxGameMode


@pytest.fixture
def game():
    game_mode = SandboxGameMode()
    player = Player(1)
    return Game(game_mode, [player])

@pytest.fixture
def dummy_planet():
    return Planet(1, (0, 0), cfg.optimal_temperature, 0, 0, 0)
