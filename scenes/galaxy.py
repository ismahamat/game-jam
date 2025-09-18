import arcade
from pathlib import Path

from .UniversDialogueScene import UniversDialogueScene
from .base import BaseView

PATH = Path(__file__).resolve().parent.parent / "assets" 

class GalaxyView(BaseView):
    def __init__(self):
        super().__init__()
        self.background_list = arcade.SpriteList()  
        self.planet_list = arcade.SpriteList()  
        self.directions = []
        self.selected_index = 1 
        self.planet_names = ["Planète Yotz ", "Planète Bovi", "Planète Sed"]
        self.planet_desc = ["Discrète, isolée, mais connue pour ses technologies d’espionnage très avancées.", 
                             "Riche en ressources, ambitieuse, et souvent impliquée dans des conflits territoriaux.", 
                             "Pacifique en apparence, mais dont les archives montrent des alliances secrètes… avec des puissances douteuses."]
        self.alien = arcade.SpriteList()  
        self.arrow_list = arcade.SpriteList()    
        self.selected_index = 0  # planète actuellement sélectionnée

    def setup(self): 
        self.background_list = arcade.SpriteList()  
        self.planet_list = arcade.SpriteList()  
        self.arrow_list = arcade.SpriteList()  
        self.alien = arcade.SpriteList()  
        self.directions = []

        bg = arcade.Sprite(str(PATH / "galaxy.png"), scale=1)
        bg.center_x = 0
        bg.center_y = 0
        self.background_list.append(bg)

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

        # --- création flèche ---
        arrow1 = arcade.Sprite(str(PATH / "down_arrow.png"), scale=0.1)
        arrow1.center_x = 400
        arrow1.center_y = 600
        self.arrow_list.append(arrow1)
        self.directions.append(1)
        arrow2 = arcade.Sprite(str(PATH / "down_arrow.png"), scale=0.1)
        arrow2.center_x = 600
        arrow2.center_y = 600
        arrow2.visible = False
        self.arrow_list.append(arrow2)
        self.directions.append(-1)
        arrow3 = arcade.Sprite(str(PATH / "down_arrow.png"), scale=0.1)
        arrow3.center_x = 800
        arrow3.center_y = 600
        arrow3.visible = False
        self.arrow_list.append(arrow3)
        self.directions.append(-1)

        # --- création alien ---
        alien1 = arcade.Sprite(str(PATH / "alien_spaceship_no_fire.png"), scale=0.075)
        alien1.center_x = 150
        alien1.center_y = 400
        alien1.visible = True
        self.alien.append(alien1)

    def on_draw(self):
        super().on_draw()
        self.background_list.draw()
        self.planet_list.draw()
        self.arrow_list.draw()
        self.alien.draw()
        if self.planet_names:
            arcade.draw_text(
            self.planet_names[self.selected_index],
        600,  # fixed under the middle planet
        60,
        arcade.color.WHITE,
        20,
        anchor_x="center"
        )
        if self.planet_desc:
            arcade.draw_text(
            self.planet_desc[self.selected_index],
            600,  # fixed under the middle planet
            30,
            arcade.color.WHITE,
            10,
            anchor_x="center"
        )


    def on_update(self, delta_time):
        """Idle animation : haut/bas des planètes"""
        for i, planet in enumerate(self.planet_list):
            planet.center_y += self.directions[i] * 0.5
            if planet.center_y > 420:
                self.directions[i] = -1
            elif planet.center_y < 380:
                self.directions[i] = 1
        
    def on_key_press(self, key, modifiers):
    # hide current arrow
        self.arrow_list[self.selected_index].visible = False

    # Update selection
        if key == arcade.key.LEFT:
            if self.selected_index > 0:
                self.selected_index -= 1
        elif key == arcade.key.RIGHT:
            if self.selected_index < len(self.planet_list) - 1:
                self.selected_index += 1

    # Explode other planets
        if key == arcade.key.ENTER:
            for i, planet in enumerate(self.planet_list):
                if i != self.selected_index:
                    planet.texture = arcade.load_texture(str(PATH / "explosion.png"))
                    planet.scale = 1
            self.alien[0].texture = arcade.load_texture(str(PATH / "alien_spaceship.png"))
            self.planet_names = ["HAHAHHAHA","HAHAHHAHA","HAHAHHAHA"]
            self.planet_desc = ["","",""]
            self.window.show_view(UniversDialogueScene())
        else:
            # Show arrow on selected planet
            self.arrow_list[self.selected_index].visible = True