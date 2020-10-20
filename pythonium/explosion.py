from .ship import Ship


class Explosion:
    """
    A ship that has exploded because of a conflict

    Give some insights about which ship exploded and where
    """

    def __init__(self, ship: Ship, ships_involved: int, total_attack: int):
        """
        :param ship: Destroyed ship
        :type ship: :class:`Ship`
        :param ships_involved: Amount of ships involved in the combat
        :type ships_involved: int
        :param total_attack: Total attack involved in the combat
        :type total_attack: int.
        """
        self.ship = ship
        self.ships_involved = ships_involved
        self.total_attack = total_attack

