import os
import random
import string

from . import cfg


BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(BASE_PATH, cfg.font_path)


def random_name(length):
    characters = string.ascii_uppercase + string.digits
    return "".join([random.choice(characters) for _ in range(length)])
