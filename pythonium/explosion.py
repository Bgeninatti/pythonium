from .ship import Ship


# TODO: Use attrs in this class
class Explosion:
    """
    A ship that has exploded because of a conflict

    Provides some insights about which ship exploded and where

    :param ship: Destroyed ship
    :param ships_involved: Amount of ships involved in the combat
    :param total_attack: Total attack involved in the combat
    """

    def __init__(self, ship: Ship, ships_involved: int, total_attack: int):
        self.ship = ship
        """
        :class:`Ship` that has been destroyed.
        """

        self.ships_involved = ships_involved
        """
        Amount of ships involved in the combat.
        """

        self.total_attack = total_attack
        """
        Total attack involved in the combat.
        """
