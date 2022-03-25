import sys
import attr
import json
from typing import IO

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
        if winner is None:
            message = f"\nPlayer {winner} wins\n"
        else:
            message = "\nNobody won\n"
        self.output.write(message)



@attr.s
class StreamOutputHanlder(OutputHandler):

    def start(self, galaxy):
        self.output.write(f'pythonium|{__version__}|{galaxy.name}\n')

    def step(self, galaxy, context):
        self.output.write(json.dumps(galaxy.serialize()))
        self.output.write('\n')

    def finish(self, galaxy, winner):
        self.output.write(f'pythonium|{galaxy.name}|{galaxy.turn}|{winner}\n')
