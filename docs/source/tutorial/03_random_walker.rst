.. _Tutorial Chapter 03:

Chapter 3 - Han Solo: The Random Walker
========================================

Hi human. Glad to see you here. I thought you were lost in some capitalist leisure streaming service.

In this chapter you will learn how to move once for all from your primitive planet and explore the galaxy. Once completed
this tutorial you will be a globetrotter on the galaxy. The Han Solo of the Pythonium universe.

.. warning::
    If you don't know who Han Solo is stop here and come back once you were watched the full `original trilogy of Star Wars <https://en.wikipedia.org/wiki/Star_Wars_Trilogy>`_.

``target``: Where do you want to go?
-------------------------------------

Each ``ship`` instance has a ``target`` attribute indicating where the ship is going. This is one of the control variables
for the ships. You can edit this parameter to order your ships to go into some point in the galaxy.

Let's see where our explorer ship is going:

.. code-block:: python

    ipdb> print(explorer_ship.target)
    None

This mean your ship has no target. Is not going anywhere. In the text turn it will be in the same positions.

You can verify it easily.

.. code-block:: python

    ipdb> galaxy.turn # Check the current turn
    0
    ipdb> my_ships = galaxy.get_player_ships(self.name) # Find all your ships
    ipdb> explorer_ship = next(my_ships) # Select the first ship
    ipdb> explorer_ship.position # Check the ship position
    (66, 180)
    ipdb> c # Move one turn forward
    ...
    ipdb> galaxy.turn # Now you are in turn 1
    1
    ipdb> my_ships = galaxy.get_player_ships(self.name) # Find your ship again
    ipdb> explorer_ship = next(my_ships)
    ipdb> explorer_ship.position # Your ship position is the same as previous turn
    (66, 180)

Your ship stays in the same position when times moves forward. It is not going anywhere.


Knowing the neighborhood
-------------------------

Now you know how to order your ships to go some place, let's figure out what the first destination can be.

For sure you want to visit one of the many unknown planets around you (those with ``player=None``), and possibly you don't
want to travel for all the eternity.

We need to find some unknown planet near yours to arrive fast. In pythonium "fast" means in the next turn.

But wait a minute, how fast your ships travels?

Every ship has a ``speed`` attribute indicating how many light-years can travel in a single turn.

.. code-block:: python

    ipdb> explorer_ship.speed
    80

Great, so your ship can travel up to 80ly in a single turn. The next step is to find an unknown planet that is 80ly or
less from your planet.

The :func:`Galaxy.nearby_planets<pythonium.Galaxy.nearby_planets>` method allows you to find all the planets that are
up to a certain distance away (or less) from an specific position. This method takes a ``position`` and some distance
(called ``neighborhood``), and returns a list with all the nearby planets around that position.

In our case, the neighborhood will be 80ly, the distance a ship can travel in one turn, and the position will be the
ship location.

.. code-block:: python

    ipdb> neighborhood = galaxy.nearby_planets(explorer_ship.position, explorer_ship.speed)
    ipdb> pp neighborhood
    [Planet(id=512901b7-2fa1-4546-8c28-b744e374e859, position=(48, 164), player=None),
     Planet(id=df982408-e2f0-41eb-b290-9d5b3b4c8e8c, position=(31, 65), player=None),
     Planet(id=18ebd813-309f-4e3b-860e-44dd8ac019d3, position=(57, 41), player=None),
     Planet(id=18f2e9c8-d9af-44fa-9545-895da620b479, position=(5, 67), player=None),
     Planet(id=60ca5e8d-6ce9-48a3-b42a-303a8643820b, position=(76, 166), player=None),
     Planet(id=fa611a75-1e5d-4af9-870a-b345c278198e, position=(111, 151), player=None),
     Planet(id=4f60a82a-21ff-429b-bec5-4d5f560d8d34, position=(76, 67), player=None),
     Planet(id=4210f138-3a2f-4355-a0e9-c3c841462c9a, position=(5, 46), player=None),
     Planet(id=dbc95644-4e0a-4aa7-8031-4b349a18faf7, position=(28, 139), player=None),
     Planet(id=a0cb9a30-dabf-45dc-aa06-d0b06a91a6d5, position=(68, 129), player=None),
     Planet(id=b6c14192-9261-45aa-b846-ca63c7018a83, position=(134, 68), player=None),
     Planet(id=eaf93629-c9f5-47c9-a731-d147a83484b8, position=(95, 33), player=None),
     Planet(id=6e236d4b-ef20-4752-b882-c3211640a4fd, position=(27, 26), player=None),
     Planet(id=bf33760f-13fd-4e2d-ad3e-f5572be98cda, position=(84, 92), player=None),
     Planet(id=ffe302e9-1c76-4fd8-a720-7141f288bce7, position=(124, 82), player=None),
     Planet(id=183ff157-ba85-45e3-abae-8fa74a2ddd01, position=(64, 159), player=None),
     Planet(id=5622a094-bee6-4c2b-8418-e68838a4e977, position=(61, 96), player=Han Solo),
     Planet(id=263233ec-f055-4dd7-81c3-c7782f4b8843, position=(103, 137), player=None),
     Planet(id=6e4cf954-3b73-4b72-a327-cc468e040f0e, position=(103, 155), player=None),
     Planet(id=337540ca-454a-44c1-83dd-a88edee900a0, position=(45, 22), player=None),
     Planet(id=1d29c2cc-03b4-480e-9ead-e856f6042974, position=(94, 51), player=None),
     Planet(id=15781fb7-9cfe-415c-bbf9-bc671db0b962, position=(32, 170), player=None),
     Planet(id=165fb6a1-abff-4d1b-a731-0a67212eae5d, position=(128, 58), player=None),
     Planet(id=0631d3bd-a77e-41b6-ae22-cf5592e9c327, position=(60, 97), player=None),
     Planet(id=d9533de2-994a-4783-b876-6379f83792e4, position=(15, 131), player=None)]

