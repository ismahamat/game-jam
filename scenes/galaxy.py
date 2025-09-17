import arcade
from pathlib import Path
from .base import BaseView

PATH = Path(__file__).resolve().parent.parent / "assets" 


class GalaxyView(BaseView):
    def __init__(self):
        super().__init__()
        self.planet_list = arcade.SpriteList()  
        self.directions = []
        self.alien = arcade.SpriteList()  

    def setup(self): 
        self.planet_list = arcade.SpriteList()  
        self.alien = arcade.SpriteList()  
        self.directions = []

        # --- création planètes ---
        planet = arcade.Sprite(str(PATH / "planet.png"), scale=0.1)
        planet.center_x = 400
        planet.center_y = 400
        self.planet_list.append(planet)
        self.directions.append(-1)  

        planet1 = arcade.Sprite(str(PATH / "planet_rose.png"), scale=0.1)
        planet1.center_x = 600
        planet1.center_y = 400
        self.planet_list.append(planet1)
        self.directions.append(1)

        planet2 = arcade.Sprite(str(PATH / "planet_verte.png"), scale=0.1)
        planet2.center_x = 800
        planet2.center_y = 400
        self.planet_list.append(planet2)
        self.directions.append(-1)  

        # --- création alien ---
        alien1 = arcade.Sprite(str(PATH / "alien_spaceship_no_fire.png"), scale=0.075)
        alien1.center_x = 150
        alien1.center_y = 400
        self.alien.append(alien1)

    def on_draw(self):
        super().on_draw()
        self.planet_list.draw()
        self.alien.draw()

    def on_update(self, delta_time):
        """Idle animation : haut/bas des planètes"""
        for i, planet in enumerate(self.planet_list):
            planet.center_y += self.directions[i] * 0.5
            if planet.center_y > 420:
                self.directions[i] = -1
            elif planet.center_y < 380:
                self.directions[i] = 1
