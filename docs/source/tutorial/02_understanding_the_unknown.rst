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
the universe, and in most cases all the information to develop your strategy will be extracted from the ``galaxy``.

First, you need to learn what do you know about the galaxy. To do so we will use ``ipdb``, the ancient oracle of
python code.

This tool allows you to see what's going on with your python code at some point. In our case we want to
know what's going on at the beginning of each turn.

.. note::
    Don't you know `ipdb`? `Check it out <https://github.com/gotcha/ipdb>`_.

Open the player built in :ref:`Chapter 1<Tutorial Chapter 01>` and set a trace in your ``next_turn`` method:

.. code-block:: python

   from pyhtonium import AbstractPlayer

   class Player(AbstractPlayer):

       name = 'Han Solo'

       def next_turn(self, galaxy, context):
           import ipdb; ipdb.set_trace()
           return galaxy

Once executed (if you don't remember how check on :ref:`Executing your player`), you will see something similar to:

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

There are three main galaxy attributes that you must know in deep.

``turn``
~~~~~~~~

Your time reference. The turn that is being played.

.. code-block:: python

      ipdb> galaxy.turn
      0

As expected, the game just began, and you are in turn 0.

To move one turn forward, use the `c` command.

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
      {(1, 360): Planet<id=f346b8cb-1911-438a-bbc1-a3fe3244f0f1, position=(1, 360), player=None>,
       (5, 73): Planet<id=26a1b68d-8ae8-45b7-b431-3fe45fed4907, position=(5, 73), player=None>,
       (6, 84): Planet<id=f6f9b52b-27a4-4801-83e8-360d9cab26de, position=(6, 84), player=None>,
       (8, 215): Planet<id=cce601ba-6056-4b0e-b49e-56afc1409c31, position=(8, 215), player=None>,
      ...
      }

      ipdb> len(galaxy.planets)
      300

.. note::
    In the previous example we use the ``ipdb`` command ``pp``, as an alias for `pprint <https://docs.python.org/3/library/pprint.html>`_.

A planet has tons of attributes, for now we will focus just in a few of them:

* ``id`` a unique identifier for the planet,
* ``position`` is the planet position in the galaxy in (x, y) coordinates,
* ``player`` is the planet's owner, it can be ``None`` if the planet is not colonized or the owner is unknown for you.


``ships``
~~~~~~~~~~

In a similar way as with the planets, the ``galaxy.ships`` attribute is a python list that stores references to every
:class:`Ship<pythonium.Ship>` in the galaxy.

.. code-block::

      ipdb> type(galaxy.ships)
      <class 'list'>

      ipdb> pp galaxy.ships
      [Ship<id=4a14cd55-4169-45dd-ad50-dacaf1da919f, position=(60, 185), player=Han Solo>,
       Ship<id=fda35773-c3c1-4cf7-b382-6ef09af18783, position=(60, 185), player=Han Solo>]

      ipdb> len(galaxy.ships)
      2

The ships, also have ``id``, ``position`` and ``player`` attributes.

From ``galaxy.ships`` output we can tell there are two known ships in the galaxy, and both are yours (notice the ``player=Han Solo``).


Querying to the galaxy
-----------------------

The ``galaxy`` has methods that allows you to filter ``ships`` and ``planets`` based on several criteria.
In this section we will present some receipts to answer common questions that you may have.


Where are my planets?
~~~~~~~~~~~~~~~~~~~~~

By looking carefully into the ``galaxy.planets`` output you will find a planet with ``player=Han Solo``.

That's your planet!

But you may be thinking there should be an easier way to find which planets are yours (if any). And there is: this can be done with the
:func:`Galaxy.get_player_planets<pythonium.Galaxy.get_player_planets>` method.

By passing a player name, this method returns a dictionary similar to ``galaxy.planets``, where the owner is the
player with the name you asked for.

.. code-block:: python

      ipdb> my_planets = galaxy.get_player_planets(self.name)
      ipdb> pp my_planets
      {(111, 93): Planet<id=0a1d661a-56b3-4040-888f-35bd153eddf6, position=(111, 93), player=Han Solo>}


.. note::
    You can access to the name of your :class:`Player<pythonium.AbstractPlayer>` inside your `next_turn` method with
    the `self.name` attribute.

Where are my ships?
~~~~~~~~~~~~~~~~~~~

In a similar fashion than planets, you can find all your ships with the :func:`Galaxy.get_player_ships<pythonium.Galaxy.get_player_ships>` method.

.. code-block:: python

      ipdb> my_ships = galaxy.get_player_ships(self.name)
      ipdb> pp my_ships
      [Ship<id=feb8eb82-9663-4e3e-9f05-e3cffe67e144, position=(111, 93), player=Han Solo>,
       Ship<id=3088bd21-6d62-4ce7-8f88-d63910c4dac5, position=(111, 93), player=Han Solo>]


In single player mode :func:`Galaxy.get_player_ships<pythonium.Galaxy.get_player_ships>` always returns the full ``galaxy.ships``
list, as there are no abandoned ships in pythonium (with ``player=None``).

But in multiplayer mode you can find enemy ships in the ``galaxy.ships`` attribute. In that case, this function can be handy.

Are there ships on my planet orbit?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's suppose you want to transfer some resource from one planet to another, the first thing you want to know is if
there is any ship on the same position of your planet to transfer the resource.

This can be answered with the :func:`Galaxy.get_ships_in_position<pythonium.Galaxy.get_ships_in_position>` method.

When executed with the planet position as parameter, this method returns a list with all the known ships in that position.

In our case, that will be the ``position`` attribute of your planet.

.. code-block:: python

      ipdb>

Is my ship in a planet?
~~~~~~~~~~~~~~~~~~~~~~~~


Final thoughts
--------------


Depending on the strategy that you want to implement for your player, you might find useful one method or another.
That is something you need to discover yourself, but it is good to have an overview
