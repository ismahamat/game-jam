import os
import arcade
from .base import BaseView  # BaseView doit hériter de arcade.View
from .atom import AtomView

# --- Constantes ---
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Fourmi Dialogue Scene"

ALIEN_SCALE = 0.5
DIALOGUE_BOX_HEIGHT = 150
TEXT_MARGIN = 20

PARAGRAPHS = [
    "[Transmission interstellaire établie…]",
    "Bonjour, ami et voyageur de l’univers numérique. Je suis Dokkae, explorateur paisible venu du système stellaire de Ganul.",
    "Je suis ici non pas pour te défier… mais pour t’accompagner et t’aider dans ton aventure :)",
    "Pour t’expliquer un peu la situation, tu dois compléter une série d'épreuves pour pouvoir te permettre de découvrir les secrets de l’univers.",
    "Ne t'inquiète pas, je serais à tes côtés à chaque instant pour te donner toutes les indications nécessaires.",
    "Le premier défi ? Placer les électrons d’un atome dans la bonne orbite autour du noyau, sans te faire toucher par les électrons libres qui bougent partout ! Sois rapide, mais calme, et surtout, n’aie pas peur d’essayer plusieurs fois.",
    "Je sais que ce n’est pas toujours facile, mais tu n’es pas seul. Moi aussi, la première fois, j’ai pris un électron libre en pleine antenne... 😅 On va y arriver ensemble !",
]


class FourmiDialogueScene(BaseView):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLUEBERRY)

        self.current_paragraph_index = 0

        # SpriteList pour l'alien
        self.sprites = arcade.SpriteList()
        self.alien_sprite: arcade.Sprite | None = None

        # Textes
        self.dialog_text = arcade.Text(
            PARAGRAPHS[0],
            x=SCREEN_WIDTH / 2,  # début au centre horizontalement
            y=TEXT_MARGIN + (DIALOGUE_BOX_HEIGHT - TEXT_MARGIN * 2) / 2,  # centré verticalement dans la boîte
            color=arcade.color.WHITE,
            font_size=18,
            width=SCREEN_WIDTH - 2 * TEXT_MARGIN,
            align="center",
            anchor_x="center",
            anchor_y="center",
            multiline=True,
        )
        self.hint_text = arcade.Text(
            "[Espace/Entrée/Droite] Suivant",
            x=SCREEN_WIDTH / 2,
            y=TEXT_MARGIN,
            color=arcade.color.LIGHT_GRAY,
            font_size=12,
            anchor_x="center",
        )

        self._is_setup = False
        self._done = False  # pour savoir si tous les paragraphes ont été affichés

    def on_show_view(self):
        if not self._is_setup:
            self.setup()

    def setup(self):
        self._is_setup = True

        sprite_path = "assets/alien.png"
        if os.path.isfile(sprite_path):
            self.alien_sprite = arcade.Sprite(sprite_path, ALIEN_SCALE)
        else:
            self.alien_sprite = arcade.SpriteSolidColor(80, 80, arcade.color.AVOCADO)

        # On centre horizontalement, et place verticalement au milieu entre haut de la fenêtre et début de la boîte de dialogue
        self.alien_sprite.center_x = SCREEN_WIDTH / 2
        # hauteur disponible = SCREEN_HEIGHT - DIALOGUE_BOX_HEIGHT
        self.alien_sprite.center_y = (SCREEN_HEIGHT + DIALOGUE_BOX_HEIGHT) / 2

        self.sprites.append(self.alien_sprite)


    def on_draw(self):
        self.clear()
        self.sprites.draw()
        self.draw_dialogue_box()

    def draw_dialogue_box(self):
        arcade.draw_lbwh_rectangle_filled(
            0, 0, SCREEN_WIDTH, DIALOGUE_BOX_HEIGHT, (50, 50, 50, 220)
        )
        arcade.draw_lbwh_rectangle_outline(
            0, 0, SCREEN_WIDTH, DIALOGUE_BOX_HEIGHT, arcade.color.LIGHT_GRAY, border_width=2
        )

        # dessiner le texte centré dans la boîte
        self.dialog_text.draw()
        # dessiner le hint
        self.hint_text.draw()

    def on_key_press(self, key: int, modifiers: int):
        if self._done:
            # Si le dialogue est terminé, passer à la scène AtomView
            if key in (arcade.key.SPACE, arcade.key.ENTER, arcade.key.RIGHT):
                atom_view = AtomView()
                atom_view.setup()
                self.window.show_view(atom_view)
            return
        
        if key == arcade.key.ENTER:
            from .human_dog import HumanDogView
            self.window.show_view(HumanDogView())

        if key in (arcade.key.SPACE, arcade.key.ENTER, arcade.key.RIGHT):
            self.current_paragraph_index += 1
            if self.current_paragraph_index >= len(PARAGRAPHS):
                # Si on dépasse le nombre, on reste sur le dernier paragraphe
                self.current_paragraph_index = len(PARAGRAPHS) - 1
                self._done = True  # marque que le dialogue est fini
                # Mettre à jour le texte d'aide pour indiquer comment continuer
                self.hint_text.value = "[Espace/Entrée/Droite] Commencer le jeu"
            self.dialog_text.value = PARAGRAPHS[self.current_paragraph_index]


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = FourmiDialogueScene()
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()