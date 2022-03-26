import importlib
from pathlib import Path

import click


from . import __version__
from .game import Game
from .game_modes import ClassicMode
from .helpers import random_name
from .logger import setup_logger
from .output_handler import OUTPUT_HANDLERS

HELP_EPILOG = "A space strategy algorithmic-game build in python"


@click.group(help=HELP_EPILOG)
@click.version_option(__version__)
@click.pass_context
def cli(ctx):
    pass


@cli.command()
@click.pass_context
@click.argument("galaxy-name")
@click.argument("players", nargs=-1)
@click.option("--output_handler", default='standard')
@click.option("--raise-exceptions/--no-raise-exceptions", default=False)
@click.option("--verbose/--no-verbose", default=False)
def run(
    ctx,
    galaxy_name,
    players,
    output_handler,
    raise_exceptions,
    verbose,
    *args,
    **kwargs,
):

    game_mode = ClassicMode()
    galaxy_name = galaxy_name if galaxy_name else random_name(6)
    output_handler = OUTPUT_HANDLERS[output_handler]()

    logfile = Path.cwd() / f"{galaxy_name}.log"
    setup_logger(logfile, verbose=verbose)

    _players = []
    for player_module in players:
        player = importlib.import_module(player_module)
        _player = player.Player()
        _players.append(_player)

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
