import arcade
from arcade.gui import UIManager, UIAnchorLayout, UIGridLayout, UIFlatButton
from .galaxy import GalaxyView

class PopupView(arcade.View):
    def __init__(self, parent_view, win=True):
        super().__init__()
        self.parent_view = parent_view
        self.win = win  # True si partie gagnée, False si perdue

        # UI Manager
        self.ui = UIManager()
        self.ui.enable()

        # --- Fond image ---
        self.background_sprite_list = arcade.SpriteList()
        self.background = arcade.Sprite("assets/alien-world-sunset.png")
        self.background.center_x = self.window.width / 2
        self.background.center_y = self.window.height / 2
        self.background.width = self.window.width
        self.background.height = self.window.height
        self.background_sprite_list.append(self.background)

        # --- Boutons ---
        grid = UIGridLayout(column_count=1, row_count=2, vertical_spacing=20)

        next_btn = UIFlatButton(text="Jeu suivant", width=200)
        next_btn.on_click = self.on_next_click
        grid.add(next_btn, row=0, column=0)

        quit_btn = UIFlatButton(text="Quitter", width=200)
        quit_btn.on_click = self.on_quit_click
        grid.add(quit_btn, row=1, column=0)

        self.ui.add(UIAnchorLayout(children=[grid]))

    def on_draw(self):
        self.clear()

        # Dessiner le fond
        self.background_sprite_list.draw()

        # Afficher le message selon le résultat
        message = "Partie Gagnée !" if self.win else "Partie Perdue..."
        arcade.draw_text(
            message,
            self.window.width / 2,
            self.window.height / 2 + 200,
            arcade.color.BABY_POWDER,
            font_size=60,
            anchor_x="center",
            anchor_y="center"
        )

        # Dessiner les boutons
        self.ui.draw()

    def on_next_click(self, event):
        print("👉 Jeu suivant")
        self.window.show_view(GalaxyView())

    def on_quit_click(self, event):
        print("👉 Quitter")
        arcade.exit()
