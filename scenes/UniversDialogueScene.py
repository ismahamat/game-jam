import os
import arcade
from .base import BaseView  # BaseView doit hériter de arcade.View


# --- Constantes ---
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Alien Dialogue Scene"

ALIEN_SCALE = 0.5
DIALOGUE_BOX_HEIGHT = 150
TEXT_MARGIN = 20

PARAGRAPHS = [
    "Tu ne voulais pas la garder planète ? Oh non mince, j’ai mal compris ce que tu voulais dire. Après ce n’était pas une planète qui te tenait à cœur, si ?",
    "Ne t’en fais pas, le jeu n’est pas encore terminé !",
    "Pour la prochaine épreuve, tu dois à tout prix éviter la collision des deux trous noirs en cliquant sur espace. Tu dois tenir 20 secondes pour pouvoir survivre ! Je compte sur toi, l’avenir de l’univers repose sur toi !",
    "BOOOOM ",
    "Oh… euh… tu ne voulais pas qu’on garde la planète, hein ?",
    "…Oh non… Attends, j’ai mal compris ce que tu voulais dire ? Tu voulais dire que la planète responsable était le [NomPlanèteChoisi]… et pas les deux autres ?! ",
    "Aïe.",
    "Bon… après tout, ce n’était pas comme si ces planètes comptaient vraiment pour toi… si ? Non ?",
    "Écoute, pas de panique. Le jeu n’est pas encore terminé, et l’univers est encore récupérable.",
    "Et justement, pour redresser tout ça, j’ai une mission cruciale pour toi.",
    "Deux trous noirs sont en train de dériver dangereusement l’un vers l’autre.",
    "Leur collision provoquerait une réaction en chaîne… capable de déchirer l’espace-temps sur 42 dimensions. Autrement dit : gros problème.",
    "Ta tâche :",
    "Appuie sur espace au bon moment pour éviter leur collision, encore et encore.",
    "Tiens bon pendant 20 secondes. Pas une de moins.",
    "Ta précision et ton sang-froid sont la dernière ligne de défense.",
    "Je compte sur toi.",
    "L’avenir de l’univers repose sur toi.",
    "Et cette fois… essaie de ne pas faire exploser quoi que ce soit, d’accord ?",
]

class UniversDialogueScene(BaseView):
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
                from .universe import UniverseView
                self.window.show_view(UniverseView())
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