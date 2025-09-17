import arcade
import random
import math
import time
from pathlib import Path
from .base import BaseView

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Ant Game"

ANT_SPEED = 100
CONTROL_DURATION = 5.0
FOOT_WARNING_DURATION = 2.0
FOOT_INTERVAL_RANGE = (5.0, 10.0)

class AntView(BaseView):
    def __init__(self):
        super().__init__()
        self.ant = None
        self.arrow = None
        self.ant_path = []
        self.ant_index = 0

        self.can_control = False
        self.control_timer = 0

        self.minigame_active = False
        self.minigame_success = False
        self.minigame = None

        self.feet = arcade.SpriteList()
        self.foot_warnings = []
        self.last_foot_time = time.time()

        self.game_over = False
        # Assets
        self.asset_dir: Path = Path(__file__).resolve().parent.parent / "assets" / "ant"
        # Background and actors
        self._bg_list = arcade.SpriteList()
        self.actors = arcade.SpriteList()
        # Colony: queen and followers
        self.queen: arcade.Sprite | None = None
        self.followers: arcade.SpriteList = arcade.SpriteList()
        # Trail for follower pathing
        self._trail: list[tuple[float, float]] = []
        self._trail_stride_px: float = 10.0
        self._follower_spacing_px: float = 20.0
        # Queen horizontal direction (for bouncing inside bounds)
        self._queen_dirx: int = 1
        # Control
        self.controlled_ant: arcade.Sprite | None = None
        self.keys_held: set[int] = set()
        # Mouse control
        self._mouse_x: float = 0.0
        self._mouse_y: float = 0.0
        # Feet spawn
        self._foot_timer: float = 0.0
        self._next_foot_in: float = 2.0
        self._foot_img = self.asset_dir / "foot.png"
        self._foot_target_w: int = 80
        # Arrow asset
        self._arrow_img = self.asset_dir / "arrow.png"
        # Foot events with shadow pre-warning
        self.foot_events: list[dict] = []
        # Queen asset
        self._queen_img = self.asset_dir / "queen.png"
        # Difficulty / progression
        self._elapsed: float = 0.0
        self._next_ant_spawn_in: float = 6.0

    def on_show_view(self):
        # Ensure base behavior (background color, mouse) then initialize sprites
        super().on_show_view()
        self.setup()

    def setup(self):
        if not self.window:
            return
        width = self.window.width
        height = self.window.height

        # Reset lists
        self._bg_list = arcade.SpriteList()
        self.actors = arcade.SpriteList()
        self.followers = arcade.SpriteList()
        self.feet = arcade.SpriteList()
        self._trail = []
        self.foot_warnings = []
        self.game_over = False

        # Background
        bg_img = self.asset_dir / "background_dirt.png"
        if bg_img.exists():
            bg = self._load_scaled(str(bg_img), target_w=width)
            try:
                tex = bg.texture
                if tex and tex.height:
                    bg.scale *= (height / (tex.height * bg.scale))
            except Exception:
                pass
            bg.center_x = width / 2
            bg.center_y = height / 2
            self._bg_list.append(bg)

        # Sizes scaled to screen (larger as requested)
        ant_target_w = max(18, int(height * 0.06))
        self._foot_target_w = max(60, int(height * 0.22))
        self._trail_stride_px = max(6.0, ant_target_w * 0.6)
        self._follower_spacing_px = max(ant_target_w * 0.9, 14.0)

        # Queen ant
        ant_img = self.asset_dir / "ant.png"
        # Load queen with distinct asset if available
        if self._queen_img.exists():
            self.queen = self._load_scaled(str(self._queen_img), target_w=int(ant_target_w * 1.15))
        elif ant_img.exists():
            self.queen = self._load_scaled(str(ant_img), target_w=ant_target_w)
        else:
            self.queen = arcade.SpriteSolidColor(ant_target_w, ant_target_w, arcade.color.BROWN)
        self.queen.center_x = width * 0.15
        self.queen.center_y = height * 0.5
        self._queen_dirx = 1
        self.actors.append(self.queen)

        # Followers (initial batch)
        num_followers = 10
        for _ in range(num_followers):
            if ant_img.exists():
                follower = self._load_scaled(str(ant_img), target_w=ant_target_w)
            else:
                follower = arcade.SpriteSolidColor(ant_target_w, ant_target_w, arcade.color.BROWN)
            follower.center_x = self.queen.center_x - 30
            follower.center_y = self.queen.center_y
            self.followers.append(follower)
            self.actors.append(follower)

        # Controlled ant (one of the followers); never the queen
        self.controlled_ant = self.followers[2] if len(self.followers) >= 3 else (self.followers[0] if len(self.followers) > 0 else None)

        # Arrow above controlled ant (larger)
        if self._arrow_img.exists():
            self.arrow = self._load_scaled(str(self._arrow_img), target_w=max(12, int(ant_target_w * 0.9)))
        else:
            arrow_w = max(12, int(ant_target_w * 0.7))
            arrow_h = max(18, int(ant_target_w * 1.1))
            self.arrow = arcade.SpriteSolidColor(arrow_w, arrow_h, arcade.color.RED)
        target = self.controlled_ant if self.controlled_ant else self.queen
        if target:
            self.arrow.center_x = target.center_x
            self.arrow.center_y = target.center_y + ant_target_w
        self.actors.append(self.arrow)

        # Feet spawn state
        self._foot_timer = 0.0
        self._next_foot_in = 1.8

        # Control + minigame
        self.can_control = False
        self.control_timer = 0
        self.minigame_active = False
        self.minigame = MiniGame()
        self.keys_held.clear()
        # Timebase for animations/difficulty
        self._start_time = time.time()
        self._elapsed = 0.0
        self._next_ant_spawn_in = 6.0

    def _load_scaled(self, path: str, target_w: int) -> arcade.Sprite:
        sprite = arcade.Sprite(path, scale=1.0)
        tex = sprite.texture
        if tex and tex.width:
            sprite.scale = target_w / float(tex.width)
        return sprite

    def _make_shadow_texture(self, width: int, height: int, alpha: int = 140) -> arcade.Texture:
        """Create a soft oval shadow texture (semi-transparent black).

        Returns an arcade.Texture. Falls back to circle if ellipse unavailable.
        """
        try:
            tex = arcade.make_soft_ellipse_texture(width, height, (0, 0, 0, alpha))
            return tex
        except Exception:
            diameter = max(width, height)
            try:
                tex = arcade.make_soft_circle_texture(diameter, (0, 0, 0, alpha))
            except Exception:
                tex = arcade.make_circle_texture(diameter, (0, 0, 0, alpha))
            return tex

    def on_draw(self):
        # Use base clear() to avoid start_render() incompatibility
        super().on_draw()

        # Background
        if self._bg_list:
            self._bg_list.draw()
        # Ants + arrow
        if self.actors:
            self.actors.draw()
        # Feet
        if self.feet:
            self.feet.draw()

        if self.minigame_active:
            self.minigame.draw()

        if self.game_over:
            arcade.draw_text("GAME OVER", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                             arcade.color.RED, 40, anchor_x="center")

    def on_update(self, delta_time):
        if self.game_over:
            return

        # Time accumulation for difficulty scaling & spawning
        self._elapsed += delta_time

        if self.minigame_active:
            self.minigame.update(delta_time)
            return

        # Update queen movement and followers
        self._update_queen(delta_time)
        self._update_trail_and_followers()

        # Control window timer
        if self.can_control:
            self.control_timer -= delta_time
            if self.control_timer <= 0:
                self.can_control = False

        # Mouse-driven movement while control is active (optional)
        if self.controlled_ant and self.can_control:
            self._move_controlled_toward_mouse(delta_time)

        # Continuous keyboard movement during control (with tether to queen)
        if self.controlled_ant and self.window:
            move_x = 0.0
            move_y = 0.0
            if arcade.key.LEFT in self.keys_held or arcade.key.A in self.keys_held:
                move_x -= 1
            if arcade.key.RIGHT in self.keys_held or arcade.key.D in self.keys_held:
                move_x += 1
            if arcade.key.UP in self.keys_held or arcade.key.W in self.keys_held:
                move_y += 1
            if arcade.key.DOWN in self.keys_held or arcade.key.S in self.keys_held:
                move_y -= 1
            length = math.hypot(move_x, move_y)
            if length > 0:
                move_x /= length
                move_y /= length
                speed = max(140.0, self.window.height * 0.35)
                self.controlled_ant.center_x = max(8, min(self.window.width - 8, self.controlled_ant.center_x + move_x * speed * delta_time))
                self.controlled_ant.center_y = max(8, min(self.window.height - 8, self.controlled_ant.center_y + move_y * speed * delta_time))
            # Tether force pulling toward queen to avoid straying too far
            if self.queen:
                dx = self.queen.center_x - self.controlled_ant.center_x
                dy = self.queen.center_y - self.controlled_ant.center_y
                dist = math.hypot(dx, dy)
                max_distance = max(120.0, self.window.height * 0.35)
                if dist > 1:
                    # Weak pull always; stronger when far
                    pull_strength = 0.6 if dist < max_distance else 1.8
                    self.controlled_ant.center_x += dx / dist * pull_strength
                    self.controlled_ant.center_y += dy / dist * pull_strength

        # Update arrow to controlled ant
        if self.arrow and self.controlled_ant:
            self.arrow.center_x = self.controlled_ant.center_x
            # Use sprite.height which already accounts for scale
            try:
                offset = float(getattr(self.controlled_ant, "height", 20))
            except Exception:
                offset = 20.0
            self.arrow.center_y = self.controlled_ant.center_y + offset * 0.6

        # Feet spawn/update with shadow warning
        self._maybe_spawn_feet(delta_time)
        # Move feet and advance shadow/feet state machine
        self.feet.update()
        self._update_feet_and_shadows(delta_time)
        # Progressive follower spawning: gets faster over time
        self._next_ant_spawn_in -= delta_time
        if self._next_ant_spawn_in <= 0 and self.window:
            self._spawn_follower()
            # Next spawn interval shortens with time, min cap
            base = max(1.2, 6.0 - self._elapsed * 0.12)
            jitter = random.uniform(-0.3, 0.5)
            self._next_ant_spawn_in = max(0.7, base + jitter)

        # Remove feet off-screen
        if self.window:
            for foot in list(self.feet):
                if foot.center_y < -100:
                    foot.remove_from_sprite_lists()

        # Collisions: only when foot has landed (visible at target)
        # Only the controlled ant causes game over; followers are removed
        active_shadows = [e["shadow"] for e in getattr(self, "foot_events", []) if e["state"] == "landed"]
        if self.controlled_ant and any(arcade.check_for_collision(self.controlled_ant, s) for s in active_shadows):
            self.game_over = True
        crushed = []
        for ant in self.followers:
            if any(arcade.check_for_collision(ant, s) for s in active_shadows):
                crushed.append(ant)
        for ant in crushed:
            if ant is self.controlled_ant:
                self.game_over = True
            ant.remove_from_sprite_lists()
            if ant in self.followers:
                self.followers.remove(ant)

    def _update_queen(self, dt: float):
        if not self.queen or not self.window:
            return
        speed = max(60.0, self.window.width * 0.12)
        # Horizontal bouncing within screen
        self.queen.center_x += self._queen_dirx * speed * dt
        # Vertical sine movement clamped to bounds
        elapsed = time.time() - getattr(self, "_start_time", 0.0)
        target_y = self.window.height * 0.5 + math.sin(elapsed * 0.8) * (self.window.height * 0.2)
        self.queen.center_y = max(8, min(self.window.height - 8, target_y))
        # Bounce on left/right edges
        if self.queen.center_x < 16:
            self.queen.center_x = 16
            self._queen_dirx = 1
        elif self.queen.center_x > self.window.width - 16:
            self.queen.center_x = self.window.width - 16
            self._queen_dirx = -1

    def _update_trail_and_followers(self):
        if not self.queen:
            return
        # Sample queen position
        last = self._trail[-1] if self._trail else None
        qx, qy = self.queen.center_x, self.queen.center_y
        if not last or math.hypot(qx - last[0], qy - last[1]) >= self._trail_stride_px:
            self._trail.append((qx, qy))
        # Trim trail
        max_len = int((len(self.followers) + 2) * (self._follower_spacing_px / max(1e-3, self._trail_stride_px)) + 200)
        if len(self._trail) > max_len:
            del self._trail[: len(self._trail) - max_len]
        # Move followers
        for i, ant in enumerate(self.followers):
            desired_offset = int((i + 1) * (self._follower_spacing_px / max(1e-3, self._trail_stride_px)))
            idx = max(0, len(self._trail) - 1 - desired_offset)
            target_x, target_y = self._trail[idx]
            if self.can_control and ant is self.controlled_ant:
                # Clamp to screen
                if self.window:
                    ant.center_x = max(8, min(self.window.width - 8, ant.center_x))
                    ant.center_y = max(8, min(self.window.height - 8, ant.center_y))
                continue
            dx = target_x - ant.center_x
            dy = target_y - ant.center_y
            dist = math.hypot(dx, dy)
            if dist > 1:
                step = min(dist, 180)
                ant.center_x += dx / dist * step * (1/60)
                ant.center_y += dy / dist * step * (1/60)
            # Clamp follower to screen
            if self.window:
                ant.center_x = max(8, min(self.window.width - 8, ant.center_x))
                ant.center_y = max(8, min(self.window.height - 8, ant.center_y))

    def on_key_press(self, key, modifiers):
        if self.minigame_active:
            if key == arcade.key.SPACE:
                if self.minigame.attempt_stop():
                    self.can_control = True
                    self.control_timer = CONTROL_DURATION
                    # Pick a random follower to control (never the queen)
                    if len(self.followers) > 0:
                        self.controlled_ant = random.choice(self.followers)
                self.minigame_active = False
            return

        if key == arcade.key.SPACE:
            self.minigame.reset()
            self.minigame_active = True
        # Track held keys for continuous movement while control is active
        self.keys_held.add(key)

    def on_key_release(self, key, modifiers):
        self.keys_held.discard(key)
    def _maybe_spawn_feet(self, dt: float):
        self._foot_timer += dt
        # Use accumulated elapsed (faster acceleration)
        elapsed = self._elapsed
        difficulty = min(5.0, elapsed / 18.0)
        if self._foot_timer >= self._next_foot_in and self.window:
            self._foot_timer = 0.0
            # Spawn faster as difficulty rises; shorter minimums
            base_interval = random.uniform(1.0, 2.2)
            self._next_foot_in = max(0.5, base_interval / (1.0 + 0.55 * difficulty))
            # Create shadow warning then falling foot
            target_y = random.uniform(self.window.height * 0.25, self.window.height * 0.75)
            center_x = random.uniform(60, self.window.width - 60)
            # Oval, semi-transparent shadow (black) via soft ellipse texture
            shadow_w = int(self._foot_target_w * 0.95)
            shadow_h = int(self._foot_target_w * 0.42)
            shadow_tex = self._make_shadow_texture(shadow_w, shadow_h, alpha=150)
            shadow = arcade.Sprite()
            shadow.texture = shadow_tex
            shadow.width = shadow_w
            shadow.height = shadow_h
            shadow.center_x = center_x
            shadow.center_y = target_y
            self.actors.append(shadow)
            if self._foot_img.exists():
                foot = self._load_scaled(str(self._foot_img), target_w=self._foot_target_w)
            else:
                foot = arcade.SpriteSolidColor(self._foot_target_w, int(self._foot_target_w * 1.8), arcade.color.GRAY)
            foot.center_x = center_x
            foot.center_y = self.window.height + float(getattr(foot, "height", 60))
            self.foot_events.append({
                "state": "warning",
                "spawn_time": time.time(),
                # Warning shortens slightly over time
                "warning_duration": max(0.5, random.uniform(1.0, 1.8) / (1.0 + 0.25 * difficulty)),
                "shadow": shadow,
                "foot": foot,
                "target_y": target_y,
                # Fall speed increases with time
                "fall_speed": self.window.height * 0.12 * (1.0 + 0.35 * difficulty),
            })

    def _update_feet_and_shadows(self, dt: float):
        now = time.time()
        for evt in list(self.foot_events):
            state = evt["state"]
            shadow: arcade.Sprite = evt["shadow"]
            foot: arcade.Sprite = evt["foot"]
            target_y: float = evt["target_y"]
            if state == "warning":
                if now - evt["spawn_time"] >= evt["warning_duration"]:
                    evt["state"] = "falling"
                    foot.center_y = self.window.height + float(getattr(foot, "height", 60))
                    foot.change_y = -evt["fall_speed"]
                    if foot not in self.feet:
                        self.feet.append(foot)
            elif state == "falling":
                if foot.center_y <= target_y:
                    foot.center_y = target_y
                    foot.change_y = 0
                    evt["state"] = "landed"
                    evt["land_time"] = now
            elif state == "landed":
                # After a short pause, foot retracts upward and shadow disappears
                if now - evt.get("land_time", now) > 0.6 and "retracting" not in evt:
                    # start retract
                    evt["retracting"] = True
                    if shadow in self.actors:
                        shadow.remove_from_sprite_lists()
                    foot.change_y = +evt["fall_speed"] * 0.9
                elif "retracting" in evt:
                    # Once foot is off-screen, cleanup
                    if foot.center_y > self.window.height + float(getattr(foot, "height", 60)):
                        if foot in self.feet:
                            foot.remove_from_sprite_lists()
                        self.foot_events.remove(evt)

        # Crush logic based on shadow area only when landed
        active_shadows = [e["shadow"] for e in self.foot_events if e["state"] == "landed"]
        if active_shadows:
            if self.controlled_ant and any(arcade.check_for_collision(self.controlled_ant, s) for s in active_shadows):
                self.game_over = True
            crushed2 = []
            for ant in self.followers:
                if any(arcade.check_for_collision(ant, s) for s in active_shadows):
                    crushed2.append(ant)
            for ant in crushed2:
                if ant is self.controlled_ant:
                    self.game_over = True
                ant.remove_from_sprite_lists()
                if ant in self.followers:
                    self.followers.remove(ant)

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self._mouse_x, self._mouse_y = x, y

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int):
        self._mouse_x, self._mouse_y = x, y

    def _move_controlled_toward_mouse(self, dt: float):
        if not self.window or not self.controlled_ant:
            return
        target_x = max(8, min(self.window.width - 8, self._mouse_x))
        target_y = max(8, min(self.window.height - 8, self._mouse_y))
        dx = target_x - self.controlled_ant.center_x
        dy = target_y - self.controlled_ant.center_y
        dist = math.hypot(dx, dy)
        if dist <= 0.5:
            return
        speed = max(120.0, self.window.height * 0.25)
        step = min(dist, speed * dt)
        self.controlled_ant.center_x += dx / dist * step
        self.controlled_ant.center_y += dy / dist * step

    def _spawn_follower(self):
        """Add a new follower ant that joins the end of the line."""
        if not self.window:
            return
        height = self.window.height
        ant_target_w = max(18, int(height * 0.06))
        ant_img = self.asset_dir / "ant.png"
        if ant_img.exists():
            follower = self._load_scaled(str(ant_img), target_w=ant_target_w)
        else:
            follower = arcade.SpriteSolidColor(ant_target_w, ant_target_w, arcade.color.BROWN)
        anchor = self.followers[-1] if len(self.followers) else (self.queen if self.queen else None)
        if anchor:
            follower.center_x = anchor.center_x - 24
            follower.center_y = anchor.center_y
        else:
            follower.center_x = self.window.width * 0.15
            follower.center_y = self.window.height * 0.5
        self.followers.append(follower)
        self.actors.append(follower)

