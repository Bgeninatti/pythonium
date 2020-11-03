import attr

@attr.s
class CostVector:
    """
    Represents the cost of some planet structure or ship
    """
    megacredits: int = attr.ib(converter=int, default=0)
    pythonium: int = attr.ib(converter=int, default=0)

@attr.s
class TransferVector:
    """
    Represent the transfer of resources from ship
    to planet or vice-versa.
    """

    megacredits: int = attr.ib(converter=int, default=0)
    pythonium: int = attr.ib(converter=int, default=0)
    clans: int = attr.ib(converter=int, default=0)

    def __bool__(self):
        return abs(self.megacredits + self.pythonium + self.clans) > 0


