
import math

import pytest
from pythonium import Planet, Ship, cfg


@pytest.mark.parametrize('planet_state, ship_state, transfer', [
    ((100, 100, 100), (100, 100, 100), (-100, -100, -100)),
    ((100, 100, 100), (0, 0, 0), (100, 100, 100)),
    ((100, 100, 100), (10, 10, 10), (-100, -100, -100)),
    ((100, 100, 100), (0, 0, 0), (0, 10**10, 0)),
    ((10, 10, 10), (0, 0, 0), (100, 100, 100)),
    ((10000, 10000, 10000), (0, 0, 0), (1000, 100000, 1000)),
])
def test_ship_transfer(game, planet_state, ship_state, transfer):
    ship = game.galaxy.ships[0]
    planet = game.galaxy.planets[ship.position]
    planet.clans = planet_state[0]
    planet.megacredits = planet_state[1]
    planet.pythonium = planet_state[2]
    ship.clans = ship_state[0]
    ship.megacredits = ship_state[1]
    ship.pythonium = ship_state[2]

    available_space = ship.max_cargo - (ship.clans + ship.pythonium)

    game.action_ship_transfer(ship, transfer)

    # Transfering clans...
    if transfer[0] > 0 and planet_state[0] < transfer[0]:
        # from planet to ship, and attempt to transfer more than available
        assert ship.clans == planet_state[0]
        assert not planet.clans
    elif transfer[0] < 0 and ship_state[0] < abs(transfer[0]):
        # from ship to planet, and attempt to transfer more than available
        assert planet.clans == planet_state[0] + ship_state[0]
        assert not ship.clans
    else:
        # in some direction and resources are available
        assert ship.clans == ship_state[0] + min(transfer[0], available_space)
        assert planet.clans == planet_state[0] - transfer[0]

    # Transfering megacredits...
    if transfer[1] > 0 and planet_state[1] < transfer[1]:
        # from planet to ship, and attempt to transfer more than available
        assert ship.megacredits == planet_state[1]
        assert not planet.megacredits
    elif transfer[1] < 0 and ship_state[1] < abs(transfer[1]):
        # from ship to planet, and attempt to transfer more than available
        assert planet.megacredits == planet_state[1] + ship_state[1]
        assert not ship.megacredits
    elif transfer[1] > 0 and ship_state[1] + transfer[1] > ship.max_mc:
        # from planet to ship, and transfer is higher than what left to reach ``max_mc``
        assert ship.megacredits == ship.max_mc
        assert planet.megacredits == planet_state[1] - ship.max_mc
    else:
        # in some direction and resources are available
        assert ship.megacredits == ship_state[1] + transfer[1]
        assert planet.megacredits == planet_state[1] - transfer[1]

    # Transfering pythonium...
    if transfer[2] > 0 and planet_state[2] < transfer[0]:
        # from planet to ship, and attempt to transfer more than available
        assert ship.pythonium == planet_state[2]
        assert not planet.pythonium
    elif transfer[2] < 0 and ship_state[2] < abs(transfer[2]):
        # from ship to planet, and attempt to transfer more than available
        assert planet.pythonium == planet_state[2] + ship_state[2]
        assert not ship.pythonium
    else:
        # in some direction and resources are available
        transfered_clans = ship.clans - ship_state[0]
        assert ship.pythonium == \
            ship_state[2] + min(transfer[2], available_space - transfered_clans)
        assert planet.pythonium == planet_state[2] - ship.pythonium + ship_state[2]

    # Resources can never be negative
    assert ship.clans >= 0
    assert ship.megacredits >= 0
    assert ship.pythonium >= 0
    assert planet.clans >= 0
    assert planet.megacredits >= 0
    assert planet.pythonium >= 0

    # Check for ship transfer limits
    assert ship.clans + ship.pythonium <= ship.max_cargo
    assert ship.megacredits <= ship.max_mc


@pytest.mark.parametrize('transfered_clans', list(range(1, 1000, 100)))
def test_ship_colonize_planet(game, transfered_clans):
    ship = game.galaxy.ships[0]
    planet = game.galaxy.planets[ship.position]

    # Make planet foreign
    planet.player = None
    planet.clans = 0

    # ship must have clans
    ship.clans = transfered_clans

    game.action_ship_transfer(ship, (-transfered_clans, 0, 0))

    assert planet.player == ship.player
    assert planet.clans == transfered_clans


