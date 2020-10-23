import random

from ..ship import Ship


class Player:
    """
    Move the available ships randomly
    """

    name = 'Walkers'

    def run_turn(self, galaxy, context, t):
        orders = []

        my_ships = galaxy.get_player_ships(self.name)

        for ship in my_ships:
            nearby_planets = galaxy.nearby_planets(ship.position)
            destination = random.choice(nearby_planets)
            ship.target = destination.position

            orders.extend(ship.get_orders())

        return orders
