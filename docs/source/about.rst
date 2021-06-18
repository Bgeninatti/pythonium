About Pythonium
================

Pythonium is a space turn-based strategy game where each player lead an alien race
that aim to conquer the galaxy.

You must explore planets to search and extract a valuable mineral: the `pythonium`.
This precious material allows you to build cargo and combat spaceships, mines to get
more pythonium or defenses for your planets.

Manage the economy on your planets, and collect taxes to your people to found your
constructions, but be careful! Keep your clans happy if you want to avoid unrests
in your planets.

Put your space helmet on, set your virtualenv, and start coding.
Battle for pythonium is waiting for you.

Installation
================

You can install Pythonium using PIP.

::

    $ pip install pythonium

or cloning the repository and running

::

    $ python setup.py install

You can test your installation by running

::

    $ pythonium --version
    Running 'pythonium' version x.y.z


Single player mode
==================

Once you have Pythonium installed you can test it for a single player mode with some of the available bots.
i.e: the ``standard_player`` bot.

::

    pythonium --players pythonium.bots.standard_player

Once the command finishes you should have a ``<galaxy_name>.gif`` file and a ``<galaxy_name>.log``, where ``<sector>`` is a unique code generated for the game.

* ``<galaxy_name>.gif``: This is an animation showing how the galaxy ownership changed along the game,
  which planets belongs to each player, ships movements, combats and the score on each turn.

* ``<galaxy_name>.log``: Contain the logs with all the relevant events during the game.

Here's an example of the gif

.. image:: https://ik.imagekit.io/jmpdcmsvqee/single_player_Phcod5vAc.gif
   :target: https://ik.imagekit.io/jmpdcmsvqee/single_player_Phcod5vAc.gif
   :width: 300pt

Multiplayer mode
=================

Pythonium allows up to two players per game, and you can test it by providing two bots to the ``--players`` argument.

::

    pythonium --players pythonium.bots.standard_player pythonium.bots.pacific_player

The output will be similar to the single player mode: one ``.gif`` and one ``.log`` file.


Metrics
=======

Providing the ``--metrics`` arguments, pythonium creates a report with several metrics of the game.
This is specially useful to evaluate the performance of your players, and know their strengths and wekenesses.

::

    pythonium --metrics --players pythonium.bots.standard_player pythonium.bots.pacific_player

In adition to the ``.gif`` and ``.log`` now you will se a ``report_<galaxy_name>.png`` with several charts.


What next?
==========

Now you probably wants to write your own bot, didn't you?

Check out the :ref:`tutorial` to see how to do it.
