import arcade
from .base import BaseView


class MenuView(BaseView):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.DARK_GREEN

    def on_draw(self):
        super().on_draw()
        self.show_text_center("Scale Selector - Press H for Hub")

    def on_key_press(self, key: int, modifiers: int):
        if not self.window:
            return
        if key == arcade.key.H:
            from .hub import HubView
            self.window.show_view(HubView())
        if key == arcade.key.ESCAPE:
            from .main_menu import MainMenuView
            self.window.show_view(MainMenuView())


