import logging
import os
import random
import string
import sys
from collections import defaultdict
from itertools import groupby

import attr
import numpy as np

from . import cfg
from .explosion import Explosion
from .renderer import GifRenderer
from .ship import Ship

logger = logging.getLogger("game")


class Game:
    def __init__(
        self,
        sector,
        players,
        gmode,
        *,
        renderer=GifRenderer,
        raise_exceptions=False,
    ):
        """
        :param sector: Sector name
        :type sector: str
        :param players: Players for the game. Supports one or two players.
        :type players: list of instances of classes that extends
            from :class:`AbstractPlayer`
        :param gmode: Class that define some game rules
        :type gmode: :class:GameMode
        :param logger: Logger for the game
        :param renderer: Instance that renders the game on each turn
        :param verbose: If ``True`` print the logs in stdout
        :type verbose: bool
        :param raise_exceptions: If ``True`` stop the game if an exception is raised when
            computing player actions. Useful for debuging players.
        :type raise_exceptions: bool
        """
        if len(players) != len({p.name for p in players}):
            raise ValueError("Player names must be unique")

        self.sector = sector
        sys.stdout.write("** Pythonium **\n")
        sys.stdout.write(f"Running battle in Sector #{self.sector}\n")
        self.gmode = gmode
        self.players = players
        self.raise_exceptions = raise_exceptions
        logger.info(
            "Initializing galaxy",
            extra={"players": len(self.players), "sector": self.sector},
        )
        self.galaxy = self.gmode.build_galaxy(self.players)
        logger.info("Galaxy initialized")
        self._renderer = renderer(self.galaxy, f"Sector #{self.sector}")

    def extract_player_orders(self, player, galaxy, context):
        player_galaxy = player.next_turn(galaxy, context)

        # The function must return the mutated galaxy

        if id(galaxy) != id(player_galaxy):
            raise ValueError(
                "The `run_player` method must return a mutated galaxy"
            )

        planets_orders = [
            p.get_orders()
            for p in player_galaxy.planets.values()
            if p.player == player.name
        ]
        ships_orders = [
            s.get_orders()
            for s in player_galaxy.ships
            if s.player == player.name
        ]

        orders = [
            o for orders in ships_orders + planets_orders for o in orders
        ]
        logger.info(
            "Player orders computed",
            extra={
                "turn": self.galaxy.turn,
                "player": player.name,
                "orders": len(orders),
            },
        )

        grouped_actions = groupby(orders, lambda o: o[0])
        return grouped_actions

    def play(self):
        while True:

            sys.stdout.write(f"\rPlaying game{'.' * int(self.galaxy.turn/4)}")
            sys.stdout.flush()

            logger.info("Turn started", extra={"turn": self.galaxy.turn})
            orders = defaultdict(lambda: [])
            context = self.gmode.get_context(
                self.galaxy, self.players, self.galaxy.turn
            )

            # Should I record the state?
            if self._renderer:
                self._renderer.render_frame(context)

            # log current score
            for player_score in context["score"]:
                logger.info("Current score", extra=player_score)

            for player in self.players:
                # Filtra cosas que ve el player según las reglas del juego
                galaxy = self.gmode.galaxy_for_player(self.galaxy, player)
                try:
                    logger.info(
                        "Computing orders for player",
                        extra={
                            "turn": self.galaxy.turn,
                            "player": player.name,
                        },
                    )

                    player_orders = self.extract_player_orders(
                        player, galaxy, context
                    )
                    for name, player_orders in player_orders:
                        for order in player_orders:
                            orders[name].append((player, order[1:]))

                except Exception as e:
                    logger.error(
                        "Player lost turn",
                        extra={
                            "turn": self.galaxy.turn,
                            "player": player.name,
                            "reason": str(e),
                        },
                    )
                    logger.info(
                        "Player orders computed",
                        extra={
                            "turn": self.galaxy.turn,
                            "player": player.name,
                            "orders": 0,
                        },
                    )
                    if self.raise_exceptions:
                        raise e
                    continue

            if self.gmode.has_ended(self.galaxy, self.galaxy.turn):
                if self.gmode.winner:
                    logger.info(
                        "Winner!",
                        extra={
                            "turn": self.galaxy.turn,
                            "winner": self.gmode.winner,
                        },
                    )
                    message = f"Player {self.gmode.winner} wins\n"
                else:
                    logger.info("Nobody won", extra={"turn": self.galaxy.turn})
                    message = "Nobody won\n"

                sys.stdout.write("\n")
                sys.stdout.write(message)

                if self._renderer:
                    # Render last frame
                    context = self.gmode.get_context(
                        self.galaxy, self.players, self.galaxy.turn
                    )
                    self._renderer.render_frame(context)
                    # Save as gif
                    self._renderer.save_gif(f"{self.sector}.gif")
                break

            # Reset explosions
            self.galaxy.explosions = []

            # Sort orders by object id
            for o in orders.values():
                o.sort(key=lambda o: o[1][0])

            self.run_turn(orders)

    def run_turn(self, orders):
        """
        Execute turn orders in the following order.
        1. Ships download transfers :func:`action_ship_transfer`
        2. Ships upload transfers :func:`action_ship_transfer`
        3. Mines construction :func:`action_planet_build_mines`
        4. Taxes changes
        5. Ships movements :func:`action_ship_move`
        6. Resolve ship to ship combats :func:`resolve_ship_to_ship`
        7. Resolve ship to planet combats :func:`resolve_planet_to_ship`
        8. Ships construction :func:`action_planet_build_ship`
        9. Population changes
        10. Happypoints changes
        11. Taxes recollection
        12. Pythonium extraction
        """
        # 1. Ships download transfers
        # 2. Ships upload transfers
        self.run_player_action(
            "ship_transfer", orders.get("ship_transfer", [])
        )

        # 3. Mines construction
        self.run_player_action(
            "planet_build_mines", orders.get("planet_build_mines", [])
        )

        # 4. Taxes changes
        self.run_player_action(
            "planet_set_taxes", orders.get("planet_set_taxes", [])
        )

        # 5. Ship movements
        self.run_player_action("ship_move", orders.get("ship_move", []))

        if cfg.tenacity:
            # 6. Resolve ship to ship combats
            ships_in_conflict = self.galaxy.get_ships_conflicts()
            for ships in ships_in_conflict:
                if not any((s.attack for s in ships)):
                    continue
                self.resolve_ships_to_ship_conflict(ships)

            self.galaxy.remove_destroyed_ships()

            # 7. Resolve ship to planet combats
            planets_in_conflict = self.galaxy.get_planets_conflicts()
            for planet, ships in planets_in_conflict:
                if not any((s.attack for s in ships)):
                    continue
                self.resolve_planet_conflict(planet, ships)

        # 8. Ship construction
        self.run_player_action(
            "planet_build_ship", orders.get("planet_build_ship", [])
        )

        # 9. Population change
        # 10. Happypoints changes
        # 11. Taxes recollection
        # 12. Pythonium extraction
        ocuped_planets = self.galaxy.get_ocuped_planets()
        for planet in ocuped_planets:
            self.planet_produce_resources(planet)

        self.galaxy.turn += 1

    def planet_produce_resources(self, planet):
        dhappypoints = planet.dhappypoints
        if dhappypoints:
            planet.happypoints += dhappypoints
            logger.info(
                "Happypoints change",
                extra={
                    "turn": self.galaxy.turn,
                    "player": planet.player,
                    "planet": planet.id,
                    "dhappypoints": dhappypoints,
                    "happypoints": planet.happypoints,
                },
            )

        dmegacredits = planet.dmegacredits
        if dmegacredits:
            planet.megacredits += dmegacredits
            logger.info(
                "Megacredits change",
                extra={
                    "turn": self.galaxy.turn,
                    "player": planet.player,
                    "planet": planet.id,
                    "dmegacredits": dmegacredits,
                    "megacredits": planet.megacredits,
                },
            )

        dpythonium = planet.dpythonium
        if dpythonium:
            planet.pythonium += dpythonium
            logger.info(
                "Pythonium change",
                extra={
                    "turn": self.galaxy.turn,
                    "player": planet.player,
                    "planet": planet.id,
                    "dpythonium": dpythonium,
                    "pythonium": planet.pythonium,
                },
            )

        dclans = planet.dclans
        if dclans:
            planet.clans += dclans
            logger.info(
                "Population change",
                extra={
                    "turn": self.galaxy.turn,
                    "player": planet.player,
                    "planet": planet.id,
                    "dclans": dclans,
                    "clans": planet.clans,
                },
            )

    def resolve_ships_to_ship_conflict(self, ships):

        total_attack = sum(s.attack for s in ships)
        groups = groupby(ships, lambda s: s.player)

        max_score = 0
        winner = None
        for player, player_ships in groups:
            player_attack = sum((s.attack for s in player_ships))
            attack_fraction = player_attack / total_attack

            # Compute score probability distribution
            shape = 10 * attack_fraction
            scale = (1 - self.gmode.tenacity) ** attack_fraction
            score = np.random.gamma(shape, scale)

            logger.info(
                "Score in conflict",
                extra={
                    "turn": self.galaxy.turn,
                    "player": player,
                    "player_attack": player_attack,
                    "attack_fraction": attack_fraction,
                    "score": score,
                },
            )
            if score > max_score:
                winner = player
                max_score = score

        logger.info(
            "Conflict resolved",
            extra={
                "turn": self.galaxy.turn,
                "winner": winner,
                "max_score": max_score,
                "total_attack": total_attack,
                "total_ships": len(ships),
            },
        )

        # Destroy defeated ships
        for ship in ships:
            if ship.player == winner:
                continue
            logger.info(
                "Explosion",
                extra={
                    "turn": self.galaxy.turn,
                    "player": ship.player,
                    "ship": ship.id,
                    "ship_type": ship.type.name,
                    "position": ship.position,
                },
            )
            self.galaxy.explosions.append(
                Explosion(ship, len(ships), total_attack)
            )

    def resolve_planet_conflict(self, planet, ships):

        enemies = {s.player for s in ships if s.player != planet.player}

        if not enemies:
            raise ValueError(
                "Ok, I don't know what's going on. This is not a conflict."
            )

        if len(enemies) != 1:
            raise ValueError(
                "Run :meth:`resolve_ships_to_ship_conflict` first"
            )

        winner = enemies.pop()

        # If is not of his own, the winner conquer the planet.
        if planet.player != winner:
            logger.info(
                "Planet conquered by force",
                extra={
                    "turn": self.galaxy.turn,
                    "player": winner,
                    "planet": planet.id,
                    "clans": planet.clans,
                },
            )
            planet.player = winner
            planet.clans = 1
            planet.mines = 0
            planet.taxes = 0

    def run_player_action(self, name, orders):
        """
        :param name: name del player que ejecuta la params
        :type name: str
        :param params: Una tupla que indica la params a ejecutar y los parámetros
            de la misma. ('name', *params)
        :type params: tuple
        """
        func = getattr(self, f"action_{name}", None)
        for player, params in orders:
            obj = None
            if name.startswith("ship"):
                nid = params[0]
                args = params[1:]

                obj = self.galaxy.search_ship(nid)
            elif name.startswith("planet"):
                pid = params[0]
                args = params[1:]

                obj = self.galaxy.search_planet(pid)
            else:
                logger.warning(
                    "Unknown params",
                    extra={
                        "turn": self.galaxy.turn,
                        "player": player.name,
                        "params": params,
                    },
                )
                continue

            if not obj:
                logger.warning(
                    "Object not found",
                    extra={
                        "turn": self.galaxy.turn,
                        "player": player.name,
                        "params": params,
                        "name": name,
                    },
                )
                continue

            if obj.player != player.name:
                logger.warning(
                    "This is not yours",
                    extra={
                        "turn": self.galaxy.turn,
                        "player": player.name,
                        "owner": obj.player,
                        "obj": type(obj),
                    },
                )
                continue

            logger.debug(
                "Running action for player",
                extra={
                    "turn": self.galaxy.turn,
                    "player": obj.player,
                    "action": name,
                    "obj": type(obj),
                    "args": args,
                },
            )

            try:
                func(obj, *args)
            except Exception as e:
                logger.error(
                    "Unexpected error running player params",
                    extra={
                        "turn": self.galaxy.turn,
                        "player": obj.player,
                        "action": name,
                        "obj": type(obj),
                        "args": args,
                        "reason": e,
                    },
                )

    def action_ship_move(self, ship, target):

        _from = ship.position
        distance_to_target = self.galaxy.compute_distance(
            ship.position, target
        )

        if distance_to_target <= ship.speed:
            to = target
            target = None
        else:

            direction = (
                (target[0] - ship.position[0]) / distance_to_target,
                (target[1] - ship.position[1]) / distance_to_target,
            )
            to = (
                int(ship.position[0] + direction[0] * ship.speed),
                int(ship.position[1] + direction[1] * ship.speed),
            )

        ship.position = to
        ship.target = target
        logger.info(
            "Ship moved",
            extra={
                "turn": self.galaxy.turn,
                "player": ship.player,
                "ship": ship.id,
                "from": _from,
                "to": ship.position,
                "target": ship.target,
            },
        )
        return

    def action_ship_transfer(self, ship, transfer):
        planet = self.galaxy.planets.get(ship.position)

        logger.info(
            "Attempt to transfer",
            extra={
                "ship": ship.id,
                "clans": transfer.clans,
                "pythonium": transfer.pythonium,
                "megacredits": transfer.megacredits,
            },
        )

        if not planet:
            logger.warning(
                "Can not transfer in deep space",
                extra={"turn": self.galaxy.turn, "ship": ship.id},
            )
            return

        if planet.player is not None and planet.player != ship.player:
            logger.warning(
                "Can not transfer to an enemy planet",
                extra={
                    "turn": self.galaxy.turn,
                    "ship": ship.id,
                    "planet": planet.id,
                },
            )
            return

        # Check if transfers + existances are grather than capacity on clans and pythonium
        available_cargo = ship.max_cargo - (ship.pythonium + ship.clans)

        # Adjust transfers to real availability in planet and ship
        transfer.clans = (
            min(transfer.clans, planet.clans, available_cargo)
            if transfer.clans > 0
            else max(transfer.clans, -ship.clans)
        )
        transfer.pythonium = (
            min(
                transfer.pythonium,
                planet.pythonium,
                available_cargo - transfer.clans,
            )
            if transfer.pythonium > 0
            else max(transfer.pythonium, -ship.pythonium)
        )
        transfer.megacredits = (
            min(
                transfer.megacredits,
                planet.megacredits,
                ship.max_mc - ship.megacredits,
            )
            if transfer.megacredits > 0
            else max(transfer.megacredits, -ship.megacredits)
        )

        # Do transfers
        ship.clans += transfer.clans
        ship.pythonium += transfer.pythonium
        ship.megacredits += transfer.megacredits

        logger.info(
            "Ship transfer to planet",
            extra={
                "turn": self.galaxy.turn,
                "player": ship.player,
                "ship": ship.id,
                "clans": transfer.clans,
                "pythonium": transfer.pythonium,
                "megacredits": transfer.megacredits,
            },
        )

        planet.clans -= transfer.clans
        planet.pythonium -= transfer.pythonium
        planet.megacredits -= transfer.megacredits

        if not planet.clans:
            # If nobody stays in the planet the player doesn't own it anymore
            planet.player = None
            logger.info(
                "Planet abandoned",
                extra={
                    "turn": self.galaxy.turn,
                    "player": ship.player,
                    "planet": planet.id,
                },
            )
        elif planet.player is None and planet.clans > 0:
            # If nobody owns the planet and the ship download clans the player
            # conquer the planet
            planet.player = ship.player
            logger.info(
                "Planet conquered",
                extra={
                    "turn": self.galaxy.turn,
                    "player": ship.player,
                    "planet": planet.id,
                },
            )

        return

    def action_planet_build_mines(self, planet, new_mines):
        if new_mines <= 0:
            # Nada que hacer
            return

        new_mines = int(min(new_mines, planet.can_build_mines()))

        if not new_mines:
            logger.warning(
                "Can not build mines",
                extra={
                    "turn": self.galaxy.turn,
                    "planet": planet.id,
                    "pythonium": planet.pythonium,
                    "megacredits": planet.megacredits,
                    "mines": planet.mines,
                    "max_mines": planet.max_mines,
                },
            )
            return

        planet.mines += new_mines
        planet.megacredits -= new_mines * self.gmode.mine_cost.megacredits
        planet.pythonium -= new_mines * self.gmode.mine_cost.pythonium

        logger.info(
            "New mines",
            extra={
                "turn": self.galaxy.turn,
                "player": planet.player,
                "planet": planet.id,
                "new_mines": new_mines,
            },
        )

    def action_planet_build_ship(self, planet, ship_type):

        ships_count = len(self.galaxy.get_player_ships(planet.player))
        if ships_count >= self.gmode.max_ships:
            logger.warning(
                "Ships limit reached",
                extra={
                    "turn": self.galaxy.turn,
                    "player": planet.player,
                    "ships_count": ships_count,
                },
            )
            return

        try:
            if not ship_type:
                logger.error(
                    "Ship features not found",
                    extra={
                        "turn": self.galaxy.turn,
                        "ship_type": ship_type.name,
                    },
                )
                return

        except KeyError:
            logger.warning(
                "Unknown ship type",
                extra={
                    "turn": self.galaxy.turn,
                    "player": planet.player,
                    "planet": planet.id,
                    "ship_type": ship_type.name,
                },
            )
            return

        if not planet.can_build_ship(ship_type):
            logger.warning(
                "Missing resources",
                extra={
                    "turn": self.galaxy.turn,
                    "planet": planet.id,
                    "ship_type": ship_type.name,
                    "megacredits": planet.megacredits,
                    "pythonium": planet.pythonium,
                },
            )
            return

        ship = Ship(
            player=planet.player,
            type=ship_type,
            position=planet.position,
            max_cargo=ship_type.max_cargo,
            max_mc=ship_type.max_mc,
            attack=ship_type.attack,
            speed=ship_type.speed,
        )

        planet.megacredits -= ship_type.cost.megacredits
        planet.pythonium -= ship_type.cost.pythonium

        self.galaxy.add_ship(ship)

        logger.info(
            "New ship built",
            extra={
                "turn": self.galaxy.turn,
                "player": planet.player,
                "planet": planet.id,
                "ship_type": ship_type.name,
            },
        )

    def action_planet_set_taxes(self, planet, taxes):
        if planet.taxes == taxes:
            return

        planet.taxes = min(max(0, taxes), 100)
        logger.info(
            "Taxes updated",
            extra={
                "turn": self.galaxy.turn,
                "player": planet.player,
                "planet": planet.id,
                "taxes": taxes,
            },
        )
