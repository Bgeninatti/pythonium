import attr

@attr.s
class AbstractPlayer:

    name: str = attr.ib(init=False)
    color: str = attr.ib(init=False)

    def next_turn(self, galaxy, context):
        raise NotImplementedError(
            "You must implement the `next_turn` method in your `Player` class")
