import curses
import json
import sys
import time
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
        if winner is None:
            message = f"\nPlayer {winner} wins\n"
        else:
            message = "\nNobody won\n"
        self.output.write(message)


@attr.s
class StreamOutputHanlder(OutputHandler):
    def start(self, galaxy):
        self.output.write(f"pythonium|{__version__}|{galaxy.name}\n")

    def step(self, galaxy, context):
        self.output.write(json.dumps(galaxy.serialize()))
        self.output.write("\n")

    def finish(self, galaxy, winner):
        self.output.write(f"pythonium|{galaxy.name}|{galaxy.turn}|{winner}\n")


@attr.s
class CursesOutputHanlder(OutputHandler):
    def __init__(self):
        super().__init__()
        self.sc = None
        self.win = None
        self.old_ships = []
        self.old_planets = []
        self.h_pixels_for_unit = 0
        self.w_pixels_for_unit = 0

    def start(self, galaxy):
        # Initialize screen
        self.old_ships = []
        self.old_planets = []
        self.sc = curses.initscr()
        h, w = self.sc.getmaxyx()
        self.win = curses.newwin(h, w, 0, 0)
        self.h_pixels_for_unit = h / galaxy.size[0]
        self.w_pixels_for_unit = w / galaxy.size[1]

        self.win.keypad(1)
        curses.curs_set(0)

        # Create colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_RED)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLUE)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_WHITE)
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_WHITE)
        curses.init_pair(6, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.init_pair(7, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(8, curses.COLOR_RED, curses.COLOR_BLACK)

        self.win.bkgd(' ', curses.color_pair(1))
        self.win.border(0)
        self.win.refresh()

    def step(self, galaxy, context):
        turn = galaxy.serialize()
        planets = [thing for thing in turn['things'] if self.is_planet(thing)]
        ships = [thing for thing in turn['things'] if self.is_ship(thing)]

        for item in [ships, planets]:
            for thing in item:
                # Get position
                position_h = int(thing['position'][0] * self.h_pixels_for_unit)
                position_w = int(thing['position'][1] * self.w_pixels_for_unit)

                # Get color
                color_pair = self.get_color_pair(thing, planets, position_h, position_w)

                # Draw thing
                if self.is_planet(thing):
                    old_planet = [planet for planet in self.old_planets if planet['id'] == thing['id']]
                    if len(old_planet) == 0 or old_planet[0]['player'] != thing['player']:
                        self.win.addch(position_h, position_w, curses.ACS_BLOCK, color_pair)
                        self.win.refresh()
                elif self.is_ship(thing):
                    if thing['type']['name'] == 'carrier':
                        character = 'Ö'
                    else:
                        character = '╬'

                    old_ship = [ship for ship in self.old_ships if ship['id'] == thing['id']]
                    if len(old_ship) > 0:
                        old_ship = old_ship[0]
                        old_position_h = int(old_ship['position'][0] * self.h_pixels_for_unit)
                        old_position_w = int(old_ship['position'][1] * self.w_pixels_for_unit)
                        current_position_h = old_position_h
                        current_position_w = old_position_w

                        for current_position_h in range(old_position_h, position_h):
                            if not self.exists_planet(planets, current_position_h, old_position_w):
                                color_pair = self.get_color_pair(thing, planets, current_position_h, old_position_w)
                                self.show_step(current_position_h, old_position_w, character, color_pair)
                        for current_position_w in range(old_position_w, position_w):
                            if not self.exists_planet(planets, current_position_h, current_position_w):
                                color_pair = self.get_color_pair(thing, planets, current_position_h, current_position_w)
                                self.show_step(current_position_h, current_position_w, character, color_pair)

                    color_pair = self.get_color_pair(thing, planets, position_h, position_w)
                    self.win.addch(position_h, position_w, character, color_pair)
                    self.win.refresh()

        time.sleep(.1)
        self.old_ships = ships
        self.old_planets = planets

    def finish(self, galaxy, winner):
        time.sleep(2)
        self.sc.addstr(10, 30, f"pythonium: The winner is {winner} !!")
        self.sc.addstr(11, 30, f"at turn: {galaxy.turn}")
        self.sc.refresh()
        time.sleep(10)
        curses.endwin()

    def is_planet(self, thing):
        return thing['thing_type'] == 'planet'

    def is_ship(self, thing):
        return thing['thing_type'] == 'ship'

    def exists_planet(self, planets, position_h, position_w):
        for planet in planets:
            planet_pos_h = int(planet['position'][0] * self.h_pixels_for_unit)
            planet_pos_w = int(planet['position'][1] * self.w_pixels_for_unit)
            if planet_pos_h == position_h and planet_pos_w == position_w:
                return True
        return False


    def show_step(self, position_h, position_w, character, color_pair):
        self.win.addch(position_h, position_w, character, color_pair)
        self.win.refresh()
        time.sleep(.05)
        self.win.addch(position_h, position_w, ' ', curses.color_pair(1))

    def get_color_pair(self, thing, planets, position_h, position_w):
        player = thing['player']

        if self.is_planet(thing):
            if player is None:
                return curses.color_pair(4)
            elif player == 'Solar Fed.':
                return curses.color_pair(3)
            return curses.color_pair(2)

        if not self.exists_planet(planets, position_h, position_w):
            if player == 'Solar Fed.':
                return curses.color_pair(7)
            return curses.color_pair(8)
        if player == 'Solar Fed.':
            return curses.color_pair(5)
        return curses.color_pair(6)


OUTPUT_HANDLERS = {
    "standard": StandardOutputHanlder,
    "stream": StreamOutputHanlder,
    "curses": CursesOutputHanlder
}
