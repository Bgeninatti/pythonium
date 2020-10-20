import random

from ..ship import Ship


class Player:

    name = 'Rebels'

    def next_turn(self, galaxy, context, t):
        orders = []

        my_ships = galaxy.get_player_ships(self.name)
        my_planets = galaxy.get_player_planets(self.name)

        visited_planets = []

        populated_planets = list(
            filter(lambda p: p.clans > 500, my_planets.values()))

        ships_without_target = [ship for ship in my_ships if not ship.target]

        for ship in my_ships:

            # if len(my_planets) > 100:
                # ship.target = (100, 100)

            # La nave está en un planeta?
            planet = galaxy.planets.get(ship.position)

            # Si no es de nadie y tengo clanes lo colonizo
            if ship.clans and planet and not planet.player:
                ship.transfer = (-100, -50, 0)

            # Tengo clanes?
            if not ship.clans:
                # No. De donde busco?
                # Los puedo sacar del planeta en el que estoy?
                if planet is not None and planet.player == self.name \
                        and planet.clans > 500:
                    ship.transfer = (200, 0, 0)
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
                nearby_turns = 1
                for t in range(int(max(galaxy.size) / context['ship_speed'])):
                    nearby_planets = galaxy.nearby_planets(ship.position, t)
                    unknown_nearby_planets = [p for p in nearby_planets
                                              if not p.player \
                                              and p.pid not in visited_planets]
                    if unknown_nearby_planets:
                        # Me voy a cualquiera de los que encontré para colonizar
                        destination = random.choice(unknown_nearby_planets).position
                        break
                    nearby_turns += 1
                ship.target = destination


            orders.extend(ship.get_orders())

        for planet in my_planets.values():
            planet.taxes = context.get('tolerable_taxes')
            planet.new_mines = planet.can_build_mines()
            # next_ship = Ship.CARRIER if len(my_ships) < 20 else Ship.WAR
            next_ship = Ship.WAR
            if planet.can_build_ship(next_ship):
                planet.new_ship = next_ship

            orders.extend(planet.get_orders())


        return orders
