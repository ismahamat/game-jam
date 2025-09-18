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
        grid = UIGridLayout(column_count=1, 
                            row_count=2, 
                            vertical_spacing=20
        )

        next_btn = UIFlatButton(
            x = self.window.width / 2 + 100,
            y = self.window.height / 2 + 300,

            text="Jeu suivant", 
            width=200,
            style={
                'normal': UIFlatButton.UIStyle(
                    font_size=20,
                    font_name=('calibri', 'arial'),
                    font_color=arcade.color.WHITE,
                    bg=arcade.color.BLACK,
                    border=arcade.color.WHITE,
                    border_width=2,
                ),
                'hover': UIFlatButton.UIStyle(
                    font_size=20,
                    font_name=('calibri', 'arial'),
                    font_color=arcade.color.BLACK,
                    bg=arcade.color.WHITE,
                    border=arcade.color.BLACK,
                    border_width=2,
                ),
            }
        )
        next_btn.on_click = self.on_next_click
        grid.add(next_btn, row=0, column=0)

        quit_btn = UIFlatButton(
            text="Quitter", 
            width=200,
            x = self.window.width / 2 + 150,
            y = self.window.height / 2 + 350,
            style={
                'normal': UIFlatButton.UIStyle(
                    font_size=20,
                    font_name=('calibri', 'arial'),
                    font_color=arcade.color.WHITE,
                    bg=arcade.color.BLACK,
                    border=arcade.color.WHITE,
                    border_width=2,
                ),
                'hover': UIFlatButton.UIStyle(
                    font_size=20,
                    font_name=('calibri', 'arial'),
                    font_color=arcade.color.BLACK,
                    bg=arcade.color.WHITE,
                    border=arcade.color.BLACK,
                    border_width=2,
                ),
            }
        )
        quit_btn.on_click = self.on_quit_click
        grid.add(quit_btn, row=1, column=0)
        
        self.ui.add(
            UIAnchorLayout(
                children=[grid],
                anchor_x="center",    # Centrer horizontalement
                anchor_y="center",    # Centrer verticalement
                offset_y=-150         # <- descendre la grille de 150 pixels
            )
        )

    def on_draw(self):
        self.clear()

        # Dessiner le fond
        self.background_sprite_list.draw()

        # Afficher le message selon le résultat
        message = "Partie Gagnée !" if self.win else "Partie Perdue..."
        arcade.draw_text(
            message,
            self.window.width / 2,
            self.window.height / 2 + 260,
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
