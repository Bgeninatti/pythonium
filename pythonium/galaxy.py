from itertools import groupby

import numpy as np

from . import cfg


class Galaxy:

    def __init__(self, size: tuple, planets: dict, ships: list, explosions=None):
        """
        Galaxy de planets.

        Representa mapa del juego.

        :param size: Galaxy height and width
        :type size: tuple(int, int)
        :param planets: Planets that compound the galaxy
        :type planets: dict where the key is a tuple witht he planet position
        :param ships: Ships in the galaxy
        :type ships: list of :class:`Ship`
        """
        self.size = size
        self.planets = planets
        self.ships = ships
        self.explosions = [] if not explosions else explosions
        self._next_ship_id = max(s.nid for s in ships) + 1 if ships else 0

    @property
    def known_races(self):
        return {s.player for s in self.ships} \
            .union({p.player for p in self.planets.values() if p.player is not None})

    @staticmethod
    def compute_distance(a, b):
        return np.linalg.norm(np.array(a) - np.array(b))

    def add_ship(self, ship):
        ship.nid = self._next_ship_id
        self.ships.append(ship)
        self._next_ship_id += 1


    def distances_to_planets(self, point):
        """
        Return a dict where the keys are the position of each planet and the
        values are the distance to those planets.
        """
        return dict(
            ((p, self.compute_distance(p, point)) for p in self.planets.keys())
        )

    def nearby_planets(self, point, turns=1):
        """
        Return the closest planet to `point`
        """
        distances = self.distances_to_planets(point)
        return list(
            filter(lambda p: distances[p.position] <= cfg.ship_speed*turns,
                   self.planets.values())
        )

    def get_player_planets(self, player_name):
        """
        Return a dict with all the known planets that belong to the player
        with name ``player_name``
        """
        return dict(
            ((pos, p) for pos, p in self.planets.items() if p.player == player_name)
        )

    def get_player_ships(self, player_name):
        """
        Return a list with all the known ships that belong to the player
        with name ``player_name``
        """
        return [ship for ship in self.ships if player_name == ship.player]

    def get_ships_in_deep_space(self):
        """
        Return a list with all the ships that are not located in a planet
        """
        positions = {n.position for n in self.ships} \
            .difference(set(self.planets.keys()))
        return [n for n in self.ships if n.position in positions]

    def get_ships_in_position(self, position):
        """
        Return a list with all the known ships in the given position
        """
        return list(filter(lambda s: s.position == position, self.ships))

    def search_ship(self, nid):
        """
        Return the ship with ID ``nid`` if any
        """
        match = [ship for ship in self.ships if ship.nid == nid]
        if match:
            return match.pop()

    def search_planet(self, pid):
        """
        Return the planet with ID ``nid`` if any
        """
        match = [planet for planet in self.planets.values()
                 if planet.pid == pid]
        if match:
            return match.pop()

    def get_ships_by_position(self):
        """
        Returns a dict with ships ordered by position. As in ``planets``, the keys are
        tuples of positions. Values are list of ships in the given position.
        """
        return dict((
            (position, list(ships))
            for position, ships in groupby(self.ships, lambda s: s.position)))

    def get_ships_in_planets(self):
        """
        Return a list of tuples ``(planet, ships)`` where ``planet`` is a :class:`Planet`
        instance and ``ships`` is a list with all the ships located in the planet
        """
        ships_by_position = self.get_ships_by_position()
        result = []
        for position, planet in self.planets.items():
            ships = ships_by_position.get(position)
            if not ships:
                continue
            result.append((planet, ships))
        return result

    def get_ships_conflicts(self):
        """
        Return all the ships in conflict: Ships whith at last one enemy ship
        in the same position
        """
        ships_by_position = [list(ships) for pos, ships in
                             groupby(self.ships, lambda s: s.position)]
        # keep only the groups with more than one player
        return list(
            filter(lambda ships: len({s.player for s in ships if s.player}) > 1,
                   ships_by_position)
        )

    def get_ocuped_planets(self):
        """
        Return all the planets colonized by any race
        """
        return list(filter(lambda p: p.player is not None, self.planets.values()))

    def get_planets_conflicts(self):
        """
        Return all the planets in conflict: Planets with at least one enemy ship on it
        """
        ships_by_position = self.get_ships_by_position()
        destroyed_ships = [e.ship for e in self.explosions]
        result = []
        for position, planet in self.planets.items():
            ships = ships_by_position.get(position)
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
