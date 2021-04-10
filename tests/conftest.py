import pytest

from pythonium import AbstractPlayer, Game, Planet, Transfer, cfg
from pythonium.logger import setup_logger

from .game_modes import SandboxGameMode


class TestPlayer(AbstractPlayer):

    name = "Test Player"

    def next_turn(self, galaxy, context):
        return galaxy


@pytest.fixture
def logfile(tmp_path):
    return tmp_path / "tests.log"


@pytest.fixture(autouse=True)
def logger_setup(logfile):
    setup_logger(logfile)


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
    return Game("test_sector", [player], game_mode)


@pytest.fixture
def dummy_planet():
    """
    Returns a dummy instance of :class:`Planet`
    """
    mine_cost = Transfer(megacredits=10, pythonium=20)
    return Planet(1, (0, 0), cfg.optimal_temperature, 0, 0, 0, mine_cost)
