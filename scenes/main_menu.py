import arcade
import pyglet
from pathlib import Path
from .base import BaseView


class MainMenuView(BaseView):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.BLACK

        # GIF background (pyglet sprite)
        self._bg_sprite: pyglet.sprite.Sprite | None = None

        # Menu
        self._options = ["Start", "Credit", "Quit"]  # ordre demandé
        self._selected_index = 0

    # ---------- Lifecycle ----------
    def on_show_view(self):
        super().on_show_view()
        self._load_gif()
        self._fit_bg_to_window()

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self._fit_bg_to_window()

    def on_update(self, delta_time: float):
        # Avance l’animation GIF
        try:
            pyglet.clock.tick()
        except Exception:
            pass
        return super().on_update(delta_time)

    # ---------- Input ----------
    def on_key_press(self, key, modifiers):
        if key == arcade.key.DOWN:
            self._selected_index = (self._selected_index + 1) % len(self._options)  # descend visuellement
        elif key == arcade.key.UP:
            self._selected_index = (self._selected_index - 1) % len(self._options)  # monte visuellement
        elif key in (arcade.key.ENTER, arcade.key.RETURN):
            self._activate_option()

    # ---------- Draw ----------
    def on_draw(self):
        super().on_draw()

        # Fond GIF plein écran (cover)
        if self._bg_sprite:
            ctx_mgr = getattr(getattr(self.window, "ctx", None), "pyglet_rendering", None)
            if callable(ctx_mgr):
                with ctx_mgr():
                    self._bg_sprite.draw()
            else:
                self._bg_sprite.draw()

        # Titre centré
        arcade.draw_text(
            "OUT OF SCALE",
            self.window.width // 2,
            self.window.height // 1.5,
            arcade.color.WHITE,
            font_size=72,
            anchor_x="center",
            anchor_y="center",
        )

        # Menu en bas-droite, gros
        right_margin = 70
        bottom_margin = 40
        font_size = 48
        line_h = 58

        # On empile vers le haut depuis le bas
        stack_top_y = bottom_margin + line_h * len(self._options)
        for i, option in enumerate(self._options):
            y = stack_top_y - i * line_h
            color = arcade.color.YELLOW if i == self._selected_index else arcade.color.WHITE
            arcade.draw_text(
                option,
                self.window.width - right_margin,
                y,
                color,
                font_size=font_size,
                anchor_x="right",
                anchor_y="bottom",
            )

    # ---------- Helpers ----------
    def _load_gif(self):
        gif_path = Path(__file__).resolve().parent.parent / "assets" / "main_menu" / "main_menu_background.gif"
        print(f"Trying to load GIF from: {gif_path}")
        if not gif_path.exists():
            print("Could not load GIF: file not found")
            self._bg_sprite = None
            return
        try:
            animation = pyglet.image.load_animation(str(gif_path))
            sprite = pyglet.sprite.Sprite(animation)
            sprite.batch = None  # draw immédiat
            # Ancrage bas-gauche pour un positionnement simple
            try:
                sprite.anchor_x = 0
                sprite.anchor_y = 0
            except Exception:
                # certaines versions posent l’ancrage sur l’image
                if hasattr(sprite, "image"):
                    try:
                        sprite.image.anchor_x = 0
                        sprite.image.anchor_y = 0
                    except Exception:
                        pass
            self._bg_sprite = sprite
            print("GIF loaded successfully!")
        except Exception as e:
            print(f"Could not load GIF: {e}")
            self._bg_sprite = None
    def _anim_size(self, img):
        """Retourne (w, h) de l'animation ou image pyglet."""
        # GIF/Animation
        if hasattr(img, "get_max_width"):
            return int(img.get_max_width()), int(img.get_max_height())
        # Fallback: première frame
        if hasattr(img, "frames") and img.frames:
            f = img.frames[0].image
            return int(getattr(f, "width", 0)), int(getattr(f, "height", 0))
        # Image simple
        return int(getattr(img, "width", 0)), int(getattr(img, "height", 0))

    def _fit_bg_to_window(self):
        if not self._bg_sprite or not self.window:
            return

        win_w, win_h = int(self.window.width), int(self.window.height)
        img_w, img_h = self._anim_size(self._bg_sprite.image)
        if not img_w or not img_h:
            return

        # Étirement pour remplir TOUTE la fenêtre (pas de bandes noires)
        self._bg_sprite.scale_x = win_w / img_w
        self._bg_sprite.scale_y = win_h / img_h

        # Bas-gauche = (0,0) pour couvrir entièrement
        self._bg_sprite.x = 0
        self._bg_sprite.y = 0

    def _activate_option(self):
        option = self._options[self._selected_index]
        if option == "Start":
            from .menu import MenuView
            self.window.show_view(MenuView())
        elif option == "Credit":
            from .credits import CreditsView
            self.window.show_view(CreditsView())
        elif option == "Quit":
            arcade.exit()