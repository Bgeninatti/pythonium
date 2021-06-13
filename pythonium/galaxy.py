from itertools import groupby
from typing import Dict, Iterable, Iterator, List, Set, Tuple

import numpy as np

from . import cfg
from .core import Position, StellarThing
from .explosion import Explosion
from .planet import Planet
from .ship import Ship


class Galaxy:
    """
    Galaxy of planets that represents the map of the game, and all the \
    known universe of things.

    :param size: Galaxy height and width
    :param things: Stellar things that compound the galaxy
    :param explosions: Known explosions in the galaxy
    :param turn: Time in galaxy
    """

    def __init__(
        self,
        name: str,
        size: Position,
        things: List[StellarThing],
        explosions: List[Explosion] = None,
        turn: int = 0,
    ):
        self.name = name
        """
        Galaxxy name.
        """

        self.turn: int = turn
        """
        Turn or actual time in the galaxy
        """

        self.size: Position = size
        """
        Width and height of the galaxy
        """

        self.stellar_things = things
        """
        All the things that compounds the galaxy
        """

        self._planets: Dict[Position, Planet] = {}
        """
        All the :class:`Planet` in the galaxy indexed by position
        """

        self._ships: List[Ship] = []
        """
        A list with all the :class:`Ship` in the galaxy
        """

        self.explosions: List[Explosion] = explosions or []
        """
        A list with all the recent :class:`Explosion`.
        """

    @property
    def planets(self):
        if not self._planets:
            planets = filter(
                lambda t: isinstance(t, Planet), self.stellar_things
            )
            self._planets = {p.position: p for p in planets}
        return self._planets

    @property
    def ships(self):
        if not self._ships:
            self._ships = list(
                filter(lambda t: isinstance(t, Ship), self.stellar_things)
            )
        return self._ships

    def __str__(self):
        return f"Galaxy(size={self.size}, planets={len(self.planets)})"

    def __repr__(self):
        return self.__str__()

    @property
    def known_races(self) -> Set[str]:
        """
        List all the known races that own at least one ship or one planet.
        """
        return {
            thing.player
            for thing in self.stellar_things
            if thing.player is not None
        }

    @staticmethod
    def compute_distance(a: Position, b: Position) -> float:
        """
        Compute the distance in ly between two points (usually two ``position`` attributes).

        :param a: Point of origin to compute the distance
        :param b: Point of destination to compute the distance
        """
        return np.linalg.norm(np.array(a) - np.array(b))

    def add_ship(self, ship: Ship):
        """
        Add a new ship to the known ships in the galaxy and assign an Id to it.
        """
        self.stellar_things.append(ship)
        self._ships = []

    def distances_to_planets(self, point: Position) -> Dict[Position, float]:
        """
        Compute the distance between the ``point`` and all the planets in the galaxy.
        """
        return dict(
            ((p, self.compute_distance(p, point)) for p in self.planets.keys())
        )

    def nearby_planets(
        self,
        point: Position,
        turns: int = 1,
        speed: int = cfg.ship_speed,
    ) -> List[Planet]:
        """
        Return all the planet that are ``turns`` away or less,
        traveling at a speed defined by ``cfg.ship speed``
        """
        distances = self.distances_to_planets(point)
        return list(
            filter(
                lambda p: distances[p.position] <= speed * turns,
                self.planets.values(),
            )
        )

    def get_player_planets(self, player: str) -> Iterable[Planet]:
        """
        Returns an iterable for all the known planets that belongs to``player``
        """
        for planet in filter(
            lambda p: p.player == player, self.planets.values()
        ):
            yield planet

    def get_player_ships(self, player: str) -> Iterable[Ship]:
        """
        Returns an iterable for known ships that belong to ``player``
        """
        for ship in filter(lambda s: s.player == player, self.ships):
            yield ship

    def get_ships_in_deep_space(self) -> Iterable[Ship]:
        """
        Returns an iterable for all the ships that are not located on a planet
        """
        positions = {n.position for n in self.ships}.difference(
            set(self.planets.keys())
        )
        for ship in filter(lambda s: s.position in positions, self.ships):
            yield ship

    def get_ships_in_position(self, position: Position) -> Iterable[Ship]:
        """
        Returns an iterable for all the known ships in the given position
        """
        for ship in filter(lambda s: s.position == position, self.ships):
            yield ship

    def search_ship(self, nid: int) -> Ship:
        """
        Return the ship with ID ``nid`` if any and is known
        """
        match = [ship for ship in self.ships if ship.id == nid]
        if match:
            return match.pop()

    def search_planet(self, pid: int) -> Planet:
        """
        Return the planet with ID ``nid`` if any
        """
        match = [
            planet for planet in self.planets.values() if planet.id == pid
        ]
        if match:
            return match.pop()

    def get_ships_by_position(self) -> Dict[Position, List[Ship]]:
        """
        Returns a dict with ships ordered by position.
        Ships in the same positions are grouped in a list.
        """
        return dict(
            (
                (position, list(ships))
                for position, ships in groupby(
                    self.ships, lambda s: s.position
                )
            )
        )

    def get_ships_in_planets(self) -> Iterable[Tuple[Planet, List[Ship]]]:
        """
        Return a list of tuples ``(planet, ships)`` where ``planet`` is a :class:`Planet`
        instance and ``ships`` is a list with all the ships located on the planet
        """
        ships_by_position = self.get_ships_by_position()
        for position, planet in self.planets.items():
            ships = ships_by_position.get(position)
            if not ships:
                continue
            yield planet, ships

    def get_ships_conflicts(self) -> Iterable[List[Ship]]:
        """
        Return all the ships in conflict: Ships with, at last, one enemy ship
        in the same position
        """
        ships_by_position = [
            list(ships)
            for pos, ships in groupby(self.ships, lambda s: s.position)
        ]
        # keep only the groups with more than one player
        for ships in filter(
            lambda ships: len({s.player for s in ships if s.player}) > 1,
            ships_by_position,
        ):
            yield ships

    def get_ocuped_planets(self) -> Iterable[Planet]:
        """
        Return all the planets colonized by any race
        """
        for planet in filter(
            lambda p: p.player is not None, self.planets.values()
        ):
            yield planet

    def get_planets_conflicts(self) -> Iterable[Tuple[Planet, List[Ship]]]:
        """
        Return all the planets in conflict: Planets with at least one enemy ship on it
        """
        ships_by_position = self.get_ships_by_position()
        destroyed_ships = [e.ship for e in self.explosions]
        for planet in self.get_ocuped_planets():
            ships = ships_by_position.get(planet.position)
            if not ships or not any(
                s
                for s in ships
                if s.player != planet.player and s not in destroyed_ships
            ):
                continue
            yield planet, ships

    def remove_destroyed_ships(self):
        """
        Remove the destroyed ships from the list
        """
        explosions_ids = [e.ship.id for e in self.explosions]
        self.stellar_things = list(
            filter(
                lambda things: things.id not in explosions_ids,
                self.stellar_things,
            )
        )
        self._ships = []
