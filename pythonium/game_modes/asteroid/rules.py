import random

from pythonium.core import Position
from pythonium.game_modes.asteroid.things import Asteroid
from pythonium.rules.core import GalaxyRule


def get_asteroids(galaxy):
    return [a for a in galaxy.things if isinstance(a, Asteroid)]


class DestroyAsteroidsRule(GalaxyRule):

    def execute(self) -> None:
        to_remove = []
        asteroids = get_asteroids(self.galaxy)
        for asteroid in asteroids:
            if asteroid.position[0] > self.galaxy.size[0]:
                to_remove.append(asteroid)
        self.galaxy.things = [
            thing for thing in self.galaxy.things
            if thing not in to_remove
        ]


class DestroyShipRule(GalaxyRule):

    def execute(self) -> None:
        asteroids = get_asteroids(self.galaxy)
        to_destroy = []
        for ship in self.galaxy.ships:
            nearby_asteroids = [
                a for a in asteroids
                if self.galaxy.compute_distance(
                    ship.position,
                    a.position,
                ) < 20
            ]
            if nearby_asteroids:
                to_destroy.append(ship)
        self.galaxy.things = [
            thing for thing in self.galaxy.things
            if thing not in to_destroy
        ]


class CreateAsteroidsRule(GalaxyRule):
    new_asteroid_period = 5

    def execute(self) -> None:
        asteroids = get_asteroids(self.galaxy)
        nominal_asteroids = int(self.galaxy.turn / self.new_asteroid_period)
        real_asteroids = len(asteroids)
        pending_asteroids = nominal_asteroids - real_asteroids
        for _ in range(pending_asteroids):
            self.galaxy.things.append(
                Asteroid(position=self._get_random_position())
            )

    def _get_random_position(self) -> Position:
        return Position((
            self.galaxy.size[0],
            int(random.random() * self.galaxy.size[1])
        ))


class MoveAsteroidsRule(GalaxyRule):

    def execute(self) -> None:
        asteroids = get_asteroids(self.galaxy)
        for asteroid in asteroids:
            new_position = Position((
                asteroid.position[0] - 10,
                asteroid.position[1]
            ))
            asteroid.position = new_position
