import configparser
import os

from .logger import get_logger

LOGGER = get_logger(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Move this settings to config.ini
tenacity = 0.25
happypoints_tolerance = 40
optimal_temperature = 50
max_population_rate = 0.1
tolerable_taxes = 10
ship_speed = 80
planet_max_mines = 500
taxes_collection_factor = 0.2
max_clans_in_planet = 10000
font_path = "font/jmh_typewriter.ttf"


def load_config(namespace="DEFAULT", base_dir=BASE_DIR):
    config_file = os.path.join(base_dir, "config.ini")
    # This is for local deploy with a config file
    config = configparser.ConfigParser()
    config.read(config_file)
    LOGGER.info(
        "Configuration loaded from config file", extra={"file": config_file}
    )
    return config[namespace]
