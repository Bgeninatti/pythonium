.. _Tutorial Chapter 03:

Chapter 3 - Han Solo: The Random Walker
========================================

Hi human. Glad to see you here. I thought you were lost in some capitalist leisure streaming service.

In this chapter, you will learn how to move once for all from your primitive planet and explore the galaxy. Once completed
this tutorial you will be a globetrotter on the galaxy. The Han Solo of the Pythonium universe.

.. warning::
    If you don't know who Han Solo is stop here and come back once you were watched the full `original trilogy of Star Wars <https://en.wikipedia.org/wiki/Star_Wars_Trilogy>`_.

``target``: Where do you want to go?
-------------------------------------

Each ``ship`` has a ``target`` attribute indicating where the ship is going. This is one of the control variables
for your ships. You can edit this parameter to order your ships to go to some specific point in the galaxy.

Start the ``ipdb`` debugger as you learned in :ref:`Chapter 2<Tutorial Chapter 02>`, and select some random ship to be
your explorer:

.. code-block:: python

    ipdb> my_ships = galaxy.get_player_ships(self.name) # Find all your ships
    ipdb> explorer_ship = next(my_ships) # Select the first ship


Now let's see where the explorer ship is going:

.. code-block:: python

    ipdb> print(explorer_ship.target)
    None

This means the ship has no target. In the next turn, it will be in the same position.

You can verify it easily.

.. code-block:: python

    ipdb> galaxy.turn # Check the current turn
    0
    ipdb> explorer_ship.position # Check the ship's position
    (43, 37)
    ipdb> c # Move one turn forward
    ...
    ipdb> galaxy.turn # Now you are in turn 1
    1
    ipdb> my_ships = galaxy.get_player_ships(self.name) # Find the explorer ship again
    ipdb> explorer_ship = next(my_ships)
    ipdb> explorer_ship.position # The ship position is the same as previous turn
    (43, 37)

The ship stays in the same position when time moves forward. It is not going anywhere.

.. note::
    Note that when you move one turn forward ``ipbb`` do not save the variables declared in the previous turn.
    That's why we need to search the ``explorer_ship`` again.

Knowing the neighborhood
-------------------------

The next step is to find a destination for the ``explorer_ship``

For sure you want to visit one of the many unknown planets around you (those with ``player=None``), and possibly you don't
want to travel for all eternity. We need to find some unknown planet near yours to arrive fast. The ship should arrive
by the next turn.

But wait a minute, how fast the ``explorer_ship`` moves?

Every ship has a ``speed`` attribute indicating how many light-years can travel in a single turn.

.. code-block:: python

    ipdb> explorer_ship.speed
    80

Based on this we can say the ship can travel up to 80ly in a single turn. The next step is to find an unknown planet that is 80ly or
less from your planet.

The :func:`Galaxy.nearby_planets<pythonium.Galaxy.nearby_planets>` method allows you to find all the planets that are
up to a certain distance away (or less) from a specific position. This method takes a ``position`` and a distance
(called ``neighborhood``) and returns a list with all the nearby planets around that position.

In our case, the neighborhood will be 80ly, the distance the ship can travel in one turn, and the position will be the
ship location.

.. code-block:: python

    ipdb> neighborhood = galaxy.nearby_planets(explorer_ship.position, explorer_ship.speed)
    ipdb> pp neighborhood
    [Planet(id=7d9321ab-57cb-4a05-afaa-c2f4ef8e4627, position=(43, 37), player=Han Solo),
     Planet(id=a374a560-ba94-43b1-87b0-78eca8ca5b97, position=(25, 41), player=None),
     Planet(id=e3319ed0-24ec-491c-bb76-a418d9b8b508, position=(112, 50), player=None),
     Planet(id=1b7d714e-22d2-4ca2-826a-bf0656138793, position=(115, 9), player=None),
     Planet(id=70279963-541b-49c9-bb87-32cf6936f45f, position=(31, 42), player=None),
     Planet(id=73f25d86-44f1-4cfc-a8ac-44a96affa1d9, position=(9, 21), player=None),
     Planet(id=1c7ec1c3-7aea-44bf-b582-1f7e3cb3b7ec, position=(81, 27), player=None),
     Planet(id=1378a7ab-2120-46d3-ac93-fc50632141b0, position=(96, 62), player=None),
     Planet(id=fb0d019d-ca71-4353-a06c-d3b4898ffd82, position=(93, 44), player=None),
     Planet(id=02539d23-2911-4354-81f5-9a1f83ef0936, position=(21, 86), player=None),
     Planet(id=38ce324b-ce2a-4bf1-997c-bb8990ae7509, position=(67, 37), player=None),
     Planet(id=4e19fda6-ac81-4d85-bdde-bd7244430a2e, position=(70, 33), player=None),
     Planet(id=e2234771-dbeb-425f-9b0a-1e761f5cf3e1, position=(44, 18), player=None),
     Planet(id=b5b025dd-dfcf-4ca5-8b03-67bb3a04479f, position=(30, 92), player=None),
     Planet(id=4b29c3d8-3c2f-4b33-8ca7-f451eb269e21, position=(61, 110), player=None),
     Planet(id=72b77b24-0063-42f1-aeb0-259f04125cbd, position=(67, 71), player=None),
     Planet(id=bf00cfa3-aece-48e6-8d67-11b3797e2f2c, position=(42, 69), player=None),
     Planet(id=43bcb3bb-b788-46e9-b425-8539caeff03c, position=(89, 64), player=None),
     Planet(id=0a9f5a40-034e-4fe8-a6b1-83f3437e09c8, position=(109, 54), player=None),
     Planet(id=a51d8923-1003-4357-bb2b-f3efa7d5023e, position=(17, 35), player=None),
     Planet(id=da112184-1e01-41ee-b146-d073946ce41e, position=(32, 81), player=None),
     Planet(id=765a19df-2639-4efd-8aa6-30ff3926039c, position=(75, 40), player=None),
     Planet(id=40052c15-3ffa-4dfa-ad22-9afbd0a16091, position=(95, 57), player=None)]

