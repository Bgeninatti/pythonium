import re
from collections import defaultdict
from datetime import datetime
from itertools import groupby

import matplotlib.pyplot as plt

log_regex = re.compile(r'(?P<datetime>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \[(?P<loglvl>INFO|WARNING|ERROR|DEBUG)\] (?P<file>[\w\W_]+):(?P<function>[a-zA-Z_]+) (?P<message>.+) - (?=(?:(?P<extras>.+))$)?')


class MetricsCollector:

    def __init__(self, logfile):
        lines = logfile.readlines()
        self.logdicts = []
        for line in lines:
            result = log_regex.match(line)
            if not result:
                continue
            groupdict = result.groupdict()
            groupdict['datetime'] = datetime.fromisoformat(
                groupdict['datetime'].replace(',', '.'))
            extras = groupdict.get('extras')
            if extras:
                groupdict['extras'] = dict((el.split('=') for el in extras.split('; ')))
            self.logdicts.append(groupdict)
        self.turns = [int(l['extras']['turn']) for l in
                      filter(lambda l: l['message'] == "Turn started", self.logdicts)]
        self.known_players = {l['extras']['player'] for l in
                              filter(lambda l: l['message'] == "Computing actions for player",
                                     self.logdicts)}

    def get_metric_for_players(self, message, key, data_type=int):
        """
        Return a time series of each value related to ``key`` in a log
        with ``log['message'] == message``.

        The value is transformed to ``data_type``.

        The function ensures that all there are one metric per turn for
        each``self.known_players``

        This is used to filter, for example, the score of the players
        on each turn, or metrics that we know that are only one per player and turn.
        """
        logs = filter(lambda l: l['message'] == message, self.logdicts)
        data = defaultdict(lambda: [])
        for log in logs:
            extras = log['extras']
            data[extras['player']].append(data_type(extras[key]))
        data['turn'] = self.turns
        # Check that all players have a metrics for each turn
        assert all(len(metrics) == len(self.turns) for metrics in data.values())
        found_players = data.keys()
        assert all(p in found_players for p in self.known_players)
        return data

    def get_turns_runtime(self):
        """
        Return a time serie with the runtime in microseconds for each turn
        """
        logs = list(filter(lambda l: l['message'] == "Turn started", self.logdicts))
        previous = logs[0]['datetime']
        data = defaultdict(lambda: [])
        for log in logs[1:]:
            data['turn'].append(int(log['extras']['turn']))
            data['runtime'].append((log['datetime'] - previous).microseconds)
            previous = log['datetime']
        return data

    def get_events_for_players(self, message, key, data_type=int):
        """
        Find metrics related to an event for each player.
        There can be more than one event for each player per turn.

        Return a dict where player names are the keys and values are
        a list of lists. One list per turn with none event or more.

        This is used for example to filter all the pythonium produced in each
        planet for each player every turn. There are more than one event per
        turn and player.
        """
        # Filter logs and group by turn
        grouped_logs = groupby(
            filter(lambda l: l['message'] == message, self.logdicts),
            lambda l: int(l['extras']['turn'])
        )

        # Create the empty container for each player
        data = dict((p, [[] for t in self.turns])
                    for p in self.known_players)
        for turn, logs in grouped_logs:
            # group by player
            for log in logs:
                player = log['extras']['player']
                value = data_type(log['extras'][key])
                data[player][turn].append(value)
        data['turn'] = self.turns
        return data

    def plot_metrics_for_players(self, metrics, ylabel):
        fig, axs = plt.subplots(1, 1)
        for player in (p for p in metrics.keys() if p != 'turn'):
            axs.plot(metrics['turn'], metrics[player])
            axs.set_xlabel('Turn')
            axs.set_ylabel(ylabel)
        return fig

    def aggregate_events_for_players(self, events, agg):
        """
        Perform aggregation (count, sum, avg, etc) to events metrics for each player
        ``events`` is the output of ``get_events_for_players``
        """
        data = {player: [agg(m) for m in metrics]
                for player, metrics in events.items() if player != 'turn'}
        data['turn'] = events['turn']
        return data

    def build_report(self):
        # Score
        planet_scores = self.get_metric_for_players("Current score", "planets")
        carriers_scores = self.get_metric_for_players("Current score", "carrier_ships")
        warships_scores = self.get_metric_for_players("Current score", "war_ships")
        ships_scores = self.get_metric_for_players("Current score", "total_ships")

        # Runtime
        turns_runtime = self.get_turns_runtime()
        player_actions = self.get_metric_for_players("Actions computed", "actions")

        # War
        conquered_planets = self.aggregate_events_for_players(
            self.get_events_for_players("Planet conquered by force", "planet"), len)
        killed_clans = self.aggregate_events_for_players(
            self.get_events_for_players("Planet conquered by force", "clans"), sum)
        ships_lost = self.aggregate_events_for_players(
            self.get_events_for_players("Explosion", "ship_type"), len)

        # Economy
        dpythonium = self.get_events_for_players("Pythonium change", "dpythonium")
        dclans = self.get_events_for_players("Population change", "dclans")
        dmegacredits = self.get_events_for_players("Megacredits change", "dmegacredits")
        dhappypoints = self.get_events_for_players("Happypoints change", "dhappypoints")
        built_mines = self.aggregate_events_for_players(
            self.get_events_for_players("New mines", "new_mines"), sum)
        built_ships = self.aggregate_events_for_players(
            self.get_events_for_players("New ship built", "ship_type"), len)

        total_dpythonium = self.aggregate_events_for_players(dpythonium, sum)
        total_dclans = self.aggregate_events_for_players(dclans, sum)
        total_dmegacredits = self.aggregate_events_for_players(dmegacredits, sum)

        avg = lambda i: sum(i) / len(i) if i else 0

        avg_dpythonium = self.aggregate_events_for_players(dpythonium, avg)
        avg_dclans = self.aggregate_events_for_players(dclans, avg)
        avg_dmegacredits = self.aggregate_events_for_players(dmegacredits, avg)
        avg_happypoints = self.aggregate_events_for_players(dhappypoints, avg)

        self.plot_metrics_for_players(planet_scores, "Planets") \
            .savefig("Planet Score.png")
        self.plot_metrics_for_players(carriers_scores, "Carriers") \
            .savefig("Carriers.png")
        self.plot_metrics_for_players(warships_scores, "War Ships") \
            .savefig("War Ships.png")
        self.plot_metrics_for_players(ships_scores, "Total Ships") \
            .savefig("Total ships.png")

        self.plot_metrics_for_players(turns_runtime, "Execution time") \
            .savefig("Runtime.png")
        self.plot_metrics_for_players(player_actions, "Actions") \
            .savefig("Player actions.png")

        self.plot_metrics_for_players(conquered_planets, "Conquered planets") \
            .savefig("Conquered planets.png")
        self.plot_metrics_for_players(killed_clans, "Killed clans") \
            .savefig("Killed clans.png")
        self.plot_metrics_for_players(ships_lost, "Ships lost") \
            .savefig("Ships lost.png")

        self.plot_metrics_for_players(total_dpythonium, "Extracted pythonium") \
            .savefig("Extracted pythonium.png")
        self.plot_metrics_for_players(total_dclans, "Population growth") \
            .savefig("Population growth.png")
        self.plot_metrics_for_players(total_dmegacredits, "Collected megacredits") \
            .savefig("Collected megacredits.png")
        self.plot_metrics_for_players(built_ships, "Built ships") \
            .savefig("Built Ships.png")
        self.plot_metrics_for_players(built_mines, "Built mines") \
            .savefig("Built mines.png")

        self.plot_metrics_for_players(avg_dpythonium, "Avg extracted pythonium") \
            .savefig("Avg extracted pythonium.png")
        self.plot_metrics_for_players(avg_dclans, "Avg population growth") \
            .savefig("Avg population growth.png")
        self.plot_metrics_for_players(avg_dmegacredits, "Avg collected megacredits") \
            .savefig("Avg collected megacredits.png")
        self.plot_metrics_for_players(avg_happypoints, "Avg Happypoints") \
            .savefig("Avg happypoints.png")

