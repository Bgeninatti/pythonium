import argparse
import importlib
import os
import sys
import time

from . import __version__
from .game import Game
from .game_modes import ClassicMode
from .metrics_collector import MetricsCollector
from .helpers import random_name
from .logger import get_logger

HELP_EPILOG = "A space strategy algorithmic-game build in python"


def go():
    parser = argparse.ArgumentParser(prog='pythonium', epilog=HELP_EPILOG)
    parser.add_argument(
        '-V', '--version', action='store_true',
        help="show version and info about the system, and exit")
    parser.add_argument(
        '--players', action="extend", nargs="+", help="")
    parser.add_argument(
        '--metrics',
        action="store_true",
        default=False,
        help="Generate a report with metrics of the game")
    parser.add_argument(
        '--verbose', action="store_true", default=False, help="Show logs in stdout")
    parser.add_argument(
        '--raise-exceptions',
        action="store_true",
        default=False,
        help="If the commands computations (for any player) fails, raise "
             "the exception and stop.")
    parser.add_argument(
        '--sector-name', default="", help="An identification for the game")

    args = parser.parse_args()

    if args.version:
        print("Running 'pythonium' version", __version__)
        return 0

    base_dir = os.getcwd()
    game_mode = ClassicMode()
    sector_name = random_name(6)
    logfile_path = os.path.join(base_dir, f"{sector_name}.log")
    logger = get_logger(sector_name, filename=logfile_path, verbose=args.verbose)

    players = []
    for player_module in args.players:
        player_class = importlib.import_module(player_module)
        player = player_class.Player()
        players.append(player)

    start = time.time()
    game = Game(sector_name,
                players,
                game_mode,
                logger=logger,
                raise_exceptions=args.raise_exceptions)
    game.play()
    sys.stdout.write(f"Game ran in {round(time.time() - start, 2)} seconds\n")

    if args.metrics:
        sys.stdout.write("Building report...\n")
        start = time.time()
        with open(logfile_path) as logfile:
            metrics = MetricsCollector(logfile)
        metrics.build_report()
        sys.stdout.write(f"Report built in {round(time.time() - start, 2)} seconds\n")
