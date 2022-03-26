from pythonium import ShipType, Transfer, Ship, Galaxy
from pythonium.core import Position
from pythonium.game_modes.classic_mode import ClassicMode
from pythonium.game_modes.asteroid.rules import get_asteroids, DestroyAsteroidsRule, DestroyShipRule, \
    CreateAsteroidsRule, MoveAsteroidsRule
from pythonium.rules.ship import ShipMoveRule

SHIP_SPEED = 5
SHIP_TYPE = ShipType(
    name='traveler',
    speed=SHIP_SPEED,
    cost=Transfer(),
    max_cargo=0,
    max_mc=0,
    attack=0,
)


class AsteroidsMode(ClassicMode):
    ship_speed = SHIP_SPEED
    ship_type = SHIP_TYPE
    rules = [
        DestroyAsteroidsRule,
        CreateAsteroidsRule,
        ShipMoveRule,
        MoveAsteroidsRule,
        DestroyShipRule,
    ]

    def __init__(self, max_turn=300, *args, **kwargs):
        super().__init__(
            max_turn=max_turn,
            *args,
            **kwargs
        )

    def build_galaxy(self, name, players):
        ships = []
        ship_position = (self.map_size[0] / 2, self.map_size[1])
        for player in players:
            ship = Ship(
                player=player.name,
                type=self.ship_type,
                position=Position(ship_position),
                max_cargo=self.ship_type.max_cargo,
                max_mc=self.ship_type.max_mc,
                attack=self.ship_type.attack,
                speed=self.ship_type.speed,
            )
            ships.append(ship)
        return Galaxy(name=name, size=self.map_size, things=ships)

    def has_ended(self, galaxy, t):
        if t == self.max_turn:
            return True

        if not galaxy.known_races:
            return True

        return False

    def galaxy_for_player(self, galaxy, player):
        return galaxy

    def get_context(self, galaxy, players, turn):
        asteroids = get_asteroids(galaxy)
        return {
            'asteroids': len(asteroids),
            'score': [
                {'ships': 1}
                for _ in galaxy.known_races
            ]
        }
