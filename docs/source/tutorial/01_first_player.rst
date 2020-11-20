

Coding your first player
========================

In this section we will explain how to write your own player to play pythonium.

To do so you have to create a python file with a class named ``Player`` (yes, the name is important) 
that inherith from the class ``pythonium.AbstractPlayer``.

.. code-block:: python

   from pythonium import AbstractPlayer

   class Player(AbstractPlayer):

       name = 'Newbie'

       def next_turn(self, galaxy, context):
           return galaxy

As you can see, there is one attributes and one method that need to be defined in the player class.

* ``name``: Is the name of your player. Try to make it short or your report and gif will look buggy.
* ``next_turn``: This is where the magic happens. 



