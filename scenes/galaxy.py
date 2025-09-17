import arcade
from pathlib import Path
from .base import BaseView

PATH = Path(__file__).resolve().parent.parent / "assets" 

class GalaxyView(BaseView):
    def __init__(self):
        super().__init__()
        # Build the path to the asset
        self.texture = arcade.load_texture(str(PATH/"galaxy.png"))
        print(str(PATH/"galaxy.png")) 
        self.planet_list = arcade.SpriteList()  

    def setup(self) : 
        self.planet_list = arcade.SpriteList()  
        planet = arcade.Sprite(str(PATH /"planet.png"), scale=0.1)
        planet.center_x = 400
        planet.center_y = 400
        self.planet_list.append(planet)

    def on_draw(self):
        super().on_draw()
        # Draw the background
        #scale = .5
        #arcade.draw_texture_rect(
            #self.texture,
            #arcade.XYWH(0, 0, self.texture.width, self.texture.height).scale(scale)
        #)
        self.planet_list.draw()
        # Draw a circle as a placeholder planet
        #arcade.draw_circle_filled(320, 285, 100, arcade.color.GREEN)
        #arcade.draw_circle_filled(520, 285, 100, arcade.color.GREEN)
        #arcade.draw_circle_filled(720, 285, 100, arcade.color.GREEN)
