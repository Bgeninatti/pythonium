import copy
import random
from collections import Counter

from . import cfg
from .galaxy import Galaxy
from .planet import Planet
from .ship import Ship


class GameMode:

    tenacity = cfg.tenacity

    def build_galaxy(self, players):
        """
        Fabrica la galaxy

        Retorna una instancia de :class:`Galaxy`
        """
        raise NotImplementedError("Metodo no implementado")

    def galaxy_for_player(self, player, t):
        """
        Devuelve una galaxy que muestra sólo las cosas que puede ver el player
        en un turn determinado
        """
        raise NotImplementedError("Metodo no implementado")

    def get_context(self, galaxy, players):
        """
        Genera variables de context para el player en un turn determinado
        """
        raise NotImplementedError("Metodo no implementado")



class ClassicMode(GameMode):

    # Define los atributos de las ships que se pueden construir.


    def __init__(self,
                 planets_count=300,
                 map_size=(500, 500),
                 pythonium_stock=10**6,
                 pythonium_in_surface=0.1,
                 starting_carriers=2,
                 starting_resources=(10**4, 2*10**3, 5*10**3),
                 max_turn=150):

        """
        :param planets_count: Cantidad de planets en la galaxy
        :type planets_count: int
        :param map_size: Dimensiones del mapa
        :type map_size: tuple(int, int)
        :param pythonium_stock: Cantidad total de pythonium disponible en el mapa.
        :type pythonium_stock: int
        :param pythonium_in_surface: Proporción de `pythonium_stock` disponible
            en la superficie de los planets.
        :type pythonium_in_surface: int
        :param starting_carriers: Cantidad de cargueros con los que comienza cada
            player
        :type starting_carriers: int
        ;paran max_turn; Número máximo de turnos
        :type limi: int
        """
        self.planets_count = planets_count
        self.map_size = map_size
        self.pythonium_stock = pythonium_stock
        self.pythonium_in_surface = pythonium_in_surface
        self.starting_carriers = starting_carriers
        self.starting_resources = starting_resources
        self.max_turn = max_turn
        self.winner = None

    def build_galaxy(self, players):
        """
        Representa el conjunto de planets en el que se desenvolverá el juego.

        """
        total_pythonium = int(self.pythonium_stock * self.pythonium_in_surface)
        total_underground_pythonium = self.pythonium_stock - total_pythonium
        # 1. Genera los planeras
        # 1.a positiones aleatorias para los planets
        # Nos aseguramos de todas las positiones sean únicas.
        positions = set()
        while len(positions) < self.planets_count:
            pos = (random.randint(0, self.map_size[0] - 10),
                   random.randint(0, self.map_size[1] - 10))
            positions.add(pos)

        # Genera comdiciones iniciales aleatorias para el resto de los atributos
        # de los planets
        # 1.b Distribuye el pythonium en superficie
        pythonium_distribution = [random.random() for i in range(self.planets_count)]
        coef_pythonium = total_pythonium/sum(pythonium_distribution)
        pythonium = (d*coef_pythonium for d in pythonium_distribution)
        # 1.c Distribuye el pythonium subterraneo
        underground_pythonium_distribution = [random.random()
                                              for i in range(self.planets_count)]
        coef_underground_pythonium = total_underground_pythonium / \
            sum(underground_pythonium_distribution)
        underground_pythonium = (d*coef_underground_pythonium
                                 for d in underground_pythonium_distribution)
        # 1.d Distribuye las concentraciones de pythonium
        concentrations = (round(random.random(), 2) for i in range(self.planets_count))
        # 1.e Genera las temperatures de los planets
        temperatures = (int(random.random()*100) for i in range(self.planets_count))

        planets = {}
        for pid, position, pythonium, underground_pythonium, concentration, temperature \
            in zip(range(self.planets_count),
                   positions,
                   pythonium,
                   underground_pythonium,
                   concentrations,
                   temperatures):

            planet = Planet(pid,
                            tuple(position),
                            int(temperature),
                            int(underground_pythonium),
                            concentration,
                            int(pythonium))
            planets[planet.position] = planet

        galaxy = Galaxy(self.map_size, planets, [])

        galaxy = self.init_players(players, galaxy)

        return galaxy

    def init_players(self, players, galaxy):
        # 2. Genera las condiciones iniciales de los players.

        margins = (galaxy.size[0]*0.1, galaxy.size[1]*0.1)
        for i, player in enumerate(players):
            # 2.a Asigna planets
            if not i:
                position = margins
            else:
                position = (galaxy.size[0] - margins[0],
                            galaxy.size[1] - margins[1])
            nearby_planets = galaxy.nearby_planets(position, 2)


            homeworld = random.choice(nearby_planets)

            homeworld.player = player.name
            homeworld.clans = self.starting_resources[0]
            homeworld.pythonium = self.starting_resources[1]
            homeworld.megacredits = self.starting_resources[2]

            # 2.b Asigna cargueros
            for _ in range(self.starting_carriers):
                ship_features = Ship.get_type(Ship.CARRIER)
                ship = Ship(player.name,
                            Ship.CARRIER,
                            homeworld.position,
                            *ship_features)
                galaxy.add_ship(ship)
        return galaxy

    def galaxy_for_player(self, galaxy, player):
        # TODO: add the following tests:
        # * The player can't see enemy ships not located with own ship
        # * The player can see enemy ships located with any own ship
        #   or in any own planet
        # * The player can see any ship in deep space

        player_planets = galaxy.get_player_planets(player.name)
        # Player can see ships that:
        # * Belongs to him
        # * Are located in any of his planets.
        # * Are in deep space. Not locate in any planet
        visible_ships = [ship for ship in galaxy.ships \
                         if player.name == ship.player \
                         or ship.position in player_planets.keys() \
                         or ship.position not in galaxy.planets.keys()
                        ]
        planets = copy.deepcopy(galaxy.planets)
        ships = copy.deepcopy(visible_ships)

        # Hide information from ships that are not his own
        for ship in [ship for ship in ships if ship.player != player.name]:
            ship.max_cargo = None
            ship.max_mc = None
            ship.attack = None
            ship.megacredits = None
            ship.pythonium = None
            ship.clans = None
            ship.target = None
            ship.transfer = None

        # Hide information of enemy planets and unknown planets
        # (without a player's ship in the planet)
        for planet in [p for pos, p in planets.items()
                       if p.player != player.name \
                       and (p.player is not None \
                            and pos not in [n.position for n in visible_ships])]:
            planet.temperature = None
            planet.underground_pythonium = None
            planet.concentration = None
            planet.pythonium = None
            planet.player = None
            planet.megacredits = None
            planet.max_happypoints = None
            planet.happypoints = None
            planet.clans = None
            planet.mines = None
            planet.new_mines = None
            planet.new_ship = None
            planet.taxes = None

        return Galaxy(galaxy.size, planets, ships, galaxy.explosions)

    def has_ended(self, galaxy, t):
        if t >= self.max_turn:
            return True

        planets_score = Counter(
            (p.player for p in galaxy.planets.values() if p.player is not None))
        threshold = len(galaxy.planets) * 0.7
        for name, score in planets_score.items():
            if score > threshold:
                self.winner = name
                return True
        return False

    def get_score(self, galaxy, players, turn):
        planets_score = Counter(
            (p.player for p in galaxy.planets.values() if p.player is not None))
        ships_carrier_score = Counter(
            (s.player for s in galaxy.ships if s.type == Ship.CARRIER))
        ships_war_score = Counter(
            (s.player for s in galaxy.ships if s.type == Ship.WAR))
        score = []
        for player in players:
            name = player.name
            war_ships = ships_war_score.get(name, 0)
            carrier_ships = ships_carrier_score.get(name, 0)
            score.append({
                'turn': turn,
                'player': name,
                'planets': planets_score.get(name, 0),
                'war_ships': war_ships,
                'carrier_ships': carrier_ships,
                'total_ships': war_ships + carrier_ships
            })
        return score

    def get_context(self, galaxy, players, turn):
        score = self.get_score(galaxy, players, turn)
        return {
            'ship_speed': cfg.ship_speed,
            'tolerable_taxes': cfg.tolerable_taxes,
            'happypoints_tolerance': cfg.happypoints_tolerance,
            'score': score,
            'turn': turn}
