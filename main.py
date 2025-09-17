import arcade
from scenes import MainMenuView

# Dimensions de la fenêtre
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
SCREEN_TITLE = "OUT OF SCALE"

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):
        """Initialisation du jeu"""
        pass

    def on_draw(self):
        """Affichage des éléments"""
        self.clear()
        arcade.draw_text("Hello Arcade!", 100, 300, arcade.color.WHITE, 24)

    def on_update(self, delta_time):
        """Logique du jeu (appelé 60 fois/sec)"""
        pass

    def on_key_press(self, key, modifiers):
        """Quand une touche est pressée"""
        if key == arcade.key.SPACE:
            print("Espace pressé !")

def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_view(MainMenuView())  # setup sera appelé automatiquement
    arcade.run()
    
if __name__ == "__main__":
    main()
