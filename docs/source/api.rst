Player API Reference
=====================

All the classes, methods, and attributes described in this sections can be used in your ``next_turn`` method.

Despite some of these classes have additional methods and attributes not listed here, those are not useful for you in any way.

You shouldn't expect any useful information from those methods and attributes. Most of them are used by Pythonium internally.

.. autoclass:: pythonium.AbstractPlayer
    :members: name, next_turn

.. autoclass:: pythonium.Galaxy
    :members: known_races, compute_distance, distances_to_planets, nearby_planets, get_player_planets, get_player_ships, get_ships_in_deep_space, get_ships_in_position, search_ship, search_planet, get_ships_by_position, get_ships_in_planets, get_ships_conflicts, get_ocuped_planets, get_planets_conflicts 

.. autoclass:: pythonium.Planet
    :members: pid, position, temperature, underground_pythonium, concentration, pythonium, mine_cost, player, megacredits, clans, mines, max_happypoints, happypoints, new_mines, new_ship, max_mines, taxes, rioting_index, dpythonium, dmegacredits, dhappypoints, dclans, can_build_mines, can_build_ship

.. autoclass:: pythonium.Ship
    :members: nid, player, type, position, max_cargo, max_mc, attack, megacredits, pythonium, clans, target, transfer

.. autoclass:: pythonium.ShipType
    :members: name, cost, max_cargo, max_mc, attack

.. autoclass:: pythonium.Transfer
    :members:

.. autoclass:: pythonium.Explosion
    :members:




