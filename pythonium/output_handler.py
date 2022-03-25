import copy
import curses
import json
import sys
import time
from typing import IO

import attr

from . import __version__
from .planet import Planet


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
        self.show_ships(galaxy.ships, galaxy)
        
        planets = self.get_planets(galaxy)
        self.show_planets(planets)
        time.sleep(.3)

    def get_planets(self, galaxy):
        return filter(lambda t: isinstance(t, Planet), galaxy.things)

    def show_ships(self, ships, galaxy):
        for ship in ships:
            position = self.get_screen_position(ship)
            color_pair = self.get_ship_color_pair(ship, galaxy, position)
            character = 'Ö' if ship.type.name == 'carrier' else '╬'

            old_ship = self.find_old_ship(ship)
            if old_ship is not None:
                old_position = (
                    int(old_ship.position[0] * self.h_pixels_for_unit),
                    int(old_ship.position[1] * self.w_pixels_for_unit)
                )
                current_position_h = old_position[0]
                current_position_w = old_position[1]

                for current_position_h in range(old_position[0], position[0]):
                    current_position = (current_position_h, old_position[1])
                    if not self.exists_planet(galaxy, current_position):
                        color_pair = self.get_ship_color_pair(ship, galaxy, current_position)
                        self.show_step(current_position, character, color_pair)

                for current_position_w in range(old_position[1], position[1]):
                    current_position = (current_position_h, current_position_w)
                    if not self.exists_planet(galaxy, current_position):
                        color_pair = self.get_ship_color_pair(ship, galaxy, current_position)
                        self.show_step(current_position, character, color_pair)

            color_pair = self.get_ship_color_pair(ship, galaxy, position)
            self.win.addch(position[0], position[1], character, color_pair)
            self.win.refresh()

        self.old_ships = copy.deepcopy(ships)

    def show_planets(self, planets):
        for planet in planets:
            position = self.get_screen_position(planet)
            color_pair = self.get_planet_color_pair(planet)

            old_planet = self.find_old_planet(planet)
            if old_planet is None or old_planet[0].player != planet.player:
                self.win.addch(position[0], position[1], curses.ACS_BLOCK, color_pair)
                self.win.refresh()

        self.old_planets = copy.deepcopy(planets)

    def find_old_planet(self, planet):
        for old_planet in self.old_planets:
            if old_planet.id == planet.id:
                return old_planet
        return None

    def find_old_ship(self, ship):
        for old_ship in self.old_ships:
            if old_ship.id == ship.id:
                return old_ship
        return None

    def get_screen_position(self, thing):
        position_h = int(thing.position[0] * self.h_pixels_for_unit)
        position_w = int(thing.position[1] * self.w_pixels_for_unit)
        return [position_h, position_w]

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

    def exists_planet(self, galaxy, position):
        for planet in self.get_planets(galaxy):
            planet_position = self.get_screen_position(planet)
            if planet_position[0] == position[0] and planet_position[1] == position[1]:
                return True
        return False

    def show_step(self, position, character, color_pair):
        self.win.addch(position[0], position[1], character, color_pair)
        self.win.refresh()
        time.sleep(.05)
        self.win.addch(position[0], position[1], ' ', curses.color_pair(1))

    def get_ship_color_pair(self, ship, galaxy, position):
        in_planet = self.exists_planet(galaxy, position)
        if not in_planet:
            if ship.player == 'Solar Fed.':
                return curses.color_pair(7)
            return curses.color_pair(8)

        if ship.player == 'Solar Fed.':
            return curses.color_pair(5)
        return curses.color_pair(6)

    def get_planet_color_pair(self, planet):
        player = planet.player

        if player is None:
            return curses.color_pair(4)
        elif player == 'Solar Fed.':
            return curses.color_pair(3)
        return curses.color_pair(2)

OUTPUT_HANDLERS = {
    "standard": StandardOutputHanlder,
    "stream": StreamOutputHanlder,
    "curses": CursesOutputHanlder
}
