import os
from . import cfg
from PIL import ImageFont

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(BASE_PATH, cfg.font_path)


def load_font(fontsize):
    # `layout_engine=ImageFont.LAYOUT_BASIC` fix an OSError while writintg text with Pillow
    return ImageFont.truetype(FONT_PATH,
                              fontsize,
                              layout_engine=ImageFont.LAYOUT_BASIC)
