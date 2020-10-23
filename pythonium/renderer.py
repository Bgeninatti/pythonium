
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

from . import cfg


class GifRenderer:

    available_players_colors = [(238, 48, 47, 256), (80, 168, 224, 256)]
    def __init__(self, galaxy, title=None, speed=200):
        self.galaxy = galaxy
        self.speed = speed
        self.title = title
        self.background_color = (40, 40, 40)
        self._frames = []
        self.players_colors = {p: self.available_players_colors.pop()
                               for p in galaxy.known_races}
        self.planet_color = (256, 256, 256, 256)
        self.explosion_color = (200, 157, 78, 256)
        self.header = 200
        self.margin = 10
        self.footer = 30
        self._title_font = ImageFont.truetype(cfg.font_path, 40)
        self._score_font = ImageFont.truetype(cfg.font_path, 24)
        self._footer_font = ImageFont.truetype(cfg.font_path, 10)
        self.frame_size = (self.galaxy.size[0] + self.margin,
                           self.galaxy.size[1] + self.header)
        self.plantet_radius = 3
        self.ships_radius = 5

    def galaxy2frame_coordinates(self, coordinates):
        return (coordinates[0] + 10, coordinates[1] + self.header - self.margin)

    def render_frame(self, context):
        frame = Image.new('RGB', self.frame_size, self.background_color)
        draw = ImageDraw.Draw(frame, 'RGBA')

        if self.title:
            self.render_title(draw)

        self.render_score(draw, context)

        # Plot explosions
        for explosion in self.galaxy.explosions:
            self.render_explosion(draw, explosion)

        # Plot planets
        for planet in self.galaxy.planets.values():
            self.render_planet(draw, planet)

        # Plot ships
        for ship in self.galaxy.ships:
            self.render_ship(draw, ship)

        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        draw.text((self.margin, self.frame_size[1] - 10),
                  f"github.com/Bgeninatti/pythonium - {now}",
                  font=self._footer_font)

        self._frames.append(frame)

    def render_title(self, draw):
        draw.text((self.margin, self.margin),
                  self.title,
                  font=self._title_font)

    def render_score(self, draw, context):
        # TODO: Fix this insanity of column and rows coordinates for text
        draw.text((self.margin, self.margin + 50),
                  f"Turn {context['turn']}",
                  font=self._score_font)

        draw.text((self.margin, self.margin + 90),
                  "Planets",
                  font=self._score_font)

        draw.text((self.margin, self.margin + 130),
                  "Ships",
                  font=self._score_font)

        score = context.get('score')

        for i, player_score in enumerate(score):
            color = self.players_colors.get(player_score['player'])
            draw.text((self.margin + (i + 1)*170, self.margin + 50),
                      player_score['player'],
                      font=self._score_font,
                      fill=color)
            draw.text((self.margin + (i + 1)*170, self.margin + 90),
                      str(player_score['planets']),
                      font=self._score_font)
            draw.text((self.margin + (i + 1)*170, self.margin + 130),
                      str(player_score['total_ships']),
                      font=self._score_font)

    def render_planet(self, draw, planet):
        color = self.players_colors.get(planet.player, self.planet_color)
        centroid = self.galaxy2frame_coordinates(planet.position)
        bounding_box = (
            (centroid[0] - self.plantet_radius, centroid[1] - self.plantet_radius),
            (centroid[0] + self.plantet_radius, centroid[1] + self.plantet_radius)
        )
        draw.ellipse(bounding_box, fill=color)

    def render_ship(self, draw, ship):
        color = self.players_colors.get(ship.player, self.planet_color)
        centroid = self.galaxy2frame_coordinates(ship.position)
        bounding_box = (
            (centroid[0] - self.ships_radius, centroid[1] - self.ships_radius),
            (centroid[0] + self.ships_radius, centroid[1] + self.ships_radius)
        )
        draw.ellipse(
            bounding_box,
            fill=(0, 0, 0, 0),
            outline=color,
            width=3
        )

    def render_explosion(self, draw, explosion):
        centroid = self.galaxy2frame_coordinates(explosion.ship.position)
        # Scale size based on ships amount
        radius = max(50, self.plantet_radius + int(explosion.ships_involved*0.5))
        draw.ellipse(((centroid[0] - radius, centroid[1] - radius),
                      (centroid[0] + radius, centroid[1] + radius)),
                     fill=self.explosion_color,
                     outline=self.explosion_color,
                     width=2)

    def save_gif(self, path):
        if not path.lower().endswith(".gif"):
            raise ValueError("Destination file must be a gif")
        image = self._frames[0]
        image.save(path,
                   save_all=True,
                   duration=self.speed,
                   append_images=self._frames)
        return

