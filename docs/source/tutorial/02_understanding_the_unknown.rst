.. _Tutorial Chapter 02:

Chapter 2 - Understanding the unknown
======================================

Hello human. Good to see you again.

I understand that having you reading this is an expression of the desire of knowing more about
the universe around you, and eventually leave your planet.

The next step is to know more about the galaxy. How many planets are? How far are they from you?
Do you have starships? How can you use them?

Keep reading, and all your questions will be answered.

The galaxy, an introduction
----------------------------

In Pythonium, the ``galaxy`` is the source of all truth for you. It represents all your owned knowledge about
the universe, and in most cases, all the information to develop your strategy will be extracted from the ``galaxy``.

First, you need to learn what do you know about the galaxy. To do so we will use ``ipdb``, the ancient oracle of
python code.

This tool allows you to see what's going on with your python code at some point. In our case, we want to
know what's going on at the beginning of each turn.

.. note::
    Don't you know `ipdb`? `Check it out <https://github.com/gotcha/ipdb>`_.

Open the player you built in :ref:`Chapter 1<Tutorial Chapter 01>` and set a trace in your ``next_turn`` method:

.. code-block:: python

    from pyhtonium import AbstractPlayer

    class Player(AbstractPlayer):

        name = 'Han Solo'

        def next_turn(self, galaxy, context):
            import ipdb; ipdb.set_trace()
            return galaxy

Once executed you will see something similar to:

.. code-block:: python

             8     def next_turn(self, galaxy, context):
             9         import ipdb; ipdb.set_trace()
    ---> 10         return galaxy

    ipdb> _

.. note::
    If you don't remember how to do execute your player check on :ref:`Executing your player`

Now we can start investigating the ``galaxy``.

.. code-block:: python

    ipdb> galaxy
    Galaxy(size=(500, 500), planets=300)


Ok then, this means you are in a galaxy of 500 light-years width and 500 ly height (``size=(500, 500)``) compounded by
300 planets (``planets=300``).

There are three main galaxy attributes that you must know in deep.

``turn``
~~~~~~~~

Your time reference. The turn that is being played.

.. code-block:: python

    ipdb> galaxy.turn
    0

As expected, the game just began, and you are in turn 0.

To move one turn forward, use the ``c`` command.

.. code-block:: python

    ipdb> c

             8     def next_turn(self, galaxy, context):
             9         import ipdb; ipdb.set_trace()
    ---> 10         return galaxy

    ipdb> galaxy.turn
    1

.. note::
    And as you may suspect, there is no way to come back in time. Time always moves forward.

``planets``
~~~~~~~~~~~~

This attribute stores the state of all the planets in the galaxy.

``galaxy.planets`` is a python dictionary where the keys are planet's :class:`Position<pythonium.core.Position>`,
and the values are :class:`Planet<pythonium.Planet>` instances.

.. code-block::

    ipdb> type(galaxy.planets)
    <class 'dict'>

    ipdb> pp galaxy.planets
    {(1, 360): Planet(id=f346b8cb-1911-438a-bbc1-a3fe3244f0f1, position=(1, 360), player=None),
     (5, 73): Planet(id=26a1b68d-8ae8-45b7-b431-3fe45fed4907, position=(5, 73), player=None),
     (6, 84): Planet(id=f6f9b52b-27a4-4801-83e8-360d9cab26de, position=(6, 84), player=None),
     (8, 215): Planet(id=cce601ba-6056-4b0e-b49e-56afc1409c31, position=(8, 215), player=None),
    ...
    }

    ipdb> len(galaxy.planets)
    300

.. note::
    In the previous example, we use the ``ipdb`` command ``pp``, as an alias for `pprint <https://docs.python.org/3/library/pprint.html>`_.

A planet has tons of attributes, for now we will focus just in a few of them:

* ``id`` a unique identifier for the planet,
* ``position`` is the planet position in the galaxy in (x, y) coordinates,
* ``player`` is the planet's owner, it can be ``None`` if the planet is not colonized or the owner is unknown to you.


``ships``
~~~~~~~~~~

In a similar way as with the planets, the ``galaxy.ships`` attribute is a python list that stores references to every
:class:`Ship<pythonium.Ship>` in the galaxy.

.. code-block::

    ipdb> type(galaxy.ships)
    <class 'list'>

    ipdb> pp galaxy.ships
    [Ship(id=4a14cd55-4169-45dd-ad50-dacaf1da919f, position=(60, 185), player=Han Solo),
     Ship(id=fda35773-c3c1-4cf7-b382-6ef09af18783, position=(60, 185), player=Han Solo)]

    ipdb> len(galaxy.ships)
    2

The ships, also have ``id``, ``position``, and ``player`` attributes.

From ``galaxy.ships`` output we can tell there are two known ships in the galaxy, and both are yours (notice the ``player=Han Solo``).


Querying to the galaxy
-----------------------

The ``galaxy`` has methods that allow you to filter ``ships`` and ``planets`` based on several criteria.
In this section, we will present some receipts to answer common questions that you may have.


Where are my planets?
~~~~~~~~~~~~~~~~~~~~~

By looking carefully into the ``galaxy.planets`` output you will find a planet with ``player=Han Solo``.

That's your planet!

But you may be thinking there should be an easier way to find which planets are yours (if any). And there is: this can be done with the
:func:`Galaxy.get_player_planets<pythonium.Galaxy.get_player_planets>` method.

This method takes a player name as attribute and returns an iterable with all the planets where the owner is the player with the
name you asked for.

