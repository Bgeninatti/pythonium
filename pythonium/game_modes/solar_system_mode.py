from pythonium import Planet
from pythonium.core import Position
from pythonium.game_modes.classic_mode import ClassicMode


class SolarSystemMode(ClassicMode):


    def build_galaxy(self, name, players):
        sun = Planet(
            position=Position((250, 250)),
            temperature=100,
            underground_pythonium=0,
            concentration=0.0,
            pythonium=0,
            mine_cost=self.mine_cost,
        )
        earth = Planet(
            position=Position((250, 250)),
            temperature=50,
            underground_pythonium=10**6,
            concentration=0.5,
            pythonium=1000,
            mine_cost=self.mine_cost,

        )
