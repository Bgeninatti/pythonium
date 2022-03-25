import importlib
import random
import time
import uuid
from pathlib import Path

import click

from . import __version__
from .game import Game
from .game_modes import ClassicMode
from .helpers import random_name
from .logger import setup_logger
from .output_handler import StandardOutputHanlder, StreamOutputHanlder

HELP_EPILOG = "A space strategy algorithmic-game build in python"


def set_seed(seed):
    random.seed(seed)
    uuid.uuid4 = lambda: uuid.UUID(version=4, int=random.getrandbits(128))


@click.group(help=HELP_EPILOG)
@click.version_option(__version__)
@click.pass_context
def cli(ctx):
    pass


@cli.command()
@click.pass_context
@click.argument("galaxy-name")
@click.argument("players", nargs=-1)
@click.option("--seed", default=time.time(), type=int)
@click.option("--raise-exceptions/--no-raise-exceptions", default=False)
@click.option("--verbose/--no-verbose", default=False)
@click.option("--stream-state/--no-stream-state", default=False)
def run(
    ctx,
    galaxy_name,
    players,
    seed,
    raise_exceptions,
    verbose,
    stream_state,
    *args,
    **kwargs,
):
    set_seed(seed)

    game_mode = ClassicMode()
    galaxy_name = galaxy_name if galaxy_name else random_name(6)

    logfile = Path.cwd() / f"{galaxy_name}.log"
    setup_logger(logfile, verbose=verbose)

    _players = []
    for player_module in players:
        player = importlib.import_module(player_module)
        _player = player.Player()
        _players.append(_player)

    if stream_state:
        output_handler = StreamOutputHanlder()
    else:
        output_handler = StandardOutputHanlder()

    game = Game(
        name=galaxy_name,
        players=_players,
        gmode=game_mode,
        output_handler=output_handler,
        raise_exceptions=raise_exceptions,
    )
    game.play()


@cli.command()
def visualize():
    click.echo("implement me")
