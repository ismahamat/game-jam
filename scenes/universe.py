import math
from pathlib import Path
import arcade
import pyglet
from .base import BaseView


class UniverseView(BaseView):
    """Deux trous noirs se dirigent l'un vers l'autre.

    Appuyez sur le bouton "Ralentir !" pour temporiser et éviter la collision.
    """

    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.BLACK

        # Etat des trous noirs
        self.left_pos: tuple[float, float] = (0.0, 0.0)
        self.right_pos: tuple[float, float] = (0.0, 0.0)
        self.left_vel: tuple[float, float] = (0.0, 0.0)
        self.right_vel: tuple[float, float] = (0.0, 0.0)
        self.collision_dist: float = 180.0
        
        # Sprites
        self.asset_dir: Path = Path(__file__).resolve().parent.parent / "assets" / "universe"
        self.left_bh: arcade.Sprite | None = None
        self.right_bh: arcade.Sprite | None = None
        self.wind: arcade.Sprite | None = None
        self._wind_angle: float = 0.0
        self._objects = arcade.SpriteList()
        self._fx = arcade.SpriteList()
        self._bg_image_list = arcade.SpriteList()

        # Bouton "Ralentir !"
        # (center_x, center_y, width, height)
        self._btn_rect: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
        self._btn_fill: arcade.Sprite | None = None
        self._btn_border: arcade.Sprite | None = None
        self._help_fill: arcade.Sprite | None = None
        self._help_border: arcade.Sprite | None = None
        self._help_rect: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
        self._ui = arcade.SpriteList()
        self._slow_timer: float = 0.0
        self._game_over: bool = False
        self._slow_uses: int = 0
        self._space_held: bool = False
        self._slow_impulse: float = 0.12
        self._explosion_sprite: pyglet.sprite.Sprite | None = None
        self._explosion_timer: float = 0.0
        self._explosion_duration: float = 0.0
        self._exploding: bool = False
        self._show_game_over: bool = False
        self._post_explosion_delay: float = 0.8
        self._post_explosion_timer: float = 0.0
        self._explosion_fade_time: float = 0.6
        self._core_factor: float = 0.10

    # ----- Lifecycle -----
    def on_show_view(self):
        super().on_show_view()
        # Positionnement initial dépendant de la fenêtre
        w = self.window.width if self.window else 1080
        h = self.window.height if self.window else 720

        # Plus éloignés au départ
        self.left_pos = (w * 0.22, h * 0.58)
        self.right_pos = (w * 0.78, h * 0.42)

        # Vitesse plus faible
        speed = 110.0
        # Vitesse vers le centre
        self.left_vel = (speed, -speed * 0.15)
        self.right_vel = (-speed, speed * 0.15)

        # Charger les sprites
        # Fond d'écran si disponible
        self._bg_image_list = arcade.SpriteList()
        bg_path = self.asset_dir / "SpaceBackground.png"
        if bg_path.exists():
            bg = self._load_scaled(bg_path, target_w=w)
            # Ajuster pour couvrir la hauteur
            try:
                tex = bg.texture
                if tex and tex.height:
                    current_h = tex.height * bg.scale
                    if current_h < h:
                        bg.scale *= h / current_h
            except Exception:
                pass
            bg.center_x = w / 2
            bg.center_y = h / 2
            self._bg_image_list.append(bg)
        target_w = int(min(320, w * 0.26))
        self.left_bh = self._load_scaled(self.asset_dir / "blackhole.png", target_w) if (self.asset_dir / "blackhole.png").exists() else None
        self.right_bh = self._load_scaled(self.asset_dir / "blackhole2.png", target_w) if (self.asset_dir / "blackhole2.png").exists() else None
        wind_w = int(min(420, w * 0.34))
        self.wind = self._load_scaled(self.asset_dir / "wind.png", wind_w) if (self.asset_dir / "wind.png").exists() else None
        
        # Placer les sprites
        if self.left_bh:
            self.left_bh.center_x, self.left_bh.center_y = self.left_pos
            self._objects.append(self.left_bh)
        if self.right_bh:
            self.right_bh.center_x, self.right_bh.center_y = self.right_pos
            self._objects.append(self.right_bh)
        if self.wind:
            self.wind.center_x = w / 2
            self.wind.center_y = h * 0.1
            try:
                self.wind.alpha = 160
            except Exception:
                pass
            self._fx.append(self.wind)

        # Distance de collision quand les noyaux se superposent presque
        left_w = self.left_bh.width if self.left_bh else 180.0
        right_w = self.right_bh.width if self.right_bh else 180.0
        self.collision_dist = (left_w * self._core_factor) + (right_w * self._core_factor)

        # Bouton centré en haut (sprites pour compat maximal)
        btn_w, btn_h = 380, 80
        self._btn_rect = (w / 2, h - 60, float(btn_w), float(btn_h))
        self._ui = arcade.SpriteList()
        self._btn_border = arcade.SpriteSolidColor(int(btn_w + 6), int(btn_h + 6), arcade.color.WHITE)
        self._btn_border.center_x, self._btn_border.center_y = self._btn_rect[0], self._btn_rect[1]
        self._btn_fill = arcade.SpriteSolidColor(int(btn_w), int(btn_h), arcade.color.DARK_RED)
        self._btn_fill.center_x, self._btn_fill.center_y = self._btn_rect[0], self._btn_rect[1]
        self._ui.append(self._btn_border)
        self._ui.append(self._btn_fill)

        # Aide en haut-droite: rectangle + bordure
        margin = 18
        help_w, help_h = 300, 46
        help_x = w - help_w / 2 - margin
        help_y = h - help_h / 2 - margin
        self._help_rect = (help_x, help_y, float(help_w), float(help_h))
        self._help_border = arcade.SpriteSolidColor(int(help_w + 4), int(help_h + 4), arcade.color.WHITE)
        self._help_border.center_x, self._help_border.center_y = help_x, help_y
        self._help_fill = arcade.SpriteSolidColor(int(help_w), int(help_h), (10, 10, 18))
        self._help_fill.center_x, self._help_fill.center_y = help_x, help_y
        self._ui.append(self._help_border)
        self._ui.append(self._help_fill)

        self._slow_timer = 0.0
        self._game_over = False
        self._slow_uses = 0
        self._space_held = False
        self._explosion_sprite = None
        self._explosion_timer = 0.0
        self._explosion_duration = 0.0
        self._exploding = False
        self._show_game_over = False
        self._post_explosion_timer = 0.0
        self._explosion_fade_time = 0.6

    # ----- Drawing -----
    def on_draw(self):
        super().on_draw()

        # Fond étoilé simple (noir + quelques points)
        if self.window:
            w, h = self.window.width, self.window.height
        else:
            w, h = 1080, 720

        # Background image if present
        if len(self._bg_image_list) > 0:
            self._bg_image_list.draw()

        # Explosion par-dessus le fond
        if self._exploding and self._explosion_sprite is not None:
            self._explosion_sprite.draw()
        elif not self._game_over:
            # Dessin des trous noirs (sprites si dispo), sinon fallback uniquement en jeu
            if len(self._objects) > 0:
                self._objects.draw()
            else:
                self._draw_black_hole(self.left_pos[0], self.left_pos[1], 90)
                self._draw_black_hole(self.right_pos[0], self.right_pos[1], 90)

        # Effet "wind" en bas (statique) - seulement pendant le jeu
        if not self._exploding and not self._game_over and self.wind and len(self._fx) > 0:
            self._fx.draw()

        # UI (sprites pour les cadres), puis textes - seulement pendant le jeu
        if not self._exploding and not self._game_over:
            if len(self._ui) > 0:
                self._ui.draw()
            self._draw_button()
            hint = f"ESPACE pour ralentir  (x{self._slow_uses})"
            hx, hy, _, _ = self._help_rect
            arcade.draw_text(hint, hx, hy - 9, arcade.color.WHITE, 18, anchor_x="center")

        if self._show_game_over:
            self.show_text_center("Collision ! Appuie sur ESC pour revenir", size=42)

        # Rien ici: l'explosion est déjà dessinée plus haut

    # ----- Update -----
    def on_update(self, delta_time: float):
        # Gérer l'explosion et le texte de fin
        if self._exploding:
            if self._explosion_timer > 0.0:
                # Fade-out dans les dernières secondes de l'animation
                if self._explosion_sprite is not None:
                    if self._explosion_timer <= self._explosion_fade_time:
                        ratio = max(0.0, min(1.0, self._explosion_timer / self._explosion_fade_time))
                        try:
                            self._explosion_sprite.opacity = int(255 * ratio)
                        except Exception:
                            pass
                    else:
                        try:
                            self._explosion_sprite.opacity = 255
                        except Exception:
                            pass
                self._explosion_timer = max(0.0, self._explosion_timer - delta_time)
            else:
                self._exploding = False
                self._game_over = True
                self._post_explosion_timer = self._post_explosion_delay
            # Pendant l'explosion, on ne met pas à jour les trous noirs
            return
        if self._game_over and not self._show_game_over:
            self._post_explosion_timer = max(0.0, self._post_explosion_timer - delta_time)
            if self._post_explosion_timer <= 0.0:
                self._show_game_over = True
            return
        if self._game_over:
            return
        if not self.window:
            return

        slow_factor = 0.25 if self._slow_timer > 0.0 else 1.0
        self._slow_timer = max(0.0, self._slow_timer - delta_time)

        # Mise à jour des positions
        prev_left = self.left_pos
        prev_right = self.right_pos
        lx = self.left_pos[0] + self.left_vel[0] * slow_factor * delta_time
        ly = self.left_pos[1] + self.left_vel[1] * slow_factor * delta_time
        rx = self.right_pos[0] + self.right_vel[0] * slow_factor * delta_time
        ry = self.right_pos[1] + self.right_vel[1] * slow_factor * delta_time
        self.left_pos = (lx, ly)
        self.right_pos = (rx, ry)
        if self.left_bh:
            self.left_bh.center_x, self.left_bh.center_y = self.left_pos
        if self.right_bh:
            self.right_bh.center_x, self.right_bh.center_y = self.right_pos

        # Détection de collision
        dist = math.hypot(self.right_pos[0] - self.left_pos[0], self.right_pos[1] - self.left_pos[1])
        if dist <= self.collision_dist:
            if self._slow_timer > 0.0:
                # Tant que ralenti actif, figer juste avant l'impact
                self.left_pos = prev_left
                self.right_pos = prev_right
                if self.left_bh:
                    self.left_bh.center_x, self.left_bh.center_y = self.left_pos
                if self.right_bh:
                    self.right_bh.center_x, self.right_bh.center_y = self.right_pos
            else:
                # Démarrer l'explosion immédiatement et masquer les trous noirs
                self._start_explosion()
                # Retirer les trous noirs visuellement
                if self.left_bh:
                    self.left_bh.remove_from_sprite_lists()
                if self.right_bh:
                    self.right_bh.remove_from_sprite_lists()
                self.left_bh = None
                self.right_bh = None
                self._objects = arcade.SpriteList()
                # Retirer aussi le vent
                if self.wind:
                    self.wind.remove_from_sprite_lists()
                    self.wind = None
                self._fx = arcade.SpriteList()
                self._exploding = True

    # ----- Input -----
    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.ESCAPE and self.window:
            from .menu import MenuView
            self.window.show_view(MenuView())
            return
        if key == arcade.key.SPACE:
            # Ralentissement court uniquement à l'appui (pas en maintien)
            if not self._space_held:
                self._space_held = True
                self._slow_timer = self._slow_impulse
                self._slow_uses += 1

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        # Interaction souris désactivée: on utilise la touche ESPACE
        return

    def on_key_release(self, key: int, modifiers: int):
        if key == arcade.key.SPACE:
            self._space_held = False

    # ----- Helpers -----
    def _draw_black_hole(self, x: float, y: float, r: float):
        # Noyau sombre
        arcade.draw_circle_filled(x, y, r * 0.28, (20, 10, 30))
        # Halo violet dégradé simple
        for i in range(8, 0, -1):
            t = i / 8.0
            radius = r * (0.4 + 0.6 * t)
            color = (110 + int(80 * t), 40, 150 + int(60 * t))
            alpha = 28 + int(18 * i)
            arcade.draw_circle_filled(x, y, radius, (*color, alpha))

    def _draw_button(self):
        cx, cy, _, _ = self._btn_rect
        label = f"Ralentir !  (Espace)  x{self._slow_uses}"
        arcade.draw_text(label, cx, cy - 14, arcade.color.WHITE, 28, anchor_x="center")

    @staticmethod
    def _point_in_rect(x: float, y: float, rect: tuple[float, float, float, float]) -> bool:
        cx, cy, w, h = rect
        return (x >= cx - w / 2 and x <= cx + w / 2 and y >= cy - h / 2 and y <= cy + h / 2)

    # ----- Asset helper -----
    def _load_scaled(self, path: Path, target_w: int) -> arcade.Sprite:
        sprite = arcade.Sprite(str(path), scale=1.0)
        tex = sprite.texture
        if tex and tex.width:
            sprite.scale = target_w / float(tex.width)
        return sprite

    # ----- Explosion -----
    def _start_explosion(self):
        if self._explosion_sprite is not None:
            return
        path = self.asset_dir / "explosion.gif"
        if not path.exists():
            return
        try:
            anim = pyglet.image.load_animation(str(path))
            self._explosion_duration = 0.0
            try:
                # Sum frame durations if available
                for f in getattr(anim, "frames", []) or []:
                    self._explosion_duration += getattr(f, "duration", 0.05)
                if self._explosion_duration <= 0:
                    self._explosion_duration = 1.0
            except Exception:
                self._explosion_duration = 1.0
            self._explosion_sprite = pyglet.sprite.Sprite(anim)
            # Position au milieu des deux trous noirs
            cx = (self.left_pos[0] + self.right_pos[0]) / 2
            cy = (self.left_pos[1] + self.right_pos[1]) / 2
            # Convert to bottom-left origin for pyglet sprite
            self._explosion_sprite.update(x=cx - self._explosion_sprite.width / 2,
                                          y=cy - self._explosion_sprite.height / 2)
            self._explosion_timer = self._explosion_duration
        except Exception:
            # Si l'animation ne charge pas, ignorer proprement
            self._explosion_sprite = None
            self._explosion_timer = 0.0
