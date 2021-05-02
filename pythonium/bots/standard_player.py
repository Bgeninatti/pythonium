import random

import attr

from ..player import AbstractPlayer
from ..ship import Ship
from ..vectors import Transfer


class Player(AbstractPlayer):

    name = "Solar Fed."
    colonization_transfer = Transfer(clans=50, megacredits=100)
    colonization_carrier_autonomy = 5
    colonization_refill_transfer = (
        colonization_transfer * colonization_carrier_autonomy
    )
    populated_planet_exigency = 20
    populated_planet_threshold = (
        colonization_transfer * populated_planet_exigency
    )
    tenacity = 0.5

    def next_turn(self, galaxy, context):

        my_ships = galaxy.get_player_ships(self.name)
        my_planets = galaxy.get_player_planets(self.name)

        visited_planets = []

        populated_planets = list(
            filter(
                lambda p: p.clans > self.populated_planet_threshold.clans,
                my_planets.values(),
            )
        )

        for ship in my_ships:

            # La nave está en un planeta?
            planet = galaxy.planets.get(ship.position)

            # Si no es de nadie y tengo clanes lo colonizo
            if ship.clans and planet and not planet.player:
                ship.transfer = -self.colonization_transfer

            # Tengo clanes?
            if not ship.clans:
                # No. De donde busco?
                # Los puedo sacar del planeta en el que estoy?
                if planet in populated_planets:
                    ship.transfer = self.colonization_refill_transfer
                elif populated_planets:
                    # Voy a cualquier planeta del que pueda sacar recursos
                    target_planet = populated_planets.pop()
                    ship.target = target_planet.position
                else:
                    pass

            # Si.
            # Voy a buscar un planeta que no sea mio para colonizar.
            if not ship.target:
                destination = None
                nearby_planets = galaxy.nearby_planets(ship.position)
                unknown_nearby_planets = [
                    p
                    for p in nearby_planets
                    if not p.player and p.id not in visited_planets
                ]
                if unknown_nearby_planets:
                    destination = random.choice(unknown_nearby_planets)
                else:
                    destination = random.choice(nearby_planets)

                ship.target = destination.position

        for planet in my_planets.values():
            planet.taxes = context.get("tolerable_taxes")
            planet.new_mines = planet.can_build_mines()

            if random.random() > self.tenacity:
                next_ship = context["ship_types"]["carrier"]
            else:
                next_ship = context["ship_types"]["war"]

            if planet.can_build_ship(next_ship):
                planet.new_ship = next_ship

        return galaxy
