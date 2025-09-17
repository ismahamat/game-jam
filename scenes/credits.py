from typing import Optional
import arcade

from .base import BaseView


class CreditsView(BaseView):
    def __init__(self):
        super().__init__()
        self.background_color = (10, 12, 16)
        self._title: Optional[arcade.Text] = None
        self._sections: list[list[arcade.Text]] = []
        self._hint: Optional[arcade.Text] = None
        self._rules: Optional[arcade.Text] = None

        # Données de crédits
        self.game_name = "OUT OF SCALE"
        self.team = [
            "MAHAMAT Issa",
            "LETELLIER Aymeric",
            "PREVOT Maxime",
            "ZHAN Isabelle",
            "LEFEVRE Grégoire",
        ]
        self.instructors = [
            "Rémi Forax",
            "Nicolas Borie",
        ]
        self.meta = {
            "jam": "Game Jam ESIEE 2025",
            "theme": "Vous n'êtes pas au centre de l'histoire",
            "school": "ESIEE Paris",
        }
        self.tech = ["Python 3.13", "Arcade"]
        self.art = ["Sprites et UI: Équipe Groupe 15"]
        self.thanks = ["Merci à l'équipe pédagogique et aux assistants"]

    def _build_texts(self):
        if not self.window:
            return

        w, h = self.window.width, self.window.height
        self._sections.clear()

        # Sections à afficher
        content = [
            ("Développement", self.team),
            ("Encadrement", self.instructors),
            ("À propos", [f"{self.meta['jam']} - {self.meta['school']}",
                          f"Thème: {self.meta['theme']}"]),
            ("Technologies", self.tech),
            ("Art et UI", self.art),
            ("Remerciements", self.thanks),
        ]

        # Compter toutes les lignes (titres + contenus)
        total_lines = sum(1 + len(lines) for _, lines in content)

        # Calculer taille dynamique
        available_height = h * 0.65  # espace vertical entre titre et footer
        line_spacing = available_height / (total_lines + 1)
        font_size = min(int(line_spacing * 0.7), 28)  # cap à 28 pour lisibilité

        # Titre
        self._title = arcade.Text(
            f"Crédits - {self.game_name}",
            w / 2,
            h * 0.9,
            arcade.color.ANTIQUE_WHITE,
            font_size=max(32, int(h * 0.05)),
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )

        # Construire sections
        y = h * 0.8
        self._sections.clear()
        for section_title, lines in content:
            block: list[arcade.Text] = []
            block.append(
                arcade.Text(
                    section_title,
                    w / 2,
                    y,
                    arcade.color.LIGHT_STEEL_BLUE,
                    font_size=font_size + 2,
                    anchor_x="center",
                    anchor_y="center",
                    bold=True,
                )
            )
            y -= line_spacing
            for line in lines:
                block.append(
                    arcade.Text(
                        line,
                        w / 2,
                        y,
                        arcade.color.ANTIQUE_WHITE,
                        font_size=font_size,
                        anchor_x="center",
                        anchor_y="center",
                    )
                )
                y -= line_spacing
            self._sections.append(block)

        # Indications bas écran
        self._hint = arcade.Text(
            "ESC: retour",
            w / 2,
            h * 0.08,
            arcade.color.ANTIQUE_WHITE,
            font_size=max(14, int(h * 0.025)),
            anchor_x="center",
            anchor_y="center",
        )


    def on_show_view(self):
        super().on_show_view()
        self._build_texts()

    def on_resize(self, width: int, height: int):
        self._build_texts()

    def on_draw(self):
        super().on_draw()
        arcade.set_background_color(self.background_color)
        if self._title:
            self._title.draw()
        for section in self._sections:
            for text in section:
                text.draw()
        if self._hint:
            self._hint.draw()
        if self._rules:
            self._rules.draw()

    def on_key_press(self, key: int, modifiers: int):
        if not self.window:
            return
        if key == arcade.key.ESCAPE :
            from .main_menu import MainMenuView
            self.window.show_view(MainMenuView())