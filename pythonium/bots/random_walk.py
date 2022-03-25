import random

from ..player import AbstractPlayer


class Player(AbstractPlayer):
    """
    Move the available ships randomly
    """

    name = "Walkers"

    def step(self, galaxy, context):

        my_ships = galaxy.get_player_ships(self.name)

        for ship in my_ships:
            nearby_planets = galaxy.nearby_planets(ship.position, ship.speed)
            destination = random.choice(nearby_planets)
            ship.target = destination.position

        return galaxy