.. code-block:: python

    ipdb> my_planets = galaxy.get_player_planets(self.name)
    ipdb> pp list(my_planets)
    [Planet(id=0a1d661a-56b3-4040-888f-35bd153eddf6, position=(111, 93), player=Han Solo)]


.. note::
    You can access to the name of your :class:`Player<pythonium.AbstractPlayer>` inside your ``next_turn`` method with
    the ``self.name`` attribute.

Where are my ships?
~~~~~~~~~~~~~~~~~~~

In a similar fashion to planets, you can find all your ships with the :func:`Galaxy.get_player_ships<pythonium.Galaxy.get_player_ships>` method.

.. code-block:: python

    ipdb> my_ships = galaxy.get_player_ships(self.name)
    ipdb> pp list(my_ships)
    [Ship(id=feb8eb82-9663-4e3e-9f05-e3cffe67e144, position=(111, 93), player=Han Solo),
     Ship(id=3088bd21-6d62-4ce7-8f88-d63910c4dac5, position=(111, 93), player=Han Solo)]


In single-player mode :func:`Galaxy.get_player_ships<pythonium.Galaxy.get_player_ships>` always returns all the ships in
``galaxy.ships``, as there are no abandoned ships in pythonium (with ``player=None``).

But in multiplayer mode, you can also find enemy ships in the ``galaxy.ships`` attribute. In that case, this function can
be handy to get only your ships, or the visible enemy ships.

Are there ships on my planet orbit?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s suppose you want to transfer some resource from one planet to another, the first thing you want to know is if
there is any ship in the same position as your planet, to use this ship to transfer the resource.

This can be answered with the :func:`Galaxy.get_ships_in_position<pythonium.Galaxy.get_ships_in_position>` method.

This method takes a position as parameter and returns an iterable with all the known ships in that position.

In our case, that will be the ``position`` attribute of your planet.

.. code-block:: python

    ipdb> my_planets = galaxy.get_player_planets(self.name)
    ipdb> some_planet = next(my_planets)
    ipdb> some_planet
    Planet(id=4bd4d574-e4c9-459d-9da2-72802ca91ea2, position=(81, 184), player=Han Solo)

    ipdb> ships_in_planet = galaxy.get_ships_in_position(some_planet.position)
    ipdb> pp list(ships_in_planet)
    [Ship(id=d5bb02cd-eeb5-4e1e-a93f-028773443b25, position=(81, 184), player=Han Solo),
     Ship(id=2a98e5bf-b5bd-4f97-8884-d83577df85c2, position=(81, 184), player=Han Solo)]


Is my ship in a planet?
~~~~~~~~~~~~~~~~~~~~~~~~

Now think the opposite example, you have a ship and you want to know if it is located on a planet or in deep space.

This can be answered by simply searching if there is planets in the ship's position.

.. code-block:: python

    ipdb> my_ships = galaxy.get_player_ships(self.name)
    ipdb> some_ship = next(my_ships)
    ipdb> some_ship
    Ship(id=d5bb02cd-eeb5-4e1e-a93f-028773443b25, position=(81, 184), player=Han Solo)

    ipdb> planet = galaxy.planets.get(some_ship.position)
    ipdb> planet
    Planet(id=63fa8f87-9fa6-40da-a744-5b8b23a9d538, position=(157, 10), player=Han Solo)


Turn ``context``
----------------

Apart from ``galaxy`` there is a second argument received by the ``Player.next_turn`` method: the turn ``context``.

The ``context`` contains additional metadata about the turn and the overall game.

.. code-block::

    ipdb> type(context)
    <class 'dict'>

    ipdb> context.keys()
    dict_keys(['ship_types', 'tolerable_taxes', 'happypoints_tolerance', 'score'])


Here we see that ``context`` is a dictionary with several keys. For now, we will focus on the ``score``.


.. code-block:: python

    ipdb> context['score']
    [{'turn': 1, 'player': 'Han Solo', 'planets': 1, 'ships_carrier': 2, 'ships_war': 0, 'total_ships': 2}]


From the score we know:

* The current turn number is ``1``,
* there is only one player called 'Han Solo' (that's you!),
* Han Solo owns,

    * one planet,
    * two carrier ships
    * zero warships,
    * and two ships in total

This is, in fact, consistent with the found results in previous sections. When you query your owned planets, the result
was one single planet, and for your ships, the result was two ships.

You can verify that both ships are carriers by doing

.. code-block:: python

    ipdb> for ship in my_ships:
        print(ship.type.name)

    carrier
    carrier

In the next chapters, we will explore a bit more about the ``context``, different ship types, and their attributes.

.. _exit the debugger:

How to exit from the `ipdb` debugger
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pythonium has a special command for exit the ``ipdb``. You will notice that the usual ``exit`` command
will not work in this case. Exiting from the infinite loop of time is a bit more complex.

If you want to exit the debugger do:

.. code-block:: python

    ipdb> from pythonium.debugger import terminate
    ipdb> terminate()


Final thoughts
--------------

In this chapter, we explained how to access the different objects from the galaxy, with a focus on those objects owned by your player.
Depending on the complexity of the player that you want to implement, you might find useful one method or another.
That is something you need to discover yourself, but it is good to have an overview.

You can also implement your own query methods for ``galaxy.planets`` and ``galaxy.ships`` depending on your needs.
For starters space explorers, the methods presented in this section should be enough for most cases.

In the next chapter, you will learn how to move your ships.

Keep moving human, the battle for pythonium is waiting for you.
