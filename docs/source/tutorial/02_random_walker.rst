.. _Tutorial Chapter 02:

Chapter 2 - Han Solo: The Random Walker
========================================

Hello player. Good to see you again.

In this chapter you will learn how to move once for all from your primitive planet and explore the galaxy. Once completed
this tutorial you will be a globetrotter on the galaxy. The Han Solo of the Pythonium universe.

.. warning::
    If you don't know who Han Solo is stop here and come back once you were watched the full `original trilogy of Star Wars <https://en.wikipedia.org/wiki/Star_Wars_Trilogy>`_.



In Pythonium, the ``galaxy`` will be the source of all truth for you. It represents all your owned knowledge about
the universe, and in most cases all the information to develop your strategy will be extracted from the ``galaxy``.

.. note::
    To know more about ``galaxy`` (and ``context``) check :func:`AbstractPlayer.next_turn<pythonium.AbstractPlayer.next_turn>`

First, you need to learn what do you know about the galaxy. To do so we will use ``ipdb``, the ancient oracle of
python code.

This tool allows you to see what's going on with your python code at some point. In our case we want to
know what's going on at the beginning of each turn.

Open the player built in :ref:`Chapter 1<Tutorial Chapter 01>` and set a trace in your ``next_turn`` method. Like this:

.. code-block:: python

   from pyhtonium import AbstractPlayer

   class Player(AbstractPlayer):

       name = 'Han Solo'

       def next_turn(self, galaxy, context):
           import ipdb; ipdb.set_trace()
           return galaxy

Once executed (I'll not tell you how to do that at this point), you will see something similar to:

.. code-block:: python

               8     def next_turn(self, galaxy, context):
               9         import ipdb; ipdb.set_trace()
      ---> 10         return galaxy

      ipdb> _

Now we can start investigating the ``galaxy``.


.. code-block:: python

      ipdb> galaxy
      Galaxy<size=(500, 500), planets=300>


Ok then, this means you are in a galaxy of 500 light-years width and 500 ly height (``size=(500, 500)``) compounded by
300 planets (``planets=300``).

Let's check now what about ``context``.

.. code-block:: bash

      ipdb> type(context)
      <class 'dict'>

      ipdb> context.keys()
      dict_keys(['ship_types', 'tolerable_taxes', 'happypoints_tolerance', 'score', 'turn'])


Here we see that ``context`` is a dictionary with several keys, for now we will focus on the ``score``.


.. code-block:: python

      ipdb> context['score']
      [{'turn': 0, 'player': 'Han Solo', 'planets': 1, 'ships_carrier': 2, 'ships_war': 0, 'total_ships': 2}]


From the score we know:

* The current turn number is ``0``,
* there is only one player called 'Han Solo' (that's you!),
* Han Solo owns,

    * one planet,
    * two carrier ships
    * zero war ships,
    * and two ships in total

Next question, how do we access to your planet and ships?

Give me my things!
------------------

Let's start with your planet. From the score we know you own one planet and two ships, here you will learn how to access
to those things.

At this point you may suspect that this is something to be asked to the ``galaxy``, and you are correct. There are
several methods in ``galaxy`` to answer most of your questions in relation of the state of the game.

In this case we will use :meth:`galaxy.get_player_planets<pythonium.Galaxy.get_player_planets>`, a method that takes
a player name as only parameter and returns all the known planets owned by that player.

.. note::
    In case you didn't noticed yet, you can access to your player's name easily from your ``next_turn`` method with the
    ``self.name`` attribute.

Knowing this, let's store all your planets in a variable named ``my_planets``.

.. code-block:: python

      ipdb> my_planets = galaxy.get_player_planets(self.name)
      ipdb> my_planets
      {(152, 154): Planet<id=14, position=(152, 154), player=Han Solo>}

A set of planets is usually represented as a dictionary where the keys are the planet's position and the value
a :class:`Planet<pythonium.Planet>` instance.

.. note::
    Don't worry if you don't see the exact same values for ``position`` and ``id``, the reason for this is that galaxies
    are randomly generated for each game, so having different values is the normal behavior.


A planet has tons of attributes, for now we will focus just in a few of them:

* ``id`` a unique identifier for the planet,
* ``position`` is the planet position in the galaxy,
* ``player`` is the planet's owner, it can be ``None`` if the planet is not colonized or the owner is unknown for you.

What about your ships?

In a similar fashion, you can use the :meth:`galaxy.get_player_ships<pythonium.Galaxy.get_player_ships>` to get all your ships.

.. code-block:: python

      ipdb> my_ships = galaxy.get_player_ships(self.name)
      ipdb> pp my_ships
      [Ship<id=0, position=(152, 154), player=Han Solo>,
       Ship<id=1, position=(152, 154), player=Han Solo>]

In this case the ships are returned as a list of :class:`Planet<pythonium.Ship>` instances, and those also have a
``position`` and ``player`` indicating the owner of the ship.

Note that the position of both ships is equal to the position of your only planet.

``target``: Where do you want to go?
-------------------------------------

Each ``ship`` instance has a ``target`` attribute indicating where the ship is going. This is one of the control variables
for the ships. You can edit this parameter to order your ships to go into some point in the galaxy.

Let's select one o your ships and see where it is going:

.. code-block:: python

    ipdb> ship = my_ships[0]
    ipdb> print(ship.target)
    None

This mean your ship has no target. Is not going anywhere.

Now let's suppose you want to send your ship 10 ly to the left and 10 ly down the current position.
This is done by setting the ``target`` to the desired position.

``target`` then, in the same way as ``position``, must be a tuple of two integers ``(x, y)``

.. code-block:: python

    ipdb> print(ship.position)
    (91, 102)
    ipdb> ship.target = (ship.position - 10, ship.position - 10)
    ipdb> print(ship.target)
    (81, 92)
