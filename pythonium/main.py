import argparse
import importlib
import logging
import sys
import time
from pathlib import Path

from . import __version__
from .game import Game
from .game_modes import ClassicMode
from .helpers import random_name
from .logger import setup_logger


HELP_EPILOG = "A space strategy algorithmic-game build in python"


def go():
    parser = argparse.ArgumentParser(prog="pythonium", epilog=HELP_EPILOG)
    parser.add_argument(
        "-V",
        "--version",
        action="store_true",
        help="show version and info about the system, and exit",
    )
    parser.add_argument("--players", action="extend", nargs="+", help="")
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Show logs in stdout",
    )
    parser.add_argument(
        "--raise-exceptions",
        action="store_true",
        default=False,
        help="If the commands computations (for any player) fails, raise "
        "the exception and stop.",
    )
    parser.add_argument(
        "--galaxy-name", default="", help="An identification for the game"
    )

    parser.add_argument(
        "--stream-state",
        action="store_true",
        default=False,
        help="Print to standard output",
    )

    args = parser.parse_args()

    if args.version:
        print("Running 'pythonium' version", __version__)
        return 0

    game_mode = ClassicMode()
    galaxy_name = random_name(6)

    logfile = Path.cwd() / f"{galaxy_name}.log"
    setup_logger(logfile, verbose=args.verbose)

    players = []
    for player_module in args.players:
        player_class = importlib.import_module(player_module)
        player = player_class.Player()
        players.append(player)

    game = Game(
        name=galaxy_name,
        players=players,
        gmode=game_mode,
        raise_exceptions=args.raise_exceptions,
        stream_state=args.stream_state
    )
    game.play()
