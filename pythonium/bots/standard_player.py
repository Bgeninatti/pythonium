import random

from ..ship import Ship
from ..player import AbstractPlayer
from ..vectors import TransferVector



class Player(AbstractPlayer):

    name = 'Rebels'

    def next_turn(self, galaxy, context):

        my_ships = galaxy.get_player_ships(self.name)
        my_planets = galaxy.get_player_planets(self.name)

        visited_planets = []

        populated_planets = list(
            filter(lambda p: p.clans > 500, my_planets.values()))

        for ship in my_ships:

            # La nave está en un planeta?
            planet = galaxy.planets.get(ship.position)

            # Si no es de nadie y tengo clanes lo colonizo
            if ship.clans and planet and not planet.player:
                ship.transfer.clans = -100
                ship.transfer.megacredits = -50

            # Tengo clanes?
            if not ship.clans:
                # No. De donde busco?
                # Los puedo sacar del planeta en el que estoy?
                if planet is not None and planet.player == self.name \
                        and planet.clans > 500:
                    ship.transfer.clans = 200
                else:
                    # Entonces voy a buscar en que planeta hay y voy a ir ahí.

                    if not populated_planets:
                        # No encontré. Me quedo donde estoy
                        continue

                    ship.target = populated_planets.pop().position

            # Si.
            # Voy a buscar un planeta que no sea mio para colonizar.
            if not ship.target:
                destination = None
                nearby_planets = galaxy.nearby_planets(ship.position)
                unknown_nearby_planets = [p for p in nearby_planets
                                          if not p.player \
                                          and p.pid not in visited_planets]
                if unknown_nearby_planets:
                    destination = random.choice(unknown_nearby_planets)
                else:
                    destination = random.choice(nearby_planets)

                ship.target = destination.position

        for planet in my_planets.values():
            planet.taxes = context.get('tolerable_taxes')
            planet.new_mines = planet.can_build_mines()
            next_ship = context['ship_types']['war']
            if planet.can_build_ship(next_ship):
                planet.new_ship = next_ship

        return galaxy