Cool, right?

All those planets are one turn away the ``explorer_ship``. Notice that your planet is included in the neighborhood (because your ship is located in it and
the distance to it is zero).

Traveling
----------

Now let's select the target for the ship. For now, keep it simple: pic some random unknown planet from the list.

.. code-block:: python

    ipdb> unknown_nearby_planets = [p for p in neighborhood if p.player is None]
    ipdb> import random
    ipdb> target_planet = random.choice(unknown_nearby_planets)
    ipdb> target_planet
    Planet(id=1b7d714e-22d2-4ca2-826a-bf0656138793, position=(115, 9), player=None)

That's your ship first destination. An unknown planet one turn away from your ship's location.

The next step is set the ship's ``target`` as the planet's ``position`` and move one turn forward.

.. code-block:: python

    ipdb> galaxy.turn # Check the current turn
    1
    ipdb> explorer_ship.position # Check the ship position
    (43, 37)
    ipdb> explorer_ship.target = target_planet.position # set the ship target
    ipdb> c # move one turn forward

Where is the ship now?

.. code-block:: python

    ipdb> galaxy.turn # you are one turn ahead
    2
    ipdb> my_ships = galaxy.get_player_ships(self.name) # Find all your ships
    ipdb> explorer_ship = next(my_ships) # And keep the explorer ship
    ipdb> explorer_ship.position # Check the ship position
    (115, 9)
    ipdb> explored_planet = galaxy.planets.get(explorer_ship.position) # Find the planet in the ship's position
    ipdb> explored_planet
    Planet(id=1b7d714e-22d2-4ca2-826a-bf0656138793, position=(115, 9), player=None)

Your explorer ship just arrived at the target planet. A new and unknown rock in the middle of the space with a lot of
things to learn about and explore.

Congratulations human. You did it. You left the pathetic rock where you spent your whole life, and now you are in a
different one. Probably more pathetic, probably more boring, maybe you don't even have air to breathe or food to eat.
But hey... you are a space traveler.


Putting the pieces together
----------------------------

In this chapter, we explained how to move your ships. You learned the first, and most basic command: Ship movement.

But we also developed a strategy. I call it "The Random Walker Strategy": A group of ships moving around, exploring
planets without much more to do but travel around the galaxy.

Let's :ref:`exit the debugger<exit the debugger>`, edit your player class, and apply the random walker strategy to all your ships.

You will end up with something like this:

.. code-block:: python

    import random
    from pythonium import AbstractPlayer

    class Player(AbstractPlayer):

        name = 'Han Solo'

        def next_turn(self, galaxy, context):
            # Get your ships
            my_ships = galaxy.get_player_ships(self.name)
            # For every of your ships...
            for ship in my_ships:
                # find the nearby planets...
                nearby_planets = galaxy.nearby_planets(ship.position, ship.speed)
                # pick any of them...
                target_planet = random.choice(nearby_planets)
                # an set the target to the selected planet
                ship.target = target_planet.position

            return galaxy

After executing your player the generated gif should look similar to this one:


.. image:: https://ik.imagekit.io/jmpdcmsvqee/chapter_03_Xkt-G_P7-.gif
   :target: https://ik.imagekit.io/jmpdcmsvqee/chapter_03_Xkt-G_P7-.gif
   :width: 300pt

Can you see those ships moving around? That, my friend, is what I call freedom.

Long travels
-------------

The implemented random walker strategy moves ships to planets that are one turn away from the original position only.

If you send a ship to a point that is furthest the distance the ship can travel in one turn (this is ``ship.speed``),
it will take more than one turn to arrive at the destination. In the next turn, the ship will be at some point in the
middle between the target and the original destination.

Of course, you can change the ship's target at any time during travel.

.. note::

    **Challenge**
    Build a random walker player that travels to planets that are two turns away only (and not planets that are one turn away)


Final thoughts
--------------

In this chapter we introduced the :attr:`target<pythonium.Ship.target>` attribute, and how it can be used
to set a movement command for a ship.

We also explained how to find planets around certain position with the :func:`Galaxy.nearby_planets<pythonium.Galaxy.nearby_planets>`
method.

Finally, this chapter is a first attempt to describe a player-building methodology in pythonium. Usually, you will make
use of the debugger to test some commands, try a few movements and see how they work from one turn to another. This will help
you to start a draft for your player strategy, and after that, you will need to code it in your player class.

The debugger is a good tool for testing and see how things evolve in a rudimentary way. On more complex players it is hard
to track all the changes and commands that happen in one turn. Imagine you having an empire of more than
100 planets and around 150 ships, it is impossible to check all the positions and movements with the ``ipdb`` debugger.

For those cases, there are more advanced techniques of analysis that involve the generated logs and the report file.
But that is a topic for future chapters.

I hope to see you again, there's still a lot more to learn.
