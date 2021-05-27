.. _First Player:

Coding your first player
========================

Welcome player!

Welcome to the hard path of stop being part of a selfish colony of humanoids,
jailed in their lonely planet with the only purpose of destroying themselves; to start being an adventurer,
a space explorer, and a strategist. All with the power of your terminal and text editor.

In this section, you will learn how to create a player to play Pythonium.

Yes, you read correctly. You will not play Pythonium. You will build a player that will play Pythonium
for you, and all your strategy needs to be implemented on that player.

This is a turn-based game, which means the player will receive a set of information (or state of the game)
at the beginning of turn 0, and it will make decisions based on that information to influence the state of
the game at turn 1. This process will be repeated again and again in an iterative process until the
game finishes.

Your player then is not more than a python class implementing a method that is executed every turn.
This method receives as parameters the state of the ``galaxy``, and some other ``context`` about the state of the game
(i.e, the scoreboard and other useful data), and it must return the same ``galaxy`` instance with some changes reflecting
the player's desitions.

Let's stop divagating and start coding.

Put this code inside a python file:

.. code-block:: python

   from pyhtonium import AbstractPlayer

   class Player(AbstractPlayer):

       name = 'Han Solo'

       def next_turn(self, galaxy, context):
           return galaxy


There are a few things to note from here.

In the first place, the ``Player`` class inherits from an ``AbstractPlayer``.
Second, there is one attribute and one method that needs to be defined in the player class.

* ``name``: This is the name of your player. Try to make it short or your reports and gif will look buggy.
* ``next_turn``: A method that will be executed every turn. *Where the magic happens*.

Let's save now this file as ``my_player.py`` and execute the following command:

.. code-block:: bash

    $ pyhtonium --player my_player
    ** Pythonium **
    Running battle in Sector #PBA5V2
    Playing game.....................................
    Nobody won
    Game ran in 5.38 seconds

The output will show the name of the *sector* (some place in the galaxy) where the game occurs, and some other
self-explained information.

Once the command finishes, you will find in your working directory two files:

* ``PBA5V2.gif``: A visual representation of the game. The closest thing to a UI that you will find in Pythonium.
* ``PBA5V2.log``: This contains all the information related to the game execution. Every change on the galaxy state (influenced by the player or not) is logged on this file.

.. note::

    Notice that the name of both files is the sector name. Each game is generated with a random (kinda unique)
    sector name.

As a gif you will see something similar to this:

.. image:: https://ik.imagekit.io/jmpdcmsvqee/first_player_tT9jZvrre.gif
   :target: https://ik.imagekit.io/jmpdcmsvqee/first_player_tT9jZvrre.gif
   :width: 300pt

Do you see it? Nothing happens. You just stay on your planet and do nothing for all eternity.
If you check again on the player's code, this is precisely what it does: returns the galaxy without changing anything.

Congratulations! You just reproduced your miserable human life on earth, as a Pythonium player.

Wanna see the cool stuff? Then keep moving, human.