

from pythonium import Ship, Planet, Galaxy, GameMode


class SandboxGameMode(GameMode):

    def build_galaxy(self, players):

        if len(players) != 1:
            raise ValueError("SandboxGameMode only allows one player")

        player = players.pop()
        map_size = (244, 244)
        planets_positions = (
            (10, 10),
            (66, 66),
            (122, 122),
            (178, 178),
            (234, 234),
            (10, 234),
            (66, 178),
            (178, 66),
            (234, 10)
        )

        planets = {}
        for i, position in enumerate(planets_positions):
            planet = Planet(i+1, position, 50, 1000, 1, 100)
            planets[position] = planet
        galaxy = Galaxy(map_size, planets, [])

        homeworld = galaxy.planets[(10, 10)]
        homeworld.player = player.jid
        homeworld.clans = 1000
        homeworld.pythonium = 1000
        homeworld.megacredits = 1000

        ship_features = Ship.get_type(Ship.CARRIER)
        ship = Ship(player.jid,
                    Ship.CARRIER,
                    homeworld.position,
                    *ship_features)
        galaxy.add_ship(ship)

        return galaxy
