import re
from collections import defaultdict

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
            extras = groupdict.get('extras')
            if extras:
                groupdict['extras'] = dict((el.split('=') for el in extras.split('; ')))
            self.logdicts.append(groupdict)

    def get_metric_for_players(self, message, key, data_type=int):
        logs = filter(lambda l: l['message'] == message, self.logdicts)
        data = defaultdict(lambda: [])
        for log in logs:
            extras = log['extras']
            turn = int(extras['turn'])
            if turn not in data['turn']:
                data['turn'].append(turn)
            data[extras['player']].append(data_type(extras[key]))
        return data

    def plot_metrics_for_players(self, metrics, ylabel):
        fig, axs = plt.subplots(1, 1)
        for player in (p for p in metrics.keys() if p != 'turn'):
            axs.plot(metrics['turn'], metrics[player])
            axs.set_xlabel('Turn')
            axs.set_ylabel(ylabel)
        return fig

    def get_planets_scores(self):
        planet_scores = self.get_metric_for_players("Current score", "planets")
        carriers_scores = self.get_metric_for_players("Current score", "carrier_ships")
        warships_scores = self.get_metric_for_players("Current score", "war_ships")
        ships_scores = self.get_metric_for_players("Current score", "total_ships")
