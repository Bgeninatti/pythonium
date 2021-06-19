import attr

from .galaxy import Galaxy


@attr.s
class AbstractPlayer:

    name: str = attr.ib(init=False)
    """
    Player's name. Please make it short (less than 12 characters), or you will break the
    gif and reports.
    """

    def next_turn(self, galaxy: Galaxy, context: dict) -> Galaxy:
        """
        Compute the player strategy based on the available information in the ``galaxy``
        and ``context``.

        :param galaxy: The state of the Galaxy known by the player.
        :param context: Aditional information about the game.

        Each player sees a different part of the galaxy, and the ``galaxy`` \
        known by every player is different.

        A galaxy contains:

          * All his ships and planets,
          * All the enemy ships in any of his planets,
          * All the enemy ships located in the same position as any of his ships,
          * All the attributes of a planet that has no owner if a player's ship is \
            on the planet,
          * The position of all the planets (not the rest of its attributes),
          * All the explosions that occur in the current turn.

        The player won't know the attributes of enemy ships or planets but the position.

        ``context`` has the following keys:

          * ``ship_types``: A dictionary with all the ship types that the player can \
            build. See: :class:`ShipType`
          * ``tolerable_taxes``: The level of taxes from where ``happypoints`` start \
            to decay.
          * ``happypoints_tolerance``: The level of happypoints from where \
          * ``score``: A list with the score for each player.
          * ``turn``: Number of the current turn.
        """
        raise NotImplementedError(
            "You must implement the ``next_turn`` method in your ``Player`` class"
        )
