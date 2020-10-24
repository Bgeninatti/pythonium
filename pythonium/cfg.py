import os

tenacity = .25
happypoints_tolerance = 40
optimal_temperature = 50
max_population_rate = 0.1
tolerable_taxes = 10
mine_cost = (2, 5) # (mc, p)
ship_speed = 80
planet_max_mines = 500
taxes_collection_factor = .2
max_clans_in_planet = 10000

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
font_path = os.path.join(base_path, 'font', 'jmh_typewriter.ttf')
