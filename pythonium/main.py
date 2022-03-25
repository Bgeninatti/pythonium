import argparse
import importlib
import logging
import re
import sys
import time
from pathlib import Path

import click

from . import __version__
from .game import Game
from .game_modes import ClassicMode
from .helpers import random_name
from .logger import setup_logger
from .output_handler import StandardOutputHanlder, StreamOutputHanlder

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
@click.option("--raise-exceptions/--no-raise-exceptions", default=False)
@click.option("--verbose/--no-verbose", default=False)
@click.option("--stream-state/--no-stream-state", default=False)
def run(
    ctx,
    galaxy_name,
    players,
    raise_exceptions,
    verbose,
    stream_state,
    *args,
    **kwargs,
):

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


from datetime import date, datetime as dt
import os

@cli.command()
@click.argument("state")
@click.option("--html", default=None)
def visualize(state, html):
    with open(state, "r") as state_file:
        state_data = parseToJS(state_file.read())

    with open("pythonium/index.html", "r") as template_file:
        template = template_file.read()
        web = template.replace(
            "<!-- DATA PLACEHOLDER -->",
            state_data
        )
    
    output_fname = html
    if output_fname is None:
        prefix, ext = os.path.splitext(state)
        ts = dt.timestamp(dt.now())
        output_fname = prefix + str(ts) + ".html"
        
    with open(output_fname, "w") as out_file:
        out_file.write(web)
        click.echo('Visualization in ' + output_fname)

def parseToJS(data_json):
    match_data = f"""{{
        turns: {get_data_turns(data_json)},
        galaxyName: {get_data_galaxy_name(data_json)},
        players: {get_data_players(data_json)},
    }}"""

    return match_data

def get_data_galaxy_name(data_json):
    name_end = data_json.index('\n')
    data_turns = data_json[:name_end+1]
    name = re.findall('\w+\n', data_turns)[0][:-1]
    return f'"{name}"'

def get_data_turns(data_json):
    data_js_start = data_json.index('\n')
    data_turns = data_json[data_js_start:]
    data_turns = data_turns.replace('}{', '}, {')
    data_turns = data_turns.replace('}\n{', '},\n{')

    start_tail = data_turns.index('|') - len('pythonium')
    data_turns = data_turns[0:start_tail]
    data_turns = f'[{data_turns}]'

    return data_turns

def get_data_players(data_json):
    def oc_to_name(oc):
        return oc[len('"player": '):]

    names_occurrencies = re.findall('"player": "[^(?!")]*"', data_json)
    names = list(set([oc_to_name(name_oc) for name_oc in names_occurrencies]))

    if len(names) == 1:
        return f'[{names[0]}]'
    return f'[{names[0]}, {names[1]}]'