class MiniGame:
    def __init__(self):
        self.bar_x = 200
        self.direction = 1
        self.speed = 300  # px/sec
        self.target_zone = (350, 450)
        # Build sprites instead of using draw_* API
        self.sprites = arcade.SpriteList()
        # Background gray bar
        self.bg = arcade.SpriteSolidColor(400, 20, arcade.color.GRAY)
        self.bg.center_x = 400
        self.bg.center_y = 100
        self.sprites.append(self.bg)
        # Red zone indicator
        self.red = arcade.SpriteSolidColor(100, 30, arcade.color.RED)
        self.red.center_x = 400
        self.red.center_y = 100
        self.sprites.append(self.red)
        # Moving blue bar
        self.bar = arcade.SpriteSolidColor(20, 30, arcade.color.BLUE)
        self.bar.center_x = self.bar_x
        self.bar.center_y = 100
        self.sprites.append(self.bar)

    def reset(self):
        self.bar_x = 200
        self.direction = 1

    def update(self, dt):
        self.bar_x += self.direction * self.speed * dt
        if self.bar_x > 600 or self.bar_x < 200:
            self.direction *= -1
        # Sync sprite position
        if hasattr(self, 'bar') and self.bar:
            self.bar.center_x = self.bar_x

    def draw(self):
        if hasattr(self, 'sprites'):
            self.sprites.draw()

    def attempt_stop(self):
        return 350 <= self.bar_x <= 450


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = AntView()
    # When launching directly, call setup once before showing
    view.setup()
    window.show_view(view)
    arcade.run()

if __name__ == "__main__":
    main()