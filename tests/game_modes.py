

from pythonium import Ship, Planet, Galaxy, GameMode


class SandboxGameMode(GameMode):

    def __init__(self, max_ships=500):
        self.max_ships = max_ships

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
            planet = Planet(pid=i+1,
                            position=position,
                            temperature=50,
                            underground_pythonium=1000,
                            concentration=1,
                            pythonium=100)
            planets[position] = planet
        galaxy = Galaxy(map_size, planets, [])

        homeworld = galaxy.planets[(10, 10)]
        homeworld.player = player.name
        homeworld.clans = 1000
        homeworld.pythonium = 1000
        homeworld.megacredits = 1000

        ship_features = Ship.get_type(Ship.CARRIER)
        ship = Ship(player=player.name,
                    type=Ship.CARRIER,
                    position=homeworld.position,
                    max_cargo=ship_features[0],
                    max_mc=ship_features[1],
                    attack=ship_features[2])
        galaxy.add_ship(ship)

        return galaxy