Cool, right?

All those planets are one turn away from you. Notice that your planet is included in the neighborhood (because your ship is located in it and
the distance to it is zero).

Traveling
----------

Now let's select the target for your ship. For now, keep it simple: pic some random unknown planet from the list.

.. code-block:: python

    ipdb> unknown_nearby_planets = [p for p in neighborhood if p.player is None]
    ipdb> import random
    ipdb> target_planet = random.choice(unknown_nearby_planets)
    ipdb> target_planet
    Planet(id=18f2e9c8-d9af-44fa-9545-895da620b479, position=(5, 67), player=None)

That's your ship first destination. An unknown planet one turn away from your ship's location.

The next step is set the ship ``target`` to the ``target_planet.position`` and move one turn forward.

.. code-block:: python

    ipdb> galaxy.turn # Check the current turn
    1
    ipdb> explorer_ship.position # Check the ship position
    (61, 96)
    ipdb> explorer_ship.target = target_planet.position # set the ship target
    ipdb> c # move one turn forward

Where is your ship now?

.. code-block:: python

    ipdb> galaxy.turn # you are one turn ahead
    2
    ipdb> my_ships = galaxy.get_player_ships(self.name) # Find all your ships
    ipdb> explorer_ship = next(my_ships) # And keep the explorer ship
    ipdb> explorer_ship.position # Check the ship position
    (5, 67)
    ipdb> explored_planet = galaxy.planets.get(explorer_ship.position) # Find the planet in the ship's position
    ipdb> explored_planet
    Planet(id=18f2e9c8-d9af-44fa-9545-895da620b479, position=(5, 67), player=None)

Your explorer ship just arrived to the target planet. A new and unknown rock in the middle of the space with a lot of
things to learn about and explore.

Congratulations human. You did it. You left the pathetic rock where you spent your whole life, and now you are in a
different one. Probably more pathetic, probably more boring, maybe you don't even have air to breath or food to eat.
But hey... you are a space traveler.


Putting the pieces together
----------------------------

Here we explained how to move your ships. You learned the first, and most basic command: Ship movement.

But we also developed a strategy. I call it "The Random Walker Strategy": A group of ships moving around, exploring
planets without much more to do but travel around the galaxy.

Let's :ref:`exit the debugger<exit the debugger>`, edit your player class, and apply the random walker strategy to all your ships.

You will end up with something like this:

.. code-block:: python

    import random
    from pyhtonium import AbstractPlayer

    class Player(AbstractPlayer):

        name = 'Han Solo'

        def next_turn(self, galaxy, context):
            # Get your ships
            my_ships = galaxy.get_player_ships(self.name)
            # For every of your ships...
            for ship in my_ships:
                # find the nearby planets
                nearby_planets = galaxy.nearby_planets(ship.position, ship.speed)
                # pick any of them
                target_planet = random.choice(nearby_planets)
                # set the target to the selected planet
                ship.target = target_planet.position

            return galaxy

After executing your player you will end up with something like this:


Can you see those ships moving around? That, my friend, is what I call freedom.

Final thoughts
--------------

*“You know, sometimes I amaze even myself.”* - Han Solo
