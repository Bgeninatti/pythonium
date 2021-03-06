from itertools import groupby
from typing import Dict, List, Tuple, Set

import numpy as np

from . import cfg
from .planet import Planet
from .ship import Ship
from .explosion import Explosion

class Galaxy:
    """
    Galaxy of planets that represents the map of the game, and all the \
    known universe of things.

    :param size: Galaxy height and width
    :param planets: Planets that compound the galaxy
    :param ships: Ships in the galaxy
    :param explosions: Known explosions in the galaxy
    """

    def __init__(self,
                 size: Tuple[int, int],
                 planets: Dict[Tuple[int, int], Planet],
                 ships: List[Ship],
                 explosions: List[Explosion] = None):
        self.size = size
        """
        Width and height of the galaxy
        """

        self.planets = planets
        """
        All the :class:`Planet` in the galaxy indexed by position
        """

        self.ships = ships
        """
        A list with all the :class:`Ship` in the galaxy
        """

        self.explosions = [] if not explosions else explosions
        """
        A list with all the recent :class:`Explosion`.
        """

        self._next_ship_id = max(s.nid for s in ships) + 1 if ships else 0

    @property
    def known_races(self) -> Set[str]:
        """
        List all the known races that own at least one ship or one planet.
        """
        return {s.player for s in self.ships} \
            .union({p.player for p in self.planets.values() if p.player is not None})

    @staticmethod
    def compute_distance(a: Tuple[int, int], b: Tuple[int, int]) -> float:
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
        ship.nid = self._next_ship_id
        self.ships.append(ship)
        self._next_ship_id += 1


    def distances_to_planets(self, point: Tuple[int, int]) -> Dict[Tuple[int, int], float]:
        """
        Compute the distance between the ``point`` and all the planets in the galaxy.
        """
        return dict(
            ((p, self.compute_distance(p, point)) for p in self.planets.keys())
        )

    def nearby_planets(self, point: Tuple[int, int], turns: int = 1) -> List[Planet]:
        """
        Return all the planet that are ``turns`` away or less,
        traveling at a speed defined by ``cfg.ship speed``
        """
        distances = self.distances_to_planets(point)
        return list(
            filter(lambda p: distances[p.position] <= cfg.ship_speed*turns,
                   self.planets.values())
        )

    def get_player_planets(self, player_name: str) -> Dict[Tuple[int, int], Planet]:
        """
        Return all the known planets that belong to the player with the name ``player_name``
        """
        return dict(
            ((pos, p) for pos, p in self.planets.items() if p.player == player_name)
        )

    def get_player_ships(self, player_name: str) -> List[Ship]:
        """
        Return all the known ships that belong to the player with name the ``player_name``
        """
        return [ship for ship in self.ships if player_name == ship.player]

    def get_ships_in_deep_space(self) -> List[Ship]:
        """
        Return a list with all the ships that are not located on a planet
        """
        positions = {n.position for n in self.ships} \
            .difference(set(self.planets.keys()))
        return [n for n in self.ships if n.position in positions]

    def get_ships_in_position(self, position: Tuple[int, int]) -> List[Ship]:
        """
        Return a list with all the known ships in the given position
        """
        return list(filter(lambda s: s.position == position, self.ships))

    def search_ship(self, nid: int) -> Ship:
        """
        Return the ship with ID ``nid`` if any and is known
        """
        match = [ship for ship in self.ships if ship.nid == nid]
        if match:
            return match.pop()

    def search_planet(self, pid: int) -> Planet:
        """
        Return the planet with ID ``nid`` if any
        """
        match = [planet for planet in self.planets.values()
                 if planet.pid == pid]
        if match:
            return match.pop()

    def get_ships_by_position(self) -> Dict[Tuple[int, int], List[Ship]]:
        """
        Returns a dict with ships ordered by position.
        Ships in the same positions are grouped in a list.
        """
        return dict((
            (position, list(ships))
            for position, ships in groupby(self.ships, lambda s: s.position)))

    def get_ships_in_planets(self) -> List[Tuple[Planet, List[Ship]]]:
        """
        Return a list of tuples ``(planet, ships)`` where ``planet`` is a :class:`Planet`
        instance and ``ships`` is a list with all the ships located on the planet
        """
        ships_by_position = self.get_ships_by_position()
        result = []
        for position, planet in self.planets.items():
            ships = ships_by_position.get(position)
            if not ships:
                continue
            result.append((planet, ships))
        return result

    def get_ships_conflicts(self) -> List[List[Ship]]:
        """
        Return all the ships in conflict: Ships with, at last, one enemy ship
        in the same position
        """
        ships_by_position = [list(ships) for pos, ships in
                             groupby(self.ships, lambda s: s.position)]
        # keep only the groups with more than one player
        return list(
            filter(lambda ships: len({s.player for s in ships if s.player}) > 1,
                   ships_by_position)
        )

    def get_ocuped_planets(self) -> List[Planet]:
        """
        Return all the planets colonized by any race
        """
        return list(filter(lambda p: p.player is not None, self.planets.values()))

    def get_planets_conflicts(self) -> List[Tuple[Planet, List[Ship]]]:
        """
        Return all the planets in conflict: Planets with at least one enemy ship on it
        """
        ships_by_position = self.get_ships_by_position()
        destroyed_ships = [e.ship for e in self.explosions]
        result = []
        for planet in self.get_ocuped_planets():
            ships = ships_by_position.get(planet.position)
            if not ships or not any(s for s in ships
                                    if s.player != planet.player \
                                    and s not in destroyed_ships):
                continue
            result.append((planet, ships))
        return result

    def remove_destroyed_ships(self):
        """
        Remove the destroyed ships from the list
        """
        explosions_ids = [e.ship.nid for e in self.explosions]
        self.ships = list(filter(lambda s: s.nid not in explosions_ids, self.ships))
