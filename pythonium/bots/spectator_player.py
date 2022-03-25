from ..player import AbstractPlayer


class Player(AbstractPlayer):
    name = "Monitor"

    def step(self, galaxy, context):
        return galaxy
