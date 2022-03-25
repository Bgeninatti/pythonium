import json
import sys
from typing import IO

import attr

from pythonium import __version__


@attr.s
class OutputHandler:
    output: IO = attr.ib(default=sys.stdout)

    def start(self, galaxy):
        raise NotImplementedError()

    def step(self, galaxy, context):
        raise NotImplementedError()

    def finish(self, galaxy, winner):
        raise NotImplementedError()


@attr.s
class StandardOutputHanlder(OutputHandler):
    def start(self, galaxy):
        self.output.write("** Pythonium **\n")
        self.output.write(f"Running battle in galaxy #{galaxy.name}\n")

    def step(self, galaxy, context):
        self.output.write(f"\rPlaying game{'.' * int(galaxy.turn / 4)}")
        self.output.flush()

    def finish(self, galaxy, winner):
        if winner is not None:
            message = f"\nPlayer {winner} wins\n"
        else:
            message = "\nNobody won\n"
        self.output.write(message)


@attr.s
class StreamOutputHanlder(OutputHandler):
    def start(self, galaxy):
        data = {
            "version": __version__,
            "galaxy": galaxy.name,
            "players": [player for player in galaxy.known_races],
            "size": list(galaxy.size)
        }
        self.output.write(json.dumps(data))
        self.output.write("\n")


    def step(self, galaxy, context):
        data = {
            "galaxy": galaxy.serialize(),
            "score": context["score"]
        }
        self.output.write(json.dumps(data))
        self.output.write("\n")

    def finish(self, galaxy, winner):
        data = {
            "turns": galaxy.turn,
            "winner": winner
        }
        self.output.write(json.dumps(data))