@pytest.mark.parametrize('planet_state, ship_state, transfer', [
    ((100, 100, 100), (100, 100, 100), (-100, -100, -100)),
    ((100, 100, 100), (0, 0, 0), (100, 100, 100)),
    ((100, 100, 100), (10, 10, 10), (-100, -100, -100)),
    ((100, 100, 100), (0, 0, 0), (0, 10**10, 0)),
    ((10, 10, 10), (0, 0, 0), (100, 100, 100)),
])
def test_ship_attempt_transfer_to_enemy(game, planet_state, ship_state, transfer):
    ship = game.galaxy.ships[0]
    ship.clans = ship_state[0]
    ship.megacredits = ship_state[1]
    ship.pythonium = ship_state[2]

    planet = game.galaxy.planets[ship.position]
    planet.clans = planet_state[0]
    planet.megacredits = planet_state[1]
    planet.pythonium = planet_state[2]
    planet.player = 2

    game.action_ship_transfer(ship, transfer)

    assert planet.clans == planet_state[0]
    assert planet.megacredits == planet_state[1]
    assert planet.pythonium == planet_state[2]
    assert ship.clans == ship_state[0]
    assert ship.megacredits == ship_state[1]
    assert ship.pythonium == ship_state[2]


@pytest.mark.parametrize('planet_state, existing_mines, new_mines', [
    ((100, 0, 0), 100, 100),
    ((1000, 1000, 1000), 100, 100),
    ((1000, 100, 100), 100, 200),
    ((100, 100, 100), 100, -100),
])
def test_planet_build_mines(game, planet_state, existing_mines, new_mines):
    planet = list(
        filter(lambda p: p.player is not None, game.galaxy.planets.values())).pop()
    # generate initial conditions for planet
    planet.clans = planet_state[0]
    planet.megacredits = planet_state[1]
    planet.pythonium = planet_state[2]
    planet.mines = existing_mines
    # ``can_build_mines`` also checks for ``max_mines``
    can_build_mines = planet.can_build_mines()

    game.action_planet_build_mines(planet, new_mines)

    if new_mines <= 0:
        assert planet.mines == existing_mines
    elif can_build_mines >= new_mines:
        assert planet.mines == existing_mines + new_mines
    else:
        assert planet.mines == existing_mines + can_build_mines


@pytest.mark.parametrize('planet_state, ship_type', [
    ((0, 0), Ship.CARRIER),
    ((2000, 2000), Ship.CARRIER),
    ((0, 0), Ship.WAR),
    ((2000, 2000), Ship.WAR),
    ((0, 0), 'sarasa'),
    ((2000, 2000), 'sarasa'),
])
def test_planet_build_ship(test_player, game, planet_state, ship_type):
    """
    Planet build ship:
        - New ship of demanded type located in same position as planet
    Planet attempt to build unkown ship type
    Planet attempt to build a ship without available resources
    """
    planet = list(game.galaxy.get_player_planets(test_player.name).values())[0]
    # generate initial conditions for planet
    planet.megacredits = planet_state[0]
    planet.pythonium = planet_state[1]
    # ``can_build_mines`` also checks for ``max_mines``

    if ship_type not in Ship.COSTS.keys():
        with pytest.raises(KeyError):
            planet.can_build_ship(ship_type)
        return

    can_build_ship = planet.can_build_ship(ship_type)
    ships_count = len(game.galaxy.ships)
    ships_in_planet = game.galaxy.get_ships_in_position(planet.position)

    game.action_planet_build_ship(planet, ship_type)

    last_ship = [s for s in game.galaxy.ships if s.nid == game.galaxy._next_ship_id-1][0]
    actual_ships_in_planet = game.galaxy.get_ships_in_position(planet.position)

    if can_build_ship:
        assert len(game.galaxy.ships) == ships_count + 1
        assert len(actual_ships_in_planet) == len(ships_in_planet) + 1
        assert last_ship in actual_ships_in_planet
        assert last_ship not in ships_in_planet
        assert last_ship.position == planet.position
    else:
        assert len(game.galaxy.ships) == ships_count
        assert len(actual_ships_in_planet) == len(ships_in_planet)
        assert last_ship in actual_ships_in_planet



@pytest.mark.parametrize('initial_position, destination', [
    ((0, 0,), (100, 100)),
    ((0, 0,), (10, 10)),
    ((120, 120,), (0, 0)),
    ((120, 120,), (220, 220)),
    ((120, 120,), (0, 220)),
    ((0, 0,), (-1, -10)),
    ((0, 0,), (0, 1000)),
])
def test_ship_move(game, initial_position, destination):
    """
    Ship moves less than ``ship_speed`` ly
        - New position must is destination
        - Target is ``None``
    Ship moves more than ``ship_speed`` ly
        - Only moves ``ship_speed`` ly in the target direction
        - Target is destination
    """
    ship = game.galaxy.ships[0]
    ship.position = initial_position
    distance_to_target = game.galaxy.compute_distance(initial_position, destination)

    game.action_ship_move(ship, destination)

    if distance_to_target <= cfg.ship_speed:
        assert ship.position == destination
        assert ship.target is None
    else:
        new_distance_to_origin = game.galaxy.compute_distance(
            ship.position, initial_position)
        # TODO: Somehow also test the direction. Now only the traveled distance is tested
        assert math.isclose(new_distance_to_origin, cfg.ship_speed, abs_tol=1)
        assert ship.target == destination


@pytest.mark.parametrize('planet_state', [
    (1, 101, 102, 103, 20),
    (100, 101, 102, 103, 25),
    (10, 101, 102, 103, 0),
    (500, 101, 102, 103, 90),
])
def test_planet_produce_resources(test_player, game, planet_state):
    """
    In next turn ``pythonium`` must increase in ``dpythonium``
    """
    planet = list(game.galaxy.get_player_planets(test_player.name).values())[0]
    planet.clans = planet_state[0]
    planet.megacredits = planet_state[1]
    planet.pythonium = planet_state[2]
    planet.happypoints = planet_state[3]
    planet.taxes = planet_state[4]
    planet.mines = 100

    dclans = planet.dclans
    dhappypoints = planet.dhappypoints
    dmegacredits = planet.dmegacredits
    dpythonium = planet.dpythonium

    game.planet_produce_resources(planet)

    assert planet.happypoints == planet_state[3] + dhappypoints

    # Basically test based on the `cfg.happypoints_tolerance` threshold
    if planet.happypoints > cfg.happypoints_tolerance:
        assert planet.clans == planet_state[0] + dclans
        assert planet.megacredits == planet_state[1] + dmegacredits
        assert planet.pythonium == planet_state[2] + dpythonium
    else:
        assert planet.clans < planet_state[0] + dclans
        assert planet.megacredits < planet_state[1] + dmegacredits
        assert planet.pythonium < planet_state[2] + dpythonium


    assert planet.clans > 0
    assert planet.happypoints > 0 and planet.happypoints <= 100
    assert planet.megacredits > 0
    assert planet.pythonium > 0


@pytest.mark.parametrize('ships_args', [
    [
        (1, 0, (10, 10), 0, 0, 100),
        (1, 0, (10, 10), 0, 0, 100),
        (1, 0, (10, 10), 0, 0, 100),
        (2, 0, (10, 10), 0, 0, 100)
    ], [
        (1, 0, (10, 10), 0, 0, 100),
        (1, 0, (10, 10), 0, 0, 100),
        (2, 0, (10, 10), 0, 0, 100),
        (2, 0, (10, 10), 0, 0, 100)
    ], [
        (1, 0, (10, 10), 0, 0, 100),
        (2, 0, (10, 10), 0, 0, 100),
        (2, 0, (10, 10), 0, 0, 100),
        (2, 0, (10, 10), 0, 0, 100)
    ], [
        (1, 0, (10, 10), 0, 0, 100),
        (2, 0, (10, 10), 0, 0, 100),
        (3, 0, (10, 10), 0, 0, 100),
        (4, 0, (10, 10), 0, 0, 100)
    ]
])
def test_ship_to_ship_conflict(game, ships_args):

    ships = [Ship(*ship_args) for ship_args in ships_args]
    game.galaxy.ships = ships

    game.resolve_ships_to_ship_conflict(ships)

    destroyed_ships = [e.ship for e in game.galaxy.explosions]
    winner_ships = [s for s in game.galaxy.ships if s not in destroyed_ships]
    # It must be only one winner
    assert len({s.player for s in winner_ships}) == 1


@pytest.mark.parametrize('planet_args, ships_args', [
    [
        (1000, (10, 10), 0, 0, 0, 0, 1),
        [
            (1, 0, (10, 10), 0, 0, 100),
        ]
    ], [
        (1000, (10, 10), 0, 0, 0, 0, 1),
        [
            (1, 0, (10, 10), 0, 0, 100),
        ]
    ], [
        (1000, (10, 10), 0, 0, 0, 0, 1),
        [
            (2, 0, (10, 10), 0, 0, 100),
            (2, 0, (10, 10), 0, 0, 100)
        ]
    ], [
        (1000, (10, 10), 0, 0, 0, 0, 1),
        [
            (1, 0, (10, 10), 0, 0, 100),
            (4, 0, (10, 10), 0, 0, 100)
        ]
    ]
])
def test_planet_conflict(game, planet_args, ships_args):

    ships = [Ship(*ship_args) for ship_args in ships_args]
    planet = Planet(*planet_args)
    original_player = planet_args[-1]
    game.galaxy.galaxy = ships
    game.galaxy.planets[planet.position] = planet

    enemies = {s.player for s in ships if s.player != planet.player}
    if len(enemies) != 1:
        with pytest.raises(ValueError):
            game.resolve_planet_conflict(planet, ships)
        return

    enemy = enemies.pop()
    enemy_attack = sum((s.attack for s in ships if s.player == enemy))

    game.resolve_planet_conflict(planet, ships)

    if not enemy_attack:
        assert planet.player == original_player
    else:
        assert planet.player == enemy

