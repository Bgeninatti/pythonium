import attr
from .ship import Ship


@attr.s
class Explosion:
    """
    A ship that has exploded because of a conflict

    Provides some insights about which ship exploded and where

    :param ship: Destroyed ship
    :param ships_involved: Amount of ships involved in the combat
    :param total_attack: Total attack involved in the combat
    """

    ship = attr.ib()
    """
    :class:`Ship` that has been destroyed.
    """

    ships_involved = attr.ib()
    """
    Amount of ships involved in the combat.
    """

    total_attack = attr.ib()
    """
    Total attack involved in the combat.
    """
