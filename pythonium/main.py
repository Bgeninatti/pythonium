import http.server
import importlib
import os
import random
import re
import socketserver
import time
import uuid
import webbrowser
from datetime import date
from datetime import datetime as dt
from pathlib import Path

import click

from . import __version__
from .game import Game
from .game_modes import GAME_MODES
from .helpers import random_name
from .logger import setup_logger
from .output_handler import OUTPUT_HANDLERS
from .rules.extractor import OrdersExtractor

HELP_EPILOG = "A space strategy algorithmic-game build in python"
dir_path = os.path.dirname(os.path.realpath(__file__))
WEB_RENDERER_TEMPLATE = os.path.join(dir_path, "webrenderer/index.html")
PORT = 8000


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
@click.option("--output-handler", default="standard")
@click.option("--game-mode", default="classic")
@click.option("--seed", default=time.time(), type=int)
@click.option("--raise-exceptions/--no-raise-exceptions", default=False)
@click.option("--verbose/--no-verbose", default=False)
def run(
    ctx,
    galaxy_name,
    players,
    output_handler,
    game_mode,
    seed,
    raise_exceptions,
    verbose,
    *args,
    **kwargs,
):
    set_seed(seed)

    game_mode = GAME_MODES[game_mode]()
    galaxy_name = galaxy_name if galaxy_name else random_name(6)
    output_handler = OUTPUT_HANDLERS[output_handler]()

    logfile = Path.cwd() / f"{galaxy_name}.log"
    setup_logger(logfile, verbose=verbose)

    _players = []
    for player_module in players:
        player = importlib.import_module(player_module)
        fantasy_name = player.Player.class_fantasy_name
        _player_name = f"{random_name(len(fantasy_name))} [{fantasy_name}]"
        _player = player.Player(_player_name)
        _players.append(_player)
    # breakpoint()

    orders_extractor = OrdersExtractor(game_mode, raise_exceptions)

    game = Game(
        name=galaxy_name,
        players=_players,
        game_mode=game_mode,
        output_handler=output_handler,
        orders_extractor=orders_extractor,
    )
    game.play()


@cli.command()
@click.argument("state")
@click.option("--html", default=None)
def visualize(state, html):
    with open(state, "r") as state_file:
        state_data = parseToPOJO(state_file.read())

    with open(WEB_RENDERER_TEMPLATE, "r") as template_file:
        template = template_file.read()
        web = template.replace("<!-- DATA PLACEHOLDER -->", state_data)

    output_fname = html
    if output_fname is None:
        prefix, ext = os.path.splitext(state)
        ts = dt.timestamp(dt.now())
        output_fname = prefix + str(ts) + ".html"

    with open(output_fname, "w") as out_file:
        out_file.write(web)

    handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), handler) as httpd:
        click.echo("Server started at localhost:" + str(PORT))
        url = "http://localhost:{port}/{path}".format(
            port=PORT, path=output_fname
        )
        click.echo("Visualization in: " + url)
        webbrowser.open(url)
        httpd.serve_forever()


def parseToPOJO(data_json):
    prefix, *states, suffix = data_json.splitlines()
    pojo = f"""{{
        turns: {get_data_turns(states)},
        galaxyName: "{get_data_galaxy_name(prefix)}",
        players: {get_data_players(data_json)},
    }}"""

    return pojo


def get_data_galaxy_name(prefix):
    return prefix.split("|")[2]


def get_data_turns(states):
    return "[{}]".format(",\n".join(states))


def get_data_players(data_json):
    def oc_to_name(oc):
        return oc[len('"player": ') :]

    names_occurrencies = re.findall('"player": "[^(?!")]*"', data_json)
    names = list(set([oc_to_name(name_oc) for name_oc in names_occurrencies]))

    if len(names) == 1:
        return f"[{names[0]}]"
    return f"[{names[0]}, {names[1]}]"
