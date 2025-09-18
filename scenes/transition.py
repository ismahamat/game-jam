import arcade

# --- Constantes ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Alien Dialogue Scene"

ALIEN_SCALE = 0.5
DIALOGUE_BOX_HEIGHT = 150
TEXT_MARGIN = 20

# Liste de paragraphes à afficher
PARAGRAPHS = [
    "[Transmission interstellaire établie…]" ,
    "Bonjour, ami et voyageur de l’univers numérique. Je suis Dokkae, explorateur paisible venu du système stellaire de Ganul.",
    "Je suis ici non pas pour te défier… mais pour t’accompagner et t’aider dans ton aventure :)",
    "Pour t’expliquer un peu la situation, tu dois compléter une série d'épreuves pour pouvoir te permettre de découvrir les secrets de l’univers. ",
    "Ne t'inquiète pas, je serais à tes côtés à chaque instant pour te donner toutes les indications nécessaires.",
    "Le premier défi ? Placer les électrons d’un atome dans la bonne orbite autour du noyau, sans te faire toucher par les électrons libres qui bougent partout ! Sois rapide, mais calme, et surtout, n’aie pas peur d’essayer plusieurs fois.",
    "Je sais que ce n’est pas toujours facile, mais tu n’es pas seul. Moi aussi, la première fois, j’ai pris un électron libre en pleine antenne... 😅 On va y arriver ensemble !"
]



class AlienDialogueScene(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLUEBERRY)

        self.alien_sprite = None
        self.current_paragraph_index = 0

    def setup(self):
        # Charger le sprite de l'alien

        self.alien_sprite = arcade.Sprite("../assets/alien.png", ALIEN_SCALE)
        self.alien_sprite.center_x = 100
        self.alien_sprite.center_y = SCREEN_HEIGHT // 2

    def on_draw(self):
        arcade.start_render()

        # Dessiner l'alien
        self.alien_sprite.draw()

        # Dessiner la boîte de dialogue
        self.draw_dialogue_box()

    def draw_dialogue_box(self):
        # Dessiner un rectangle semi-transparent
        arcade.draw_lrtb_rectangle_filled(
            left=0,
            right=SCREEN_WIDTH,
            top=DIALOGUE_BOX_HEIGHT,
            bottom=0,
            color=(50, 50, 50, 220)  # boîte semi-transparente
        )

        # Dessiner le texte
        paragraph = PARAGRAPHS[self.current_paragraph_index]
        arcade.draw_text(
            paragraph,
            start_x=TEXT_MARGIN,
            start_y=TEXT_MARGIN,
            color=arcade.color.WHITE,
            font_size=14,
            width=SCREEN_WIDTH - 2 * TEXT_MARGIN,
            multiline=True
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.current_paragraph_index += 1
            if self.current_paragraph_index >= len(PARAGRAPHS):
                self.current_paragraph_index = 0  # Revenir au début (ou utilisez `close()` pour quitter)

def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = AlienDialogueScene()
    # When launching directly, call setup once before showing
    view.setup()
    window.show_view(view)
    arcade.run()
# --- Lancer le jeu ---
if __name__ == "__main__":
    main()
