from pythonium import Galaxy
from pythonium.core import Position
from pythonium.player import AbstractPlayer


class Player(AbstractPlayer):
    name = 'explorer'

    def next_turn(self, galaxy: Galaxy, context: dict) -> Galaxy:
        ships = galaxy.get_player_ships(self.name)

        for ship in ships:
            ship.target = Position((
                ship.position[0],
                0,
            ))

        return galaxy
