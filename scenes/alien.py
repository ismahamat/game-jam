import arcade, random, math
from .base import BaseView
from pathlib import Path


class AlienView(BaseView):
    def __init__(self):
        super().__init__()

        # Image de la cible (indice visuel affiché en haut)
        self.target_hint = arcade.Sprite("assets/tete_alien_cible.png", scale=0.2)
        
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
        self.target = arcade.Sprite("assets/tete_alien_cible.png", scale=0.1)
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

    def on_show_view(self):
        super().on_show_view()

    def on_draw(self):
        super().on_draw()
        self.img_list.draw()
        self.show_text_center("Trouvez l'alien !",size=25, height=self.window.height- 200, width=self.window.width/4)

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


        if self.show_popup:
            # zone rectangulaire centrée
            w, h = 1080, 700
            center_x = self.window.width / 2
            center_y = self.window.height / 2

            rect = arcade.Rect(
                width=w,
                height=h,
                x = center_x,
                y=center_y,
                left=center_x - w / 2,
                right=center_x + w / 2,
                bottom=center_y - h / 2,
                top=center_y + h / 2
            )

            arcade.draw_rect_filled(rect, (0, 0, 0,255)) 

            # texte au milieu
            arcade.draw_text(
                "🎉 Gagné ! 🎉",
                self.window.width / 2,
                self.window.height / 2 + 40,
                arcade.color.WHITE,
                font_size=30,
                anchor_x="center",
                anchor_y="center",
            )
            arcade.draw_text(
                "Appuie sur ESC pour quitter",
                self.window.width / 2,
                self.window.height / 2 - 30,
                arcade.color.LIGHT_GRAY,
                font_size=16,
                anchor_x="center",
                anchor_y="center",
            )


    def on_update(self, delta_time: float):
        """Mettre à jour la position des têtes flottantes"""
        for alien in self.aliens:
            dx, dy = self.alien_speeds[alien]

            # --- Mouvement spécial pour la cible ---
            if alien == self.target:
                # Ajouter une petite variation aléatoire à chaque update
                dx += random.uniform(-0.2, 0.2)
                dy += random.uniform(-0.2, 0.2)

                # Normaliser pour garder la même vitesse globale
                length = math.sqrt(dx**2 + dy**2)
                if length > 0:
                    dx = (dx / length) * 3.0   # 3.0 = la vitesse définie pour tous
                    dy = (dy / length) * 3.0

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



    def show_text_center(self, text, color=arcade.color.WHITE, size=20, height = 50, width = 50):
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
        """Plus tard tu pourras tester si on clique sur la bonne tête"""
        aliens_clicked = arcade.get_sprites_at_point((x, y), self.aliens)
        for alien in aliens_clicked:
            if alien == self.target:
                print("🎉 Gagné ! Tu as trouvé le bon alien !")
                self.show_popup = True
        
    def on_key_press(self, symbol, modifiers):
        if self.show_popup and symbol == arcade.key.ESCAPE:
            arcade.close_window()
        

