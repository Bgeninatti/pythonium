import copy
import curses
import json
import sys
from enum import Enum
from time import sleep
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
class StandardOutputHandler(OutputHandler):
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
class StreamOutputHandler(OutputHandler):
    def start(self, galaxy):
        self.output.write(f"pythonium|{__version__}|{galaxy.name}\n")

    def step(self, galaxy, context):
        self.output.write(json.dumps(galaxy.serialize()))
        self.output.write("\n")

    def finish(self, galaxy, winner):
        self.output.write(f"pythonium|{galaxy.name}|{galaxy.turn}|{winner}\n")


class ColorPairs(Enum):
    SPACE = (curses.COLOR_BLACK, curses.COLOR_BLACK)
    NEUTRAL_PLANET = (curses.COLOR_WHITE, curses.COLOR_WHITE)
    EXPLOSION = (curses.COLOR_YELLOW, curses.COLOR_YELLOW)

    PLAYER_1 = (curses.COLOR_RED, curses.COLOR_RED)
    PLAYER_1_SHIP_ON_PLANET = (curses.COLOR_RED, curses.COLOR_WHITE)
    PLAYER_1_SHIP_ON_SPACE = (curses.COLOR_RED, curses.COLOR_BLACK)

    PLAYER_2 = (curses.COLOR_BLUE, curses.COLOR_BLUE)
    PLAYER_2_SHIP_ON_PLANET = (curses.COLOR_BLUE, curses.COLOR_WHITE)
    PLAYER_2_SHIP_ON_SPACE = (curses.COLOR_BLUE, curses.COLOR_BLACK)


