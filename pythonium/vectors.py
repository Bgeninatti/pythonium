import attr


@attr.s
class Transfer:
    """
    Represent the transfer of resources from a ship
    to a planet and vice-versa, or the cost of structures.
    This second case can be considered as a transfer between the player
    and the game.

    Some useful properties of this class are:

    **Negation**

    Changes the direction of the transfer.

    >>> t = Transfer(clans=100, megacredits=100, pythonium=100)
    >>> print(-t)
    Transfer(megacredits=-100, pythonium=-100, clans=-100)

    **Addition and Subtraction**

    Add/subtracts two transfers

    >>> t1 = Transfer(clans=100, megacredits=100, pythonium=100)
    >>> t2 = Transfer(clans=10, megacredits=10, pythonium=10)
    >>> print(t1 + t2)
    Transfer(megacredits=110, pythonium=110, clans=110)

    **Multiplication and Division**

    Multiplies/divides a transfer with an scalar

    >>> t = Transfer(clans=100, megacredits=100, pythonium=100)
    >>> print(t*1.5)
    Transfer(megacredits=150, pythonium=150, clans=150)
    >>> print(t/1.5)
    Transfer(megacredits=150, pythonium=150, clans=150)

    **Empty transfers**

    The conversion of a transfer to a boolean return ``False`` if the transfer is empty

    >>> t = Transfer()
    >>> print(bool(t))
    False

    """

    megacredits: int = attr.ib(converter=int, default=0)
    """
    Amount of megacredits to transfer
    """

    pythonium: int = attr.ib(converter=int, default=0)
    """
    Amount of pythonium to transfer
    """

    clans: int = attr.ib(converter=int, default=0)
    """
    Amount of clans to transfer
    """


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


    def __truediv__(self, denom):

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


