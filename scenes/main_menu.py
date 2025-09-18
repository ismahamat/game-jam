# scenes/main_menu.py

from pathlib import Path
from typing import Optional, List, Tuple
import math
import arcade

# Pillow est optionnel. Si non installé, le code utilisera frames PNG ou un fallback visuel.
try:
    from PIL import Image, ImageSequence
    _PIL_OK = True
except Exception:
    _PIL_OK = False

from .base import BaseView
from core import play_ui_sound


class MainMenuView(BaseView):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.BLACK

        # Animation background (textures + durées)
        self._bg_textures: List[arcade.Texture] = []
        self._bg_durations: List[float] = []  # secondes
        self._bg_index: int = 0
        self._bg_time_accum: float = 0.0

        # Rendu via SpriteList (API stable dans Arcade)
        self._bg_list: Optional[arcade.SpriteList] = None
        self._bg_sprite: Optional[arcade.Sprite] = None

        # Fallback si aucun asset dispo
        self._use_fallback: bool = False
        self._fallback_t: float = 0.0

        # Menu
        self._options = ["Start", "Credit", "Quit"]  # ordre demandé
        self._selected_index = 0

    # ---------- Lifecycle ----------
    def on_show_view(self):
        super().on_show_view()
        self._load_background()
        self._ensure_spritelist_and_sprite()
        self._fit_sprite_to_window()

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self._fit_sprite_to_window()

    def on_update(self, delta_time: float):
        # Anime les textures si on en a plusieurs
        if not self._use_fallback and self._bg_textures and len(self._bg_textures) > 1 and self._bg_sprite:
            self._bg_time_accum += delta_time
            cur_dur = self._bg_durations[self._bg_index] if self._bg_durations else 0.08
            if cur_dur <= 0:
                cur_dur = 0.08
            while self._bg_time_accum >= cur_dur:
                self._bg_time_accum -= cur_dur
                self._bg_index = (self._bg_index + 1) % len(self._bg_textures)
                self._bg_sprite.texture = self._bg_textures[self._bg_index]
                self._fit_sprite_to_window()

        # Fallback animé discret si aucun asset
        if self._use_fallback:
            self._fallback_t = (self._fallback_t + delta_time) % 10.0

        return super().on_update(delta_time)

    # ---------- Input ----------
    def on_key_press(self, key, modifiers):
        if key == arcade.key.DOWN:
            play_ui_sound('select')
            self._selected_index = (self._selected_index + 1) % len(self._options)
        elif key == arcade.key.UP:
            play_ui_sound('select')
            self._selected_index = (self._selected_index - 1) % len(self._options)
        elif key in (arcade.key.ENTER, arcade.key.RETURN):
            play_ui_sound('confirm')
            self._activate_option()

    # ---------- Draw ----------
    def on_draw(self):
        super().on_draw()
        win_w, win_h = self.window.width, self.window.height

        # Fond image si dispo, sinon fallback visuel
        if self._bg_list and not self._use_fallback:
            self._bg_list.draw()  # on dessine la liste, API stable
        else:
            # Fallback: évite l'écran noir si aucun asset n'est présent
            arcade.draw_lrtb_rectangle_filled(0, win_w, win_h, 0, (8, 10, 14))
            # halos animés très légers
            s1 = abs(math.sin(self._fallback_t))
            s2 = abs(math.sin(self._fallback_t * 0.7))
            r = int(40 + 30 * s1)
            g = int(70 + 40 * s2)
            b = 120
            arcade.draw_circle_filled(win_w * 0.65, win_h * 0.55, win_h * 0.6, (r, g, b, 30))
            arcade.draw_circle_filled(win_w * 0.35, win_h * 0.35, win_h * 0.5, (b, g, r, 25))

        # Titre centré
        arcade.draw_text(
            "OUT OF SCALE",
            win_w // 2,
            win_h // 1.5,
            arcade.color.WHITE,
            font_size=72,
            anchor_x="center",
            anchor_y="center",
        )

        # Menu en bas droite
        right_margin = 70
        bottom_margin = 40
        font_size = 48
        line_h = 58
        stack_top_y = bottom_margin + line_h * len(self._options)
        for i, option in enumerate(self._options):
            y = stack_top_y - i * line_h
            color = arcade.color.YELLOW if i == self._selected_index else arcade.color.WHITE
            arcade.draw_text(
                option,
                win_w - right_margin,
                y,
                color,
                font_size=font_size,
                anchor_x="right",
                anchor_y="bottom",
            )

    # ---------- Helpers ----------
    def _load_background(self):
        """
        Ordre de chargement:
        1) frames PNG: assets/main_menu/frames/*.png
        2) PNG statique: assets/main_menu/main_menu_background.png
        3) GIF via Pillow: assets/main_menu/main_menu_background.gif
        4) Fallback visuel (jamais noir)
        """
        assets_dir = Path(__file__).resolve().parent.parent / "assets" / "main_menu"
        frames_dir = assets_dir / "frames"
        static_path = assets_dir / "main_menu_background.png"
        gif_path = assets_dir / "main_menu_background.gif"

        self._bg_textures.clear()
        self._bg_durations.clear()
        self._bg_index = 0
        self._bg_time_accum = 0.0
        self._use_fallback = False

        # 1) Frames PNG
        files = sorted(frames_dir.glob("*.png")) if frames_dir.exists() else []
        if files:
            try:
                self._bg_textures = [arcade.load_texture(str(p)) for p in files]
                self._bg_durations = [0.08] * len(self._bg_textures)
                print(f"[MainMenu] Loaded {len(self._bg_textures)} PNG frames")
                return
            except Exception as e:
                print(f"[MainMenu] PNG frames load failed: {e}")
                self._bg_textures.clear()

        # 2) PNG statique
        if static_path.exists():
            try:
                tex = arcade.load_texture(str(static_path))
                self._bg_textures = [tex]
                self._bg_durations = [9999.0]
                print("[MainMenu] Loaded static PNG background")
                return
            except Exception as e:
                print(f"[MainMenu] Static PNG load failed: {e}")

        # 3) GIF via Pillow (optionnel)
        if _PIL_OK and gif_path.exists():
            try:
                textures, durations = self._decode_gif_to_textures(gif_path)
                if textures:
                    self._bg_textures = textures
                    self._bg_durations = durations
                    print(f"[MainMenu] Decoded GIF -> {len(textures)} frames")
                    return
            except Exception as e:
                print(f"[MainMenu] GIF decode failed: {e}")

        # 4) Fallback visuel
        print("[MainMenu] No background asset found. Using animated fallback.")
        self._use_fallback = True

    def _ensure_spritelist_and_sprite(self):
        """Crée SpriteList et Sprite si besoin et assigne la texture initiale."""
        if self._use_fallback or not self._bg_textures:
            self._bg_list = None
            self._bg_sprite = None
            return

        if self._bg_list is None:
            self._bg_list = arcade.SpriteList(use_spatial_hash=False)

        if self._bg_sprite is None:
            self._bg_sprite = arcade.Sprite()
            self._bg_list.append(self._bg_sprite)

        self._bg_sprite.texture = self._bg_textures[self._bg_index]
        self._bg_sprite.center_x = self.window.width / 2
        self._bg_sprite.center_y = self.window.height / 2

    def _fit_sprite_to_window(self):
        """Ajuste l’échelle du sprite pour couvrir la fenêtre sans déformer."""
        if self._use_fallback or not self._bg_sprite or not self._bg_sprite.texture or not self.window:
            return

        tex_w = getattr(self._bg_sprite.texture, "width", 1) or 1
        tex_h = getattr(self._bg_sprite.texture, "height", 1) or 1
        win_w = float(self.window.width)
        win_h = float(self.window.height)

        scale = max(win_w / tex_w, win_h / tex_h)
        self._bg_sprite.scale = scale
        self._bg_sprite.center_x = win_w / 2
        self._bg_sprite.center_y = win_h / 2

    def _decode_gif_to_textures(self, gif_path: Path) -> Tuple[List[arcade.Texture], List[float]]:
        """Decode un GIF en textures Arcade en conservant les durées de frames (ms -> s)."""
        textures: List[arcade.Texture] = []
        durations: List[float] = []

        im = Image.open(str(gif_path))
        for i, frame in enumerate(ImageSequence.Iterator(im)):
            fr = frame.convert("RGBA")
            tex = arcade.Texture(name=f"bg_{i}", image=fr)
            textures.append(tex)
            d_ms = frame.info.get("duration", 80)
            durations.append(max(0.01, d_ms / 1000.0))

        if not textures:
            fr = im.convert("RGBA")
            textures.append(arcade.Texture(name="bg_0", image=fr))
            durations.append(0.08)

        return textures, durations

    def _activate_option(self):
        option = self._options[self._selected_index]
        if option == "Start":
            from .AtomDialogueScene import AtomDialogueScene
            self.window.show_view(AtomDialogueScene())
        elif option == "Credit":
            from .credits import CreditsView
            self.window.show_view(CreditsView())
        elif option == "Quit":
            arcade.exit()