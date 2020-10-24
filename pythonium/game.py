import os
import random
import string
import sys
from collections import defaultdict
from itertools import groupby

import numpy as np

from . import cfg
from .explosion import Explosion
from .logger import get_logger
from .renderer import GifRenderer
from .ship import Ship


class Game:

    def __init__(self, players, gmode, *, renderer=GifRenderer, logdir=None):
        """
        :param gmode: Class that define some game rules
        :tpye gmode: :class:GameMode
        :param players: Lista de players
        :type players: :class:`Jugador`
        """
        if len(players) != len({p.name for p in players}):
            raise ValueError("Player names must be unique")

        self.sector = self._build_random_sector_name(6)
        if logdir:
            self.logfile = os.path.join(logdir, f"{self.sector}.log")
        else:
            self.logfile = None

        sys.stdout.write(f"** Pythonium **\n")
        sys.stdout.write(f"Running battle in Sector #{self.sector}\n")
        self.gmode = gmode
        self.players = players
        self._logger = get_logger(__name__, filename=self.logfile)
        self._logger.info("Initializing galaxy",
                          extra={'players': len(self.players), 'sector': self.sector})
        self.galaxy = self.gmode.build_galaxy(self.players)
        self._logger.info("Galaxy initialized")
        self._renderer = renderer(self.galaxy, f"Sector #{self.sector}")
        self.turn = 0

    @staticmethod
    def _build_random_sector_name(length):
        characters = string.ascii_uppercase + string.digits
        return ''.join([random.choice(characters) for _ in range(length)])

    def play(self):
        while True:

            sys.stdout.write(f"\rPlaying game{'.' * int(self.turn/4)}")
            sys.stdout.flush()


            self._logger.info("Turn started", extra={'turn': self.turn})
            actions = defaultdict(lambda: [])
            context = self.gmode.get_context(self.galaxy, self.players, self.turn)

            # Should I record the state?
            if self._renderer:
                self._renderer.render_frame(context)

            # log current score
            for player_score in context['score']:
                self._logger.info("Current score", extra=player_score)

            for player in self.players:
                # Filtra cosas que ve el player según las reglas del juego
                galaxy = self.gmode.galaxy_for_player(self.galaxy, player)
                try:
                    self._logger.info("Computing actions for player",
                                      extra={'turn': self.turn, 'player': player.name})
                    player_actions = player.next_turn(
                        galaxy, context, self.turn)

                    grouped_actions = groupby(player_actions, lambda a: a[0])

                    self._logger.info("Actions computed",
                                      extra={'turn': self.turn,
                                             'player': player.name,
                                             'actions': len(player_actions)})
                    for name, player_actions in grouped_actions:
                        for action in player_actions:
                            actions[name].append((player, action[1:]))
                except Exception as e:
                    self._logger.error("Player lost turn",
                                       extra={'turn': self.turn,
                                              'player': player.name,
                                              'reason': e})
                    continue

            if self.gmode.has_ended(self.galaxy, self.turn):
                if self.gmode.winner:
                    self._logger.info("Winner!",
                                      extra={'turn': self.turn, 'winner': self.gmode.winner})
                    message = f"Player {self.gmode.winner} wins\n"
                else:
                    self._logger.info("Nobody won", extra={'turn': self.turn})
                    message = "Nobody won\n"

                sys.stdout.write("\n")
                sys.stdout.write(message)

                if self._renderer:
                    # Render last frame
                    context = self.gmode.get_context(self.galaxy, self.players, self.turn)
                    self._renderer.render_frame(context)
                    # Save as gif
                    self._renderer.save_gif(f"{self.sector}.gif")
                break

            # Reset explosions
            self.galaxy.explosions = []

            self.run_turn(actions)

    def run_turn(self, actions):
        """
        Execute turn actions in the following order.
        1. Ships download transfers :func:`action_ship_transfer`
        2. Ships upload transfers :func:`action_ship_transfer`
        3. Mines construction :func:`action_planet_build_mines`
        4. Ships construction :func:`action_planet_build_ship`
        5. Ships movements :func:`action_ship_move`
        6. Taxes changes
        7. Resolve ship to ship combats :func:`resolve_ship_to_ship`
        8. Resolve ship to planet combats :func:`resolve_planet_to_ship`
        9. Population changes
        10. Happypoints changes
        11. Taxes recollection
        12. Pythonium extraction
        """
        # 1. Ships download transfers
        # 2. Ships upload transfers
        self.run_player_action('ship_transfer', actions.get('ship_transfer', []))

        # 3. Mines construction
        self.run_player_action('planet_build_mines',
                               actions.get('planet_build_mines', []))

        # 4. Ship construction
        self.run_player_action('planet_build_ship', actions.get('planet_build_ship', []))

        # 5. Ship movements
        self.run_player_action('ship_move', actions.get('ship_move', []))

        # 6. Taxes changes
        self.run_player_action('planet_set_taxes', actions.get('planet_set_taxes', []))

        if cfg.tenacity:
            # 7. Resolve ship to ship combats
            ships_in_conflict = self.galaxy.get_ships_conflicts()
            for ships in ships_in_conflict:
                if not any((s.attack for s in ships)):
                    continue
                self.resolve_ships_to_ship_conflict(ships)

            self.galaxy.remove_destroyed_ships()

            # 8. Resolve ship to planet combats
            planets_in_conflict = self.galaxy.get_planets_conflicts()
            for planet, ships in planets_in_conflict:
                if not any((s.attack for s in ships)):
                    continue
                self.resolve_planet_conflict(planet, ships)

        # 9. Population change
        # 10. Happypoints changes
        # 11. Taxes recollection
        # 12. Pythonium extraction
        ocuped_planets = self.galaxy.get_ocuped_planets()
        for planet in ocuped_planets:
            self.planet_produce_resources(planet)

        self.turn += 1

    def planet_produce_resources(self, planet):
        dhappypoints = planet.dhappypoints
        if dhappypoints:
            planet.happypoints += dhappypoints
            self._logger.info("Happypoints change",
                              extra={'turn': self.turn,
                                     'player': planet.player,
                                     'planet': planet.pid,
                                     'dhappypoints': dhappypoints,
                                     'happypoints': planet.happypoints})

        dmegacredits = planet.dmegacredits
        if dmegacredits:
            planet.megacredits += dmegacredits
            self._logger.info("Megacredits change",
                              extra={'turn': self.turn,
                                     'player': planet.player,
                                     'planet': planet.pid,
                                     'dmegacredits': dmegacredits,
                                     'megacredits': planet.megacredits})

        dpythonium = planet.dpythonium
        if dpythonium:
            planet.pythonium += dpythonium
            self._logger.info("Pythonium change",
                              extra={'turn': self.turn,
                                     'player': planet.player,
                                     'planet': planet.pid,
                                     'dpythonium': dpythonium,
                                     'pythonium': planet.pythonium})

        dclans = planet.dclans
        if dclans:
            planet.clans += dclans
            self._logger.info("Population change",
                              extra={'turn': self.turn,
                                     'player': planet.player,
                                     'planet': planet.pid,
                                     'dclans': dclans,
                                     'clans': planet.clans})

    def resolve_ships_to_ship_conflict(self, ships):

        total_attack = sum(s.attack for s in ships)
        groups = groupby(ships, lambda s: s.player)

        max_score = 0
        winner = None
        for player, player_ships in groups:
            player_attack = sum((s.attack for s in player_ships))
            attack_fraction = player_attack/total_attack

            # Compute score probability distribution
            shape = 10*attack_fraction
            scale = (1 - self.gmode.tenacity)**attack_fraction
            score = np.random.gamma(shape, scale)

            self._logger.info("Score in conflict",
                              extra={'turn': self.turn,
                                     'player': player,
                                     'player_attack': player_attack,
                                     'attack_fraction': attack_fraction,
                                     'score': score})
            if score > max_score:
                winner = player
                max_score = score

        self._logger.info("Conflict resolved",
                          extra={'turn': self.turn,
                                 'winner': winner,
                                 'max_score': max_score,
                                 'total_attack': total_attack,
                                 'total_ships': len(ships)})

        # Destroy defeated ships
        for ship in ships:
            if ship.player == winner:
                continue
            self._logger.info("Explosion",
                              extra={'turn': self.turn,
                                     'player': ship.player,
                                     'ship': ship.nid,
                                     'ship_type': ship.type,
                                     'position': ship.position})
            self.galaxy.explosions.append(
                Explosion(ship, len(ships), total_attack)
            )


    def resolve_planet_conflict(self, planet, ships):

        enemies = {s.player for s in ships if s.player != planet.player}

        if not enemies:
            raise ValueError("Ok, I don't know what's going on. This is not a conflict.")

        if len(enemies) != 1:
            raise ValueError("Run :meth:`resolve_ships_to_ship_conflict` first")

        winner = enemies.pop()

        # If is not of his own, the winner conquer the planet.
        if planet.player != winner:
            self._logger.info("Planet conquered by force",
                              extra={'turn': self.turn,
                                     'player': winner,
                                     'planet': planet.pid,
                                     'clans': planet.clans})
            planet.player = winner
            planet.clans = 1
            planet.mines = 0
            planet.taxes = 0

    def run_player_action(self, name, actions):
        """
        :param name: name del player que ejecuta la params
        :type name: str
        :param params: Una tupla que indica la params a ejecutar y los parámetros
            de la misma. ('name', *params)
        :type params: tuple
        """
        func = getattr(self, f"action_{name}", None)
        for player, params in actions:
            obj = None
            if name.startswith('ship'):
                nid = params[0]
                args = params[1:]

                obj = self.galaxy.search_ship(nid)
            elif name.startswith("planet"):
                pid = params[0]
                args = params[1:]

                obj = self.galaxy.search_planet(pid)
            else:
                self._logger.warning("Unknown params",
                                     extra={'turn': self.turn,
                                            'player': player.name,
                                            'params': params})
                continue

            if not obj:
                self._logger.warning("Object not found",
                                     extra={'turn': self.turn,
                                            'player': player.name,
                                            'params': params,
                                            'name': name})
                continue

            if obj.player != player.name:
                self._logger.warning("This is not yours",
                                     extra={'turn': self.turn,
                                            'player': player.name,
                                            'owner': obj.player,
                                            'obj': type(obj)})
                continue

            self._logger.debug("Running action for player",
                               extra={'turn': self.turn,
                                      'player': obj.player,
                                      'action': name,
                                      'obj': type(obj),
                                      'args': args})

            try:
                func(obj, *args)
            except Exception as e:
                self._logger.error("Unexpected error running player params",
                                   extra={'turn': self.turn,
                                          'player': obj.player,
                                          'action': name,
                                          'obj': type(obj),
                                          'args': args,
                                          'reason': e})

    def action_ship_move(self, ship, target):

        _from = ship.position
        distance_to_target = self.galaxy.compute_distance(ship.position, target)

        if distance_to_target <= cfg.ship_speed:
            to = target
            target = None
        else:

            direction = ((target[0] - ship.position[0]) / distance_to_target,
                         (target[1] - ship.position[1]) / distance_to_target)
            to = (
                int(ship.position[0] + direction[0]*cfg.ship_speed),
                int(ship.position[1] + direction[1]*cfg.ship_speed)
            )

        ship.position = to
        ship.target = target
        self._logger.info("Ship moved",
                          extra={'turn': self.turn,
                                 'player': ship.player,
                                 'ship': ship.nid,
                                 'from': _from,
                                 'to': ship.position,
                                 'target': ship.target})
        return

    def action_ship_transfer(self, ship, transfer):
        if not any(transfer):
            # Nada que hacer
            return

        planet = self.galaxy.planets.get(ship.position)

        if not planet:
            self._logger.warning("Can not transfer in deep space",
                                 extra={'turn': self.turn, 'ship': ship.nid})
            return

        if planet.player is not None and planet.player != ship.player:
            self._logger.warning("Can not transfer to an enemy planet",
                                 extra={'turn': self.turn,
                                        'ship': ship.nid,
                                        'planet': planet.pid})
            return

        tclans, tmc, tpythonium = transfer

        # Check if transfers + existances are grather than capacity on clans and pythonium
        available_cargo = ship.max_cargo - (ship.pythonium + ship.clans)

        # Adjust transfers to real availability in planet and ship
        tclans = min(tclans, planet.clans, available_cargo) \
            if tclans > 0 else max(tclans, -ship.clans)
        tpythonium = min(tpythonium, planet.pythonium, available_cargo - tclans) \
            if tpythonium > 0 else max(tpythonium, -ship.pythonium)
        tmc = min(tmc, planet.megacredits, ship.max_mc - ship.megacredits) \
            if tmc > 0 else max(tmc, -ship.megacredits)

        # Do transfers
        ship.clans += tclans
        ship.pythonium += tpythonium
        ship.megacredits += tmc

        self._logger.info("Ship transfer to planet",
                          extra={'turn': self.turn,
                                 'player': ship.player,
                                 'ship': ship.nid,
                                 'clans': tclans,
                                 'pythonium': tpythonium,
                                 'megacredits': tmc})

        planet.clans -= tclans
        planet.pythonium -= tpythonium
        planet.megacredits -= tmc

        if not planet.clans:
            # If nobody stays in the planet the player doesn't own it anymore
            planet.player = None
            self._logger.info("Planet abandoned",
                              extra={'turn': self.turn,
                                     'player': ship.player,
                                     'planet': planet.pid})
        elif planet.player is None and planet.clans > 0:
            # If nobody owns the planet and the ship download clans the player
            # conquer the planet
            planet.player = ship.player
            self._logger.info("Planet conquered",
                              extra={'turn': self.turn,
                                     'player': ship.player,
                                     'planet': planet.pid})

        return

    def action_planet_build_mines(self, planet, new_mines):
        if new_mines <= 0:
            # Nada que hacer
            return

        cost = cfg.mine_cost
        new_mines = int(min(new_mines,
                            planet.can_build_mines()))

        if not new_mines:
            self._logger.warning("Can not build mines",
                                 extra={'turn': self.turn,
                                        'planet': planet.pid,
                                        'pythonium': planet.pythonium,
                                        'megacredits': planet.megacredits,
                                        'mines': planet.mines,
                                        'max_mines': planet.max_mines})
            return

        planet.mines += new_mines
        planet.megacredits -= new_mines * cost[0]
        planet.pythonium -= new_mines * cost[1]

        self._logger.info("New mines",
                          extra={'turn': self.turn,
                                 'player': planet.player,
                                 'planet': planet.pid,
                                 'new_mines': new_mines})


    def action_planet_build_ship(self, planet, ship_type):

        try:
            can_build = planet.can_build_ship(ship_type)
            ship_features = Ship.get_type(ship_type)
            cost = Ship.COSTS[ship_type]

            if not ship_features:
                self._logger.error("Ship features not found",
                                   extra={'turn': self.turn, 'ship_type': ship_type})
                return

        except KeyError:
            self._logger.warning("Unknown ship type",
                                 extra={'turn': self.turn,
                                        'player': planet.player,
                                        'planet': planet.pid,
                                        'ship_type': ship_type})
            return

        if not can_build:
            self._logger.warning("Missing resources",
                                 extra={'turn': self.turn,
                                        'planet': planet.pid,
                                        'ship_type': ship_type,
                                        'megacredits': planet.megacredits,
                                        'pythonium': planet.pythonium})
            return

        ship = Ship(player=planet.player,
                    type=ship_type,
                    position=planet.position,
                    max_cargo=ship_features[0],
                    max_mc=ship_features[1],
                    attack=ship_features[2])

        planet.megacredits -= cost[0]
        planet.pythonium -= cost[1]

        self.galaxy.add_ship(ship)

        self._logger.info("New ship built",
                          extra={'turn': self.turn,
                                 'player': planet.player,
                                 'planet': planet.pid,
                                 'ship_type': ship_type})

    def action_planet_set_taxes(self, planet, taxes):
        if planet.taxes == taxes:
            return

        planet.taxes = min(max(0, taxes), 100)
        self._logger.info("Taxes updated",
                          extra={'turn': self.turn,
                                 'player': planet.player,
                                 'planet': planet.pid,
                                 'taxes': taxes})

