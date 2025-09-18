import arcade
from .base import BaseView


class MenuView(BaseView):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.DARK_GREEN

    def on_draw(self):
        super().on_draw()
        self.show_text_center("Out Of Scale - Press Enter to play ")

    def on_key_press(self, key: int, modifiers: int):
        if not self.window:
            return
        if key == arcade.key.ENTER:
            from .atom import AtomView
            self.window.show_view(AtomView)
        if key == arcade.key.ESCAPE:
            from .main_menu import MainMenuView
            self.window.show_view(MainMenuView())