@attr.s
class CursesOutputHandler(OutputHandler):
    def start(self, galaxy):
        self.old_planets = []
        self.old_ships = []
        self.players = list(galaxy.known_races)
        self.sc = curses.initscr()
        self.height, self.width = self.sc.getmaxyx()
        self.win = curses.newwin(self.height, self.width, 0, 0)
        self.h_pixels_for_unit = self.height / galaxy.size[0]
        self.w_pixels_for_unit = self.width / galaxy.size[1]

        self.win.keypad(1)
        curses.curs_set(0)

        # Create colors
        self.colors = {}
        curses.start_color()
        for index, color_pair in enumerate(ColorPairs):
            color_index = index + 1
            curses.init_pair(color_index, *color_pair.value)
            self.colors[color_pair.name] = curses.color_pair(color_index)

        self.win.bkgd(' ', self._get_color(ColorPairs.SPACE))
        self.win.border(0)
        self.win.refresh()

    def step(self, galaxy, context):
        self._show_ships(galaxy.ships, galaxy)
        planets = self._get_planets(galaxy)
        self._show_explosions(galaxy.explosions)
        self._show_planets(planets)
        sleep(.5)

    def finish(self, galaxy, winner):
        self.win.timeout(2)
        self.sc.addstr(10, 30, f"pythonium: The winner is {winner} !!")
        self.sc.addstr(11, 30, f"at turn: {galaxy.turn}")
        self.sc.refresh()
        self.win.timeout(10)
        curses.endwin()

    def _get_color(self, color_pair):
        return self.colors[color_pair.name]

    def _get_planets(self, galaxy):
        return filter(lambda t: isinstance(t, Planet), galaxy.things)

    def _show_ships(self, ships, galaxy):
        for ship in ships:
            position = self._get_screen_position(ship)
            color_pair = self._get_ship_color_pair(ship, galaxy, position)
            character = 'Ö' if ship.type.name == 'carrier' else '╬'

            old_ship = self._find_old_ship(ship)
            if old_ship is not None:
                (current_position_h, current_position_w) = old_position = (
                    int(old_ship.position[0] * self.h_pixels_for_unit),
                    int(old_ship.position[1] * self.w_pixels_for_unit)
                )

                for current_position_h in range(old_position[0], position[0]):
                    current_position = (current_position_h, old_position[1])
                    if not self._exists_planet(galaxy, current_position):
                        color_pair = self._get_ship_color_pair(ship, galaxy, current_position)
                        self._show_step(current_position, character, color_pair)

                for current_position_w in range(old_position[1], position[1]):
                    current_position = (current_position_h, current_position_w)
                    if not self._exists_planet(galaxy, current_position):
                        color_pair = self._get_ship_color_pair(ship, galaxy, current_position)
                        self._show_step(current_position, character, color_pair)

            color_pair = self._get_ship_color_pair(ship, galaxy, position)
            self.win.addch(*position, character, color_pair)
            self.win.refresh()

        self.old_ships = copy.deepcopy(ships)

    def _show_planets(self, planets):
        for planet in planets:
            position = self._get_screen_position(planet)
            color_pair = self._get_planet_color_pair(planet)

            old_planet = self._find_old_planet(planet)
            if old_planet is None or old_planet[0].player != planet.player:
                self.win.addch(*position, curses.ACS_BLOCK, color_pair)
                self.win.refresh()

        self.old_planets = copy.deepcopy(planets)

    def _show_explosions(self, explosions):
        for explosion in explosions:
            power_escalated = int(explosion.total_attack / 10)
            expand_range = range(2, min(power_escalated, 20), 2)
            for current_range in [expand_range, reversed(expand_range)]:
                for size in current_range:
                    position = self._get_screen_position(explosion.ship)
                    box_h = position[0] - int(size / 2)
                    box_w = position[1] - int(size / 2)
                    self._show_box(box_h, box_w, size)

    def _show_box(self, box_h, box_w, size):
        if 0 < box_h <= self.height and 0 < box_w <= self.width:
            box = self.sc.subwin(size, size, box_h, box_w)
            box.bkgd(' ', self._get_color(ColorPairs.EXPLOSION))
            box.box()
            box.refresh()
            sleep(.06)
            box.bkgd(' ', self._get_color(ColorPairs.SPACE))
            box.erase()
            box.refresh()

    def _find_old_planet(self, planet):
        for old_planet in self.old_planets:
            if old_planet.id == planet.id:
                return old_planet
        return None

    def _find_old_ship(self, ship):
        for old_ship in self.old_ships:
            if old_ship.id == ship.id:
                return old_ship
        return None

    def _get_screen_position(self, thing):
        position_h = int(thing.position[0] * self.h_pixels_for_unit)
        position_w = int(thing.position[1] * self.w_pixels_for_unit)
        return [position_h, position_w]

    def _exists_planet(self, galaxy, position):
        for planet in self._get_planets(galaxy):
            planet_position = self._get_screen_position(planet)
            if planet_position[0] == position[0] and planet_position[1] == position[1]:
                return True
        return False

    def _show_step(self, position, character, color_pair):
        self.win.addch(*position, character, color_pair)
        self.win.refresh()
        sleep(.1)
        self.win.addch(*position, ' ', self._get_color(ColorPairs.SPACE))

    def _is_player_1(self, player):
        return self.players.index(player) == 0

    def _get_ship_color_pair(self, ship, galaxy, position):
        on_planet = self._exists_planet(galaxy, position)

        if not on_planet:
            if self._is_player_1(ship.player):
                return self._get_color(ColorPairs.PLAYER_1_SHIP_ON_SPACE)
            return self._get_color(ColorPairs.PLAYER_2_SHIP_ON_SPACE)

        if self._is_player_1(ship.player):
            return self._get_color(ColorPairs.PLAYER_1_SHIP_ON_PLANET)
        return self._get_color(ColorPairs.PLAYER_2_SHIP_ON_PLANET)

    def _get_planet_color_pair(self, planet):
        player = planet.player

        if player is None:
            return self._get_color(ColorPairs.NEUTRAL_PLANET)
        elif self._is_player_1(player):
            return self._get_color(ColorPairs.PLAYER_1)
        return self._get_color(ColorPairs.PLAYER_2)


OUTPUT_HANDLERS = {
    "standard": StandardOutputHandler,
    "stream": StreamOutputHandler,
    "curses": CursesOutputHandler
}
