import os
import arcade
from .base import BaseView  # BaseView doit hériter de arcade.View


# --- Constantes ---
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Galaxy Dialogue Scene"

ALIEN_SCALE = 0.5
DIALOGUE_BOX_HEIGHT = 150
TEXT_MARGIN = 20

PARAGRAPHS = [
    "Super ! Tu l’as trouvé ! Grâce à toi, j’ai pu transmettre mon message sans le moindre accroc et il m’a même répondu en un éclair… chose rare, vu sa lenteur habituelle. ",
    "Je te remercie infiniment, ami voyageur. Sans toi, ce contact aurait été perdu.",
    "Mais… ce qu’il m’a révélé est très inquiétant.",
    "Il m’a transmis une information capitale : une guerre interplanétaire est en train de se préparer, dans l’ombre.",
    "Quelqu’un, ou quelque chose, manipule les tensions entre civilisations, et le conflit pourrait éclater à tout moment… entraînant des milliers de mondes dans le chaos.",
    "Nous devons agir vite. Et pour cela, j’ai besoin de ton intuition, de ton raisonnement, et surtout, de ton jugement impartial.",
    "Trois planètes sont soupçonnées d’être à l’origine de cette instabilité :",
    "Planète Yotz – Discrète, isolée, mais connue pour ses technologies d’espionnage très avancées.",
    "Planète Bovi – Riche en ressources, ambitieuse, et souvent impliquée dans des conflits territoriaux.",
    "Planète Sed – Pacifique en apparence, mais dont les archives montrent des alliances secrètes… avec des puissances douteuses.",
    "Alors dis-moi… laquelle de ces planètes suspectes penses-tu qu’il faut surveiller en priorité ?",
    "Réfléchis bien. Ton choix déterminera la suite de notre mission… et peut-être l’avenir de la galaxie.",
]



class GalaxyDialogueScene(BaseView):
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
            "[Entrée galaxie] Suivant",
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
            if (key == arcade.key.ENTER):
                from .galaxy import GalaxyView
                self.window.show_view(GalaxyView())
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