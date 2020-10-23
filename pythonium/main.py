import argparse
import importlib
import os
import sys
import time

from . import __version__
from .game import Game
from .game_modes import ClassicMode
from .metrics_collector import MetricsCollector

HELP_EPILOG = "A space strategy algorithmic-game build in python"


def go():
    parser = argparse.ArgumentParser(prog='pythonium', epilog=HELP_EPILOG)
    parser.add_argument(
        '-V', '--version', action='store_true',
        help="show version and info about the system, and exit")
    parser.add_argument(
        '--players', action="extend", nargs="+", help="")
    parser.add_argument(
        '--metrics', action="store_true", default="classic", help="")

    args = parser.parse_args()

    if args.version:
        print("Running 'pythonium' version", __version__)
        return 0

    game_mode = ClassicMode()

    players = []
    for player_module in args.players:
        player_class = importlib.import_module(player_module)
        player = player_class.Player()
        players.append(player)

    start = time.time()
    game = Game(players, game_mode)
    game.play()
    sys.stdout.write(f"Game ran in {round(time.time() - start, 2)} seconds\n")

    print(args.metrics)
    if args.metrics:
        sys.stdout.write("Building report...")
        start = time.time()
        with open(os.path.join(os.getcwd(), game.logfile)) as logfile:
            metrics = MetricsCollector(logfile)
        metrics.build_report()
        sys.stdout.write(f"Report built in {round(time.time() - start, 2)} seconds\n")

