import re
from collections import defaultdict
from datetime import datetime
from io import BytesIO
from itertools import groupby

from PIL import Image, ImageDraw, ImageFont

import matplotlib.pyplot as plt

from . import cfg

log_regex = re.compile(r'(?P<datetime>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \[(?P<loglvl>INFO|WARNING|ERROR|DEBUG)\] (?P<file>[\w\W_]+):(?P<function>[a-zA-Z_]+) (?P<message>.+) - (?=(?:(?P<extras>.+))$)?')


class MetricsCollector:

    def __init__(self, logfile):
        self.figsize = (8, 4)
        self._section_font = ImageFont.truetype(cfg.font_path, 40)

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
                data[player][turn + 1].append(value)
        data['turn'] = self.turns
        return data

    def aggregate_events_for_players(self, events, agg):
        """
        Perform aggregation (count, sum, avg, etc) to events metrics for each player
        ``events`` is the output of ``get_events_for_players``
        """
        data = {player: [agg(m) for m in metrics]
                for player, metrics in events.items() if player != 'turn'}
        data['turn'] = events['turn']
        return data

    def plot_metrics_for_players(self, metrics, title, ylabel):
        fig, axs = plt.subplots(figsize=self.figsize)
        available_players_colors = ['#EE302F', '#50A8E0']
        for player in (p for p in metrics.keys() if p != 'turn'):
            color = available_players_colors.pop()
            axs.plot(metrics['turn'], metrics[player], color=color)
        axs.set_xlabel('')
        axs.set_ylabel(ylabel, fontsize=16)
        axs.set_title(title, fontdict={'fontsize': 24})

        buf = BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img = Image.open(buf)
        return img

    def plot_section(self, title, charts, rows, columns, header_height):
        """
        Plot a section of metrics.
        The charts are drawed in mosaic acording to ``rows`` and ``columns``
        """
        sample_chart = charts[0]
        margin_botom = 20
        section_size = (sample_chart.width*columns,
                        sample_chart.height*rows + header_height + margin_botom)
        image = Image.new('RGB', section_size, 'white')
        draw = ImageDraw.Draw(image)
        draw.text((20, 40), title, font=self._section_font, fill='black')

        x = 0
        y = header_height
        for chart in charts:
            image.paste(chart, (x, y))
            x += chart.width
            if x == chart.width*columns:
                x = 0
                y += chart.height

        return image

    def build_sections(self):
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


        sections = []

        score = {
            'title': "Score",
            'charts': []
        }
        score['charts'].append(
            self.plot_metrics_for_players(planet_scores, "Planets Score", "Planets")
        )
        score['charts'].append(
            self.plot_metrics_for_players(carriers_scores, "Carriers", "Carriers") \
        )
        score['charts'].append(
            self.plot_metrics_for_players(warships_scores, "War Ships", "War Ships") \
        )
        score['charts'].append(
            self.plot_metrics_for_players(ships_scores, "Total Ships", "Total Ships") \
        )
        sections.append(score)

        combat = {
            'title': "Combat",
            'charts': []
        }
        combat['charts'].append(
            self.plot_metrics_for_players(
                conquered_planets, "Conquered Planets", "Conquered planets") \
        )
        combat['charts'].append(
            self.plot_metrics_for_players(killed_clans, "Killed clans", "Killed clans") \
        )
        combat['charts'].append(
            self.plot_metrics_for_players(ships_lost, "Ships lost", "Ships lost") \
        )
        sections.append(combat)


        economy = {
            'title': "Economy",
            'charts': []
        }
        economy['charts'].append(
            self.plot_metrics_for_players(
                total_dpythonium, "Extracted pythonium", "Extracted pythonium") \
        )
        economy['charts'].append(
            self.plot_metrics_for_players(
                total_dclans, "Population growth", "Population growth") \
        )
        economy['charts'].append(
            self.plot_metrics_for_players(
                total_dmegacredits, "Collected megacredits", "Collected megacredits") \
        )
        economy['charts'].append(
            self.plot_metrics_for_players(built_ships, "Built Ships", "Built ships") \
        )
        economy['charts'].append(
            self.plot_metrics_for_players(built_mines, "Built Mines", "Built mines") \
        )
        economy['charts'].append(
            self.plot_metrics_for_players(
                avg_dpythonium, "Avg extracted pythonium", "Pythonium") \
        )
        economy['charts'].append(
            self.plot_metrics_for_players(avg_dclans, "Avg population growth", "Clans") \
        )
        economy['charts'].append(
            self.plot_metrics_for_players(
                avg_dmegacredits, "Avg collected megacredits", "Megacredits") \
        )
        sections.append(economy)

        execution = {
            'title': "Execution",
            'charts': []
        }
        execution['charts'].append(
            self.plot_metrics_for_players(turns_runtime, "Execution Time", "Execution time") \
        )
        execution['charts'].append(
            self.plot_metrics_for_players(player_actions, "Actions", "Actions") \
        )
        sections.append(execution)

        return sections

    def build_report(self):
        """
        Build the report with all the metrics
        """
        sections = self.build_sections()

        sections_imgs = []
        header_height = 100
        for section in sections:
            charts_count = len(section['charts'])
            if charts_count == 8:
                rows = 2
                columns = 4
            elif charts_count == 4:
                rows = 1
                columns = 4
            elif charts_count == 3:
                rows = 3
                columns = 1
            elif charts_count == 2:
                rows = 1
                columns = 2
            elif charts_count == 1:
                rows = 1
                columns = 1
            img = self.plot_section(
                section['title'],
                section['charts'],
                rows,
                columns,
                header_height)
            img.save(f"{section['title']}.png")
            sections_imgs.append(img)

        return sections_imgs
