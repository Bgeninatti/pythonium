About Pythonium
================

Pythonium is a space turn-based strategy game where each player leads an alienrace that aims to conquer the galaxy.

You must explore planets to search and extract a valuable mineral: the `pythonium`.
This precious material allows you to build cargo and combat spaceships, or mines to get
more pythonium.

Manage the economy on your planets, and collect taxes on your people to finance your
constructions, but be careful! Keep your clans happy if you want to  avoid unrest in your planets.

Put your space helmet on, set your virtualenv, and start coding.

Battle for pythonium is waiting for you!

Installation
================

You can install Pythonium by cloning `the repository <https://github.com/Bgeninatti/pythonium>`_ and running

::

    $ python setup.py install

and then test your installation by running

::

    $ pythonium --version
    Running 'pythonium' version x.y.z


Single-player mode
==================

Once you have Pythonium installed you can test it for a single-player mode with some of the available bots.
For example, the ``standard_player`` bot.

::

    pythonium --players pythonium.bots.standard_player

Once the command finishes you should have a ``<galaxy_name>.gif`` file and a ``<galaxy_name>.log``,
where ``<galaxy_name>`` is a unique code generated for the game.

* ``<galaxy_name>.gif``: This is an animation showing how the galaxy ownership changed along with the game,
  which planets belong to each player, ships movements, combats, and the score on each turn.

* ``<galaxy_name>.log``: Contain the logs with all the relevant events during the game.

Here's an example of the gif

.. image:: https://ik.imagekit.io/jmpdcmsvqee/single_player_kOfI32YJ6sW.gif
   :target: https://ik.imagekit.io/jmpdcmsvqee/single_player_kOfI32YJ6sW.gif
   :width: 300pt

Multiplayer mode
=================

Pythonium allows up to two players per game, and you can test it by providing two bots to the ``--players`` argument.

::

    pythonium --players pythonium.bots.standard_player pythonium.bots.pacific_player

The output will be similar to the single player mode: one ``.log`` and one ``.gif`` file.


.. image:: https://ik.imagekit.io/jmpdcmsvqee/multi_player_COZwjdq3nKB.gif
   :target: https://ik.imagekit.io/jmpdcmsvqee/multi_player_COZwjdq3nKB.gif
   :width: 300pt


Metrics
=======

Providing the ``--metrics`` arguments, pythonium creates a report with several metrics of the game.
This is especially useful to evaluate the performance of your players, and know their strengths and weaknesses.

::

    pythonium --metrics --players pythonium.bots.standard_player pythonium.bots.pacific_player

In addition to the ``.gif`` and ``.log`` now you will se a ``report_<galaxy_name>.png`` with several charts.


.. image:: https://ik.imagekit.io/jmpdcmsvqee/sample_report_rm-fTWhSa.png
   :target: https://ik.imagekit.io/jmpdcmsvqee/sample_report_rm-fTWhSa.png
   :width: 300pt

Acknowledge
===========

This game is strongly inspired by `VGA Planets <https://en.wikipedia.org/wiki/VGA_Planets>`_, a space strategy war game from 1992 created by Tim Wisseman.

The modern version of VGA Planets is `Planets.nu <https://planets.nu/>`_, and that project has also influenced the development of Pythonium.

To all of them, thank you.


What next?
==========

Now you probably wants to write your own bot, didn't you?

Check out the :ref:`tutorial` to see how to do it.
