import arcade, random, math
from .base import BaseView
from pathlib import Path
from arcade.gui import (
    UIAnchorLayout,
    UIFlatButton,
    UIGridLayout,
    UIManager
)
from .popup_view import PopupView

class AlienView(BaseView):
    def __init__(self):
        super().__init__()

        self.ui = UIManager()
        self.ui.enable()
        # Les boutons pour la suite
        self.nextButtonPressed = False
        self.max_lives = 5
        self.lives = self.max_lives

        self.level = 1           # Niveau actuel
        self.speed_base = 3.0

        # Image de la cible (indice visuel affiché en haut)
        cibles = ["rouge", "bleue", "violet"]
        self.target_hint = arcade.Sprite(f"assets/tete_alien_{cibles[self.level-1]}_cible.png", scale=0.2)
        
        # Booleen pour la popup
        self.show_popup = False


        # --- Décor ---
        self.background = arcade.Sprite("assets/image.png")
        self.background.center_x = 0
        self.background.center_y = 0

        self.lune = arcade.Sprite("assets/lune.png", scale=0.075)
        self.lune.center_x = 100
        self.lune.center_y = 90


        self.alien = arcade.Sprite("assets/alien.png", scale=0.6)
        self.alien.center_x = 110
        self.alien.center_y = 310

        self.telescope = arcade.Sprite("assets/telescope.png", scale=0.9)
        self.telescope.center_x = 380
        self.telescope.center_y = 350
        self.telescope.angle = -15
        

        self.img_list = arcade.SpriteList()
        self.img_list.extend([self.background, self.alien, self.lune, self.telescope, self.target_hint])

        # --- Cercle ---
        self.circle_x = self.window.width / 2 + 290
        self.circle_y = self.window.height - 250
        self.circle_r = 250

        # --- Aliens flottants ---
        self.aliens = arcade.SpriteList()
        self.alien_speeds = {}
        self.target_change_timer = 0  # compteur pour changer de direction

        speed = 3.0  # <-- vitesse fixe pour tous
        

        # La tête spéciale à trouver
        self.target = arcade.Sprite(f"assets/tete_alien_{cibles[self.level - 1]}_cible.png", scale=0.1)
        self.target.center_x = self.circle_x
        self.target.center_y = self.circle_y

        dir_angle = random.uniform(0, 2 * math.pi)
        dx = math.cos(dir_angle) * speed
        dy = math.sin(dir_angle) * speed
        self.alien_speeds[self.target] = [dx, dy]
        
        self.aliens.append(self.target)

        colors = ["bleue", "rouge", "orange"]
        for color in colors:
            for i in range(25):  # 3 têtes par couleur
                sprite = arcade.Sprite(f"assets/tete_alien_{color}.png", scale=0.1)

                # Position aléatoire dans le cercle
                angle = random.uniform(0, 2 * math.pi)
                radius = random.uniform(20, self.circle_r - 30)
                sprite.center_x = self.circle_x + math.cos(angle) * radius
                sprite.center_y = self.circle_y + math.sin(angle) * radius

                # Direction aléatoire mais vitesse fixe
                dir_angle = random.uniform(0, 2 * math.pi)
                dx = math.cos(dir_angle) * speed
                dy = math.sin(dir_angle) * speed
                self.alien_speeds[sprite] = [dx, dy]

                self.aliens.append(sprite)
        self.spawn_aliens()

    def on_show_view(self):
        super().on_show_view()

    def on_draw(self):
        super().on_draw()
        self.img_list.draw()
        self.show_text_center("Trouvez l'alien !",size=25, height=self.window.height- 200, width=self.window.width/4)
        # Après ton texte "Trouvez l'alien !"
        self.show_text_center(f"Vies : {self.lives}", size=20, height=self.window.height - 230, width=self.window.width / 4)

        # Positionner l'indice sous le texte
        self.target_hint.center_x = self.window.width / 4
        self.target_hint.center_y = self.window.height - 120

        # Cercle
        arcade.draw_circle_filled(
            self.circle_x,
            self.circle_y,
            self.circle_r,
            (255, 255, 255),
        )
        arcade.draw_circle_outline(
            self.circle_x,
            self.circle_y,
            self.circle_r,
            arcade.color.WHITE_SMOKE,
            2.0,
        )

        # Aliens
        self.aliens.draw()

    def on_update(self, delta_time: float):
        """Mettre à jour la position des têtes flottantes"""
        for alien in self.aliens:
            dx, dy = self.alien_speeds[alien]

            # --- Mouvement spécial pour la cible ---
            if alien == self.target:
                # Variation légère pour rendre le mouvement plus vivant
                dx += random.uniform(-0.2, 0.2)
                dy += random.uniform(-0.2, 0.2)

                # Normaliser pour garder la vitesse du niveau
                length = math.sqrt(dx**2 + dy**2)
                if length > 0:
                    dx = (dx / length) * (self.speed_base + (self.level - 1) * 1.5)
                    dy = (dy / length) * (self.speed_base + (self.level - 1) * 1.5)

            alien.center_x += dx
            alien.center_y += dy

            # Vérifier si l'alien sort du cercle
            dist = math.dist((alien.center_x, alien.center_y), (self.circle_x, self.circle_y))
            if dist + alien.width / 2 > self.circle_r:
                # Rebondir en inversant la vitesse
                vec_x = alien.center_x - self.circle_x
                vec_y = alien.center_y - self.circle_y
                length = math.sqrt(vec_x**2 + vec_y**2)
                nx, ny = vec_x / length, vec_y / length  # Normal du cercle

                # Projection de la vitesse sur la normale
                dot = dx * nx + dy * ny
                dx -= 2 * dot * nx
                dy -= 2 * dot * ny

                # Appliquer nouvelle vitesse
                self.alien_speeds[alien] = [dx, dy]

                # Remettre l'alien à l'intérieur du cercle
                alien.center_x = self.circle_x + nx * (self.circle_r - alien.width / 2)
                alien.center_y = self.circle_y + ny * (self.circle_r - alien.height / 2)
            else:
                # Sauvegarder la vitesse (pour la cible modifiée aussi)
                self.alien_speeds[alien] = [dx, dy]



    def show_text_center(self, text, color=arcade.color.WHITE, size=20, height = 50, width = 100):
        arcade.draw_text(
            text,
            width,
            height,
            color,
            font_size=size,
            anchor_x="center",
            anchor_y="center",
        )

    def on_mouse_press(self, x, y, button, modifiers):
        aliens_clicked = arcade.get_sprites_at_point((x, y), self.aliens)
        if self.target in aliens_clicked:
            if self.level < 3:
                self.level += 1
                self.spawn_aliens()
            else:
                # Tous les niveaux terminés -> popup ou fin de jeu
                self.show_popup = True
                popup = PopupView(self)
                self.window.show_view(popup, win=True)
        else:
            # Clic raté → retirer une vie
            self.lives -= 1
            print(f"❌ Mauvais clic ! Vies restantes : {self.lives}")
            if self.lives <= 0:
                print("💀 Game Over !")
                # Afficher popup de fin de jeu
                self.show_popup = True
                popup = PopupView(self, win=False)
                self.window.show_view(popup)


        
    def create_popup_buttons(self):
        grid = UIGridLayout(column_count=1, row_count=2, vertical_spacing=10)

        next_btn = UIFlatButton(text="Jeu suivant", width=200)
        next_btn.on_click = self.on_next_click
        grid.add(next_btn, row=0, column=0)

        quit_btn = UIFlatButton(text="Quitter", width=200)
        quit_btn.on_click = self.on_quit_click
        grid.add(quit_btn, row=1, column=0)

        self.ui.add(UIAnchorLayout(children=[grid]))

    def on_key_press(self, symbol, modifiers):
        if self.show_popup and symbol == arcade.key.ESCAPE:
            arcade.close_window()
    
    def on_next_click(self, event):
        print("👉 Bouton 'Jeu suivant' cliqué")
        from .galaxy import GalaxyView
        self.window.show_view(GalaxyView)
        

    def on_quit_click(self, event):
        print("👉 Bouton 'Quitter' cliqué")
        arcade.exit()

    def spawn_aliens(self):
        """Crée les aliens avec vitesse adaptée au niveau et met à jour la cible"""
        self.aliens = arcade.SpriteList()
        self.alien_speeds = {}

        # Vitesse qui augmente avec le niveau
        speed = self.speed_base + (self.level - 1) * 1.5

        cibles = ["rouge", "bleue", "violet"]
        tete_cible = cibles[self.level-1]

        # Création de la cible
        self.target = arcade.Sprite(f"assets/tete_alien_{tete_cible}_cible.png", scale=0.1)
        self.target.center_x = self.circle_x
        self.target.center_y = self.circle_y

        # Mise à jour de l'indice visuel
        self.target_hint.texture = arcade.load_texture(f"assets/tete_alien_{tete_cible}_cible.png")

        # Vitesse initiale de la cible
        dir_angle = random.uniform(0, 2 * math.pi)
        dx = math.cos(dir_angle) * speed
        dy = math.sin(dir_angle) * speed
        self.alien_speeds[self.target] = [dx, dy]

        self.aliens.append(self.target)

        # Création des autres aliens avec la même vitesse
        colors = ["bleue", "rouge", "violet"]
        for color in colors:
            for i in range(25):
                sprite = arcade.Sprite(f"assets/tete_alien_{color}.png", scale=0.1)
                angle = random.uniform(0, 2 * math.pi)
                radius = random.uniform(20, self.circle_r - 30)
                sprite.center_x = self.circle_x + math.cos(angle) * radius
                sprite.center_y = self.circle_y + math.sin(angle) * radius

                dir_angle = random.uniform(0, 2 * math.pi)
                dx = math.cos(dir_angle) * speed
                dy = math.sin(dir_angle) * speed
                self.alien_speeds[sprite] = [dx, dy]

                self.aliens.append(sprite)

    


