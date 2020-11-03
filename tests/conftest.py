
import pytest
from pythonium import cfg, Game, AbstractPlayer, Planet

from .game_modes import SandboxGameMode

class TestPlayer(AbstractPlayer):

    name = 'Test Player'

    def next_turn(self, galaxy, context):
        return galaxy

@pytest.fixture
def test_player():
    """
    This don'tn return the same instance that is used in the game, but is useful to
    have a reference of `player.name`
    """
    return TestPlayer()

@pytest.fixture
def game():
    """
    Return an instance of the game
    """
    game_mode = SandboxGameMode()
    player = TestPlayer()
    return Game([player], game_mode)

@pytest.fixture
def dummy_planet():
    """
    Returns a dummy instance of :class:`Planet`
    """
    return Planet(1, (0, 0), cfg.optimal_temperature, 0, 0, 0, (10, 20))
