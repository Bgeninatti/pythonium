from pythonium import Galaxy, GameMode, Planet, Ship, core


class SandboxGameMode(GameMode):
    def __init__(self, max_ships=500, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
            (234, 10),
        )

        planets = {}
        for position in planets_positions:
            planet = Planet(
                position=core.Position(position),
                temperature=50,
                underground_pythonium=1000,
                concentration=1,
                pythonium=100,
                mine_cost=self.mine_cost,
            )
            planets[position] = planet
        galaxy = Galaxy(map_size, planets, [])

        homeworld = galaxy.planets[(10, 10)]
        homeworld.player = player.name
        homeworld.clans = 1000
        homeworld.pythonium = 1000
        homeworld.megacredits = 1000

        ship_type = self.ship_types.get("carrier")
        ship = Ship(
            player=player.name,
            type=ship_type,
            position=homeworld.position,
            max_cargo=ship_type.max_cargo,
            max_mc=ship_type.max_mc,
            attack=ship_type.attack,
            speed=ship_type.speed,
        )
        galaxy.add_ship(ship)

        return galaxy
