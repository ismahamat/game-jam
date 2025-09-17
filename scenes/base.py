import arcade


class BaseView(arcade.View):
    """Base class for all game Views.

    Provides common lifecycle hooks and minimal shared behavior.
    Subclasses should override hooks as needed.
    """

    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.BLACK
        
    def setup(self):
        """Méthode de préparation de la vue (par défaut ne fait rien).
        Les sous-classes peuvent la surcharger.
        """
        pass

    # ----- Lifecycle -----
    def on_show_view(self):
        """Appelé automatiquement quand la vue devient active"""
        self.setup()  # <-- chaque sous-classe peut surcharger setup()
        arcade.set_background_color(self.background_color)
        if self.window:
            self.window.set_mouse_visible(True)

    def on_draw(self):
        self.clear()

    def on_update(self, delta_time: float):
        pass

    # ----- Input -----
    def on_key_press(self, key: int, modifiers: int):
        pass

    def on_key_release(self, key: int, modifiers: int):
        pass

    # ----- Utility -----
    def show_text_center(self, text: str, color: arcade.color = arcade.color.WHITE, size: int = 24):
        width = self.window.width if self.window else 800
        height = self.window.height if self.window else 600
        arcade.draw_text(
            text,
            width / 2,
            height / 2,
            color,
            font_size=size,
            anchor_x="center",
            anchor_y="center",
        )
