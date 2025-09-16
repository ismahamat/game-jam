import arcade
from .base import BaseView


class MainMenuView(BaseView):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.DARK_SLATE_BLUE

    def on_show_view(self):
        super().on_show_view()

    def on_draw(self):
        super().on_draw()
        self.show_text_center("Main Menu - Press ENTER to Start")

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.ENTER and self.window:
            from .menu import MenuView
            self.window.show_view(MenuView())


