.. _Tutorial Chapter 01:

Chapter 1 - The beginning of the road
======================================

Welcome player!

Welcome to the hard path of stop being part of a selfish colony of humanoids,
jailed in their lonely planet with the only purpose of destroying themselves; to start being an adventurer,
a space explorer, and a strategist. All with the power of your terminal and text editor.

In this section, you will learn how to create a player to play Pythonium.

Yes, you read correctly. You will not play Pythonium. You will build a player that to play Pythonium
for you, and all your strategy must be implemented on that player.

This is a turn-based game, which means each player receives a set of information (or state of the game)
at the beginning of turn `t`, and makes decisions based on that information to influence the state of
the game at turn `t+1`. This sequence is repeated again and again in an iterative process until the
game finishes.

Your player then is not more than a `python class <https://docs.python.org/3/tutorial/classes.html>`_ implementing a
`method <https://docs.python.org/3/tutorial/classes.html#method-objects>`_ that is executed every turn.
This method receives as parameters the state of the ``galaxy``, and some other ``context`` about the state of the game
(i.e, the scoreboard and other useful data), and it must return the same ``galaxy`` instance with some changes reflecting
the player's decisions.

Let's stop divagating and start coding.

Put this code inside a python file:

.. code-block:: python

   from pythonium import AbstractPlayer

   class Player(AbstractPlayer):

       name = 'Han Solo'

       def next_turn(self, galaxy, context):
           return galaxy


There are a few things to note from here.

In the first place, the ``Player`` class inherits from an ``AbstractPlayer``.
Second, there is one attribute and one method that needs to be defined in this class.

* ``name``: The name of your player. Try to make it short or your reports and gif will look buggy.
* ``next_turn``: A method that will be executed every turn. This is where your strategy is implemented.

.. _Executing your player:

Executing your player
----------------------

Let's save now this file as ``my_player.py`` (or whatever name you like) and execute the following command:

.. code-block:: bash

    $ pythonium --player my_player
    ** Pythonium **
    Running battle in Galaxy #PBA5V2
    Playing game.....................................
    Nobody won

The output will show the name of the galaxy where the game occurs, and some other
self-explained information.

Once the command finishes, you will find in your working directory two files:

* ``PBA5V2.gif``: A visual representation of the game. The closest thing to a UI that you will find in Pythonium.
* ``PBA5V2.log``: A plain-text file containing all the information related to the game execution. Every change on the galaxy state (influenced by the player or not) is logged on this file.

.. note::

    Notice that the name of both files is the galaxy name. Each game is generated with a random (kinda unique)
    galaxy name.

As a gif you will see something similar to this:

.. image:: https://ik.imagekit.io/jmpdcmsvqee/chapter_01_pwIQAPgxD.gif
   :target: https://ik.imagekit.io/jmpdcmsvqee/chapter_01_pwIQAPgxD.gif
   :width: 300pt

Reading from the top to the bottom:

* You are in the galaxy `#PBA5V2`
* You are Han Solo (your player's name)
* The turn at each frame is displayed at the left of the player name
* You have one planet and two ships
* Your planet and ships are in the blue dot. The rest of the dots are the others 299 planets in the galaxy.

.. note::

    The blue dot is bigger than the white ones. The reason for this is that planets with any ship on their orbits are
    represented with bigger dots. This means your two ships are placed on your only planet.


Do you see it? Nothing happens. You just stay on your planet and do nothing for all eternity.
By reviewing the player's code closely you will notice that this is precisely what it does: returns the galaxy without
changing anything.

Congratulations! You just reproduced your miserable human life on earth, as a Pythonium player.

Wanna see the cool stuff? Then keep moving, human.
