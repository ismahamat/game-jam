import os
import arcade
from .base import BaseView  # BaseView doit hériter de arcade.View
from .atom import AtomView

# --- Constantes ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Alien Dialogue Scene"

ALIEN_SCALE = 0.5
DIALOGUE_BOX_HEIGHT = 150
TEXT_MARGIN = 20

PARAGRAPHS = [
    "Oh non… mince. Te faire percuter comme ça, ça pique un peu, pour toi comme pour moi ! J’ai presque senti le choc jusque dans mes antennes. ",
    "Mais eh, ce n’est pas un échec. Juste une autre expérience de plus sur ton carnet d’explorateur.",
    "On va dire que l’incarnation physique, ce n’est pas encore ton truc… et ce n’est pas grave du tout ! Tu as d’autres qualités bien plus précieuses : ta mémoire, ton sens de l’observation, et ta capacité à garder ton calme dans le chaos.",
    "Et justement… c’est ce dont j’ai besoin maintenant.",
    "Écoute bien : l’un de mes confrères Ganuliens s’est égaré. Il était censé me retrouver pour une réunion importante sur notre planète… mais il s’est perdu dans une foule d’aliens lors d’un grand rassemblement interespèces sur Ganul, et je ne parviens plus à capter son signal précisément.",
    "J’ai besoin de toi, de tes yeux et de ton attention, pour m’aider à le retrouver. Je vais t’afficher sa photo dans un instant — garde bien son apparence en tête.",
    "Ta mission est de le repérer parmi tous les visages. Ignore les distractions, concentre-toi sur les détails. Il a un air un peu distrait, mais on l’aime bien. Et j’ai un message très important à lui faire passer.",
    "Tu es prêt ? Respire un bon coup, nettoie ta visière, et prépare-toi à scanner la foule.",
    "On compte sur toi… surtout lui, vu son sens de l’orientation.",
]


class AlienDialogueScene(BaseView):
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
            "[Entrée] Suivant",
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
            if key == arcade.key.ENTER:
                from .alien import AlienView
                self.window.show_view(AlienView())
            return

        if key == arcade.key.ENTER:
            self.current_paragraph_index += 1
            if self.current_paragraph_index >= len(PARAGRAPHS):
                # Si on dépasse le nombre, on reste sur le dernier paragraphe
                self.current_paragraph_index = len(PARAGRAPHS) - 1
                self._done = True  # marque que le dialogue est fini
                # Mettre à jour le texte d'aide pour indiquer comment continuer
                self.hint_text.value = "[Entrée] Commencer le jeu"
            self.dialog_text.value = PARAGRAPHS[self.current_paragraph_index]

def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = AtomDialogueScene()
    window.show_view(view)
    arcade.run()

if __name__ == "__main__":
    main()