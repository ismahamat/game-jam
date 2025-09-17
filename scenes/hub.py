import arcade
from .base import BaseView
from .alien import AlienView

class HubView(BaseView):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.DARK_BROWN

    def on_draw(self):
        super().on_draw()
        self.show_text_center("Hub - Press A to enter a micro-game, ESC for Menu")

    def on_key_press(self, key: int, modifiers: int):
        if not self.window:
            return
        key_to_view = {
            arcade.key.KEY_1: ("atom", "AtomView"),
            arcade.key.KEY_2: ("ant", "AntView"),
            arcade.key.KEY_3: ("human_dog", "HumanDogView"),
            arcade.key.KEY_4: ("alien", "AlienView"),
            arcade.key.KEY_5: ("moon_ship", "MoonShipView"),
            arcade.key.KEY_6: ("galaxy", "GalaxyView"),
            arcade.key.KEY_7: ("universe", "UniverseView"),
        }
        if key  == arcade.key.A:
            self.window.show_view(AlienView())
        elif key == arcade.key.ESCAPE:
            from .menu import MenuView
            self.window.show_view(MenuView())


