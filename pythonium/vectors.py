import attr


@attr.s
class Transfer:
    """
    Represent the transfer of resources from ship
    to planet or vice-versa, or cost of structures.
    This second case can be considered as a transfer between the player
    and the game.
    """

    megacredits: int = attr.ib(converter=int, default=0)
    pythonium: int = attr.ib(converter=int, default=0)
    clans: int = attr.ib(converter=int, default=0)

    def __neg__(self):
        return self.__class__(megacredits=-self.megacredits,
                              clans=-self.clans,
                              pythonium=-self.pythonium)

    def __add__(self, obj):

        if not isinstance(obj, Transfer):
            raise ValueError("Can not sum Transfer class and {}".format(type(obj)))

        return self.__class__(megacredits=self.megacredits + obj.megacredits,
                              clans=self.clans + obj.clans,
                              pythonium=self.pythonium + obj.pythonium)

    def __sub__(self, obj):
        self.__add__(-obj)

    def __mul__(self, factor):

        if not isinstance(factor, (int, float)):
            msg = "Can not apply multiplication to {}".format(type(factor))
            raise ValueError(msg)

        return self.__class__(megacredits=self.megacredits * factor,
                              clans=self.clans * factor,
                              pythonium=self.pythonium * factor)


    def __div__(self, denom):

        if not isinstance(denom, (int, float)):
            msg = "Can not apply division to {}".format(type(denom))
            raise ValueError(msg)

        return self.__class__(self.megacredits / denom,
                              self.clans / denom,
                              self.pythonium / denom)

    def __bool__(self):
        return any([self.clans, self.megacredits, self.pythonium])

    def __repr__(self):
        return f"({self.clans}, {self.megacredits}, {self.pythonium})"


