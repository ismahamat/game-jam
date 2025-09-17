import random
import math
from pathlib import Path
import arcade
from .base import BaseView


ROAD_MARGIN = 96  # height of sidewalks at top/bottom
LEASH_LENGTH = 140.0
OWNER_SPEED = 70.0
DOG_SPEED = 160.0
NUM_BONES = 5
CAR_MIN_INTERVAL = 2.2
CAR_MAX_INTERVAL = 3.8
CAR_SPEED_RANGE = (5.0, 7.0)

# Target on-screen sizes for image assets (in pixels, width-based)
OWNER_TARGET_W = 64
DOG_TARGET_W = 56
BONE_TARGET_W = 28
CAR_TARGET_W = 90


class HumanDogView(BaseView):
    def __init__(self):
        super().__init__()
        # Use conservative colors available in older Arcade versions
        self.background_color = arcade.color.DARK_GRAY

        # Sprites / lists
        self.owner: arcade.Sprite | None = None
        self.dog: arcade.Sprite | None = None
        self.bones = arcade.SpriteList()
        self.cars = arcade.SpriteList()
        self._bg = arcade.SpriteList()
        self._actors = arcade.SpriteList()
        self._bg_image_list = arcade.SpriteList()
        self._effects = arcade.SpriteList()

        # Input state
        self.keys_held: set[int] = set()

        # Owner wandering
        self._owner_dir: arcade.Vector = (0.0, 0.0)
        self._owner_change_timer: float = 0.0

        # Cars spawning
        self._car_timer: float = 0.0
        self._next_car_in: float = random.uniform(CAR_MIN_INTERVAL, CAR_MAX_INTERVAL)

        # Gameplay
        self.score: int = 0
        self.game_over: bool = False
        self._elapsed: float = 0.0
        self._repulse_cooldown: float = 0.0
        self._owner_repulse_target_y: float | None = None
        self._owner_repulse_speed: float = 520.0  # px/s for glide

        # Asset dir
        self.asset_dir: Path = Path(__file__).resolve().parent.parent / "assets" / "human_dog"

    # ----- Lifecycle -----
    def on_show_view(self):
        super().on_show_view()
        self._setup_sprites()

    def _setup_sprites(self):
        width = self.window.width if self.window else 800
        height = self.window.height if self.window else 600

        # Background image if provided, else draw blocks
        bg_path = self.asset_dir / "background.png"
        self._bg_image_list = arcade.SpriteList()
        if bg_path.exists():
            bg_sprite = self._load_scaled(str(bg_path), target_w=width)
            # Stretch to cover height if needed
            try:
                # Some Arcade versions allow separate scale on x/y using attributes
                tex = bg_sprite.texture
                if tex and tex.height:
                    desired_h = height
                    current_h = tex.height * bg_sprite.scale
                    scale_adjust = desired_h / current_h
                    bg_sprite.scale *= scale_adjust
            except Exception:
                pass
            bg_sprite.center_x = width / 2
            bg_sprite.center_y = height / 2
            self._bg_image_list.append(bg_sprite)
        
        # Background blocks as sprites (compatible across Arcade versions)
        self._bg = arcade.SpriteList()
        # Grass top/bottom
        sprite = arcade.SpriteSolidColor(int(width), 30, arcade.color.DARK_GREEN)
        sprite.center_x = width / 2
        sprite.center_y = height - 15
        self._bg.append(sprite)
        sprite = arcade.SpriteSolidColor(int(width), 30, arcade.color.DARK_GREEN)
        sprite.center_x = width / 2
        sprite.center_y = 15
        self._bg.append(sprite)

        # Sidewalks
        sidewalk_height = max(0, ROAD_MARGIN - 30)
        if sidewalk_height > 0:
            sprite = arcade.SpriteSolidColor(int(width), int(sidewalk_height), arcade.color.GRAY)
            sprite.center_x = width / 2
            sprite.center_y = height - (30 + ROAD_MARGIN) / 2
            self._bg.append(sprite)
            sprite = arcade.SpriteSolidColor(int(width), int(sidewalk_height), arcade.color.GRAY)
            sprite.center_x = width / 2
            sprite.center_y = (30 + ROAD_MARGIN) / 2
            self._bg.append(sprite)

        # Road
        road_height = height - 2 * ROAD_MARGIN
        sprite = arcade.SpriteSolidColor(int(width), int(road_height), arcade.color.BLACK)
        sprite.center_x = width / 2
        sprite.center_y = height / 2
        self._bg.append(sprite)

        # Owner sprite
        self.owner = self._make_owner_sprite()
        self.owner.center_x = width * 0.6
        self.owner.center_y = height * 0.5

        # Dog sprite
        self.dog = self._make_dog_sprite()
        self.dog.center_x = self.owner.center_x - 50
        self.dog.center_y = self.owner.center_y - 10

        # Actors list for drawing
        self._actors = arcade.SpriteList()
        self._actors.append(self.owner)
        self._actors.append(self.dog)

        # Bones
        self.bones = arcade.SpriteList()
        while len(self.bones) < NUM_BONES:
            self._spawn_bone(width, height)

        # Cars
        self.cars = arcade.SpriteList()
        # Effects
        self._effects = arcade.SpriteList()

        # Reset state
        self.keys_held.clear()
        self._pick_new_owner_direction()
        self._car_timer = 0.0
        self._next_car_in = random.uniform(CAR_MIN_INTERVAL, CAR_MAX_INTERVAL)
        self.score = 0
        self.game_over = False

    # ----- Drawing -----
    def on_draw(self):
        super().on_draw()
        # Background
        if len(self._bg_image_list) > 0:
            self._bg_image_list.draw()
        else:
            self._bg.draw()
        # Actors (owner + dog)
        self._actors.draw()
        self.bones.draw()
        self.cars.draw()
        # Collision effects (draw on top)
        self._effects.draw()

        # Draw leash
        if self.owner and self.dog:
            arcade.draw_line(
                self.owner.center_x,
                self.owner.center_y,
                self.dog.center_x,
                self.dog.center_y,
                arcade.color.BLACK,
                2,
            )

        # UI
        if self.window:
            arcade.draw_text(
                f"Score: {self.score}",
                10,
                self.window.height - 30,
                arcade.color.WHITE,
                20,
            )
            arcade.draw_text(
                "Humain & Chien",
                40,
                self.window.height - 120,
                arcade.color.WHITE,
                40,
            )
        if self.game_over and self.window:
            self.show_text_center("Collision ! Appuie sur ESC pour revenir")

    def _draw_background(self):
        # Kept for compatibility; no-op because background is prebuilt as sprites
        return

        # Center dashed line
        for x in range(40, w, 80):
            # Use sprites for dashed line to avoid draw_* API variance
            dash = arcade.SpriteSolidColor(40, 6, arcade.color.YELLOW)
            dash.center_x = x
            dash.center_y = h / 2
            dash.draw()

    # ----- Update -----
    def on_update(self, delta_time: float):
        if self.game_over:
            return
        if not self.window:
            return
        # Difficulty scaling over time
        self._elapsed += delta_time
        if self._repulse_cooldown > 0:
            self._repulse_cooldown = max(0.0, self._repulse_cooldown - delta_time)

        self._update_owner(delta_time)
        self._update_dog(delta_time)
        self._check_bone_collisions()
        self._maybe_spawn_cars(delta_time)
        self._update_cars(delta_time)
        self._check_car_collisions()
        self._repulse_owner_from_cars()

    # ----- Input -----
    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.ESCAPE and self.window:
            from .menu import MenuView
            self.window.show_view(MenuView())
            return
        self.keys_held.add(key)

    def on_key_release(self, key: int, modifiers: int):
        self.keys_held.discard(key)

    # ----- Owner wandering -----
    def _pick_new_owner_direction(self):
        angle = random.uniform(0, 2 * math.pi)
        self._owner_dir = (math.cos(angle), math.sin(angle))
        # Change again in 0.8–2.0 seconds
        self._owner_change_timer = random.uniform(0.8, 2.0)

    def _update_owner(self, dt: float):
        if not self.owner or not self.window:
            return
        self._owner_change_timer -= dt
        if self._owner_change_timer <= 0:
            self._pick_new_owner_direction()

        dx = self._owner_dir[0] * OWNER_SPEED * dt
        # If in repulse glide, override dy to glide toward target
        if self._owner_repulse_target_y is not None:
            distance_y = self._owner_repulse_target_y - self.owner.center_y
            step = max(-self._owner_repulse_speed * dt, min(self._owner_repulse_speed * dt, distance_y))
            dy = step
            # Close enough -> snap and end glide
            if abs(distance_y) <= 2.0:
                self.owner.center_y = self._owner_repulse_target_y
                self._owner_repulse_target_y = None
                dy = 0.0
        else:
            dy = self._owner_dir[1] * OWNER_SPEED * dt
        new_x = self.owner.center_x + dx
        new_y = self.owner.center_y + dy

        # Allow owner to step onto sidewalks slightly (more than cars)
        sidewalk_allowance = 30
        road_top = self.window.height - ROAD_MARGIN + sidewalk_allowance
        road_bottom = ROAD_MARGIN - sidewalk_allowance
        new_x = max(16, min(self.window.width - 16, new_x))
        new_y = max(road_bottom + 16, min(road_top - 16, new_y))
        self.owner.center_x = new_x
        self.owner.center_y = new_y

    # ----- Dog control + leash -----
    def _update_dog(self, dt: float):
        if not self.dog or not self.owner or not self.window:
            return
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

        proposed_x = self.dog.center_x + move_x * DOG_SPEED * dt
        proposed_y = self.dog.center_y + move_y * DOG_SPEED * dt

        # Keep dog within window bounds first
        road_top = self.window.height - ROAD_MARGIN
        road_bottom = ROAD_MARGIN
        proposed_x = max(16, min(self.window.width - 16, proposed_x))
        proposed_y = max(road_bottom + 12, min(road_top - 12, proposed_y))

        # Enforce leash length
        vec_x = proposed_x - self.owner.center_x
        vec_y = proposed_y - self.owner.center_y
        dist = math.hypot(vec_x, vec_y)
        if dist > LEASH_LENGTH:
            scale = LEASH_LENGTH / dist
            proposed_x = self.owner.center_x + vec_x * scale
            proposed_y = self.owner.center_y + vec_y * scale

        self.dog.center_x = proposed_x
        self.dog.center_y = proposed_y

    # ----- Bones -----
    def _spawn_bone(self, width: int, height: int):
        # Bone sprite (image if available, else placeholder)
        bone = self._make_bone_sprite()
        # Ensure it spawns on the road and not too close to owner
        x = random.uniform(40, width - 40)
        y = random.uniform(ROAD_MARGIN + 24, height - ROAD_MARGIN - 24)
        bone.center_x = x
        bone.center_y = y
        self.bones.append(bone)

    def _check_bone_collisions(self):
        if not self.dog:
            return
        hit_list = arcade.check_for_collision_with_list(self.dog, self.bones)
        for bone in hit_list:
            bone.remove_from_sprite_lists()
            self.score += 1
        # Maintain 5 bones
        while len(self.bones) < NUM_BONES and self.window:
            self._spawn_bone(self.window.width, self.window.height)

    # ----- Cars -----
    def _maybe_spawn_cars(self, dt: float):
        self._car_timer += dt
        # Difficulty factor grows ~ linearly then caps
        difficulty = min(3.0, self._elapsed / 30.0)  # after ~90s reaches cap
        # Allow more concurrent cars as difficulty rises
        max_cars = 2 + int(difficulty * 2)
        if self._car_timer >= self._next_car_in and self.window and len(self.cars) < max_cars:
            self._car_timer = 0.0
            base_interval = random.uniform(CAR_MIN_INTERVAL, CAR_MAX_INTERVAL)
            # Spawn faster with higher difficulty
            self._next_car_in = max(0.6, base_interval / (1.0 + 0.6 * difficulty))
            self._spawn_car(self.window.width, self.window.height)

    def _spawn_car(self, width: int, height: int):
        # Car sprite (image if available, else colored rectangle)
        color_choice = random.choice(["red", "blue", "yellow"])
        car = self._make_car_sprite(color_choice)
        # Keep cars fully on the road, away from sidewalks
        lane_padding = 50  # distance from road edges
        road_top = height - ROAD_MARGIN - lane_padding
        road_bottom = ROAD_MARGIN + lane_padding
        start_from_left = random.choice([True, False])
        car.center_y = random.uniform(road_bottom, road_top)
        # Increase speed with difficulty
        difficulty = min(3.0, self._elapsed / 30.0)
        base_speed = random.uniform(*CAR_SPEED_RANGE)
        speed = base_speed * (1.0 + 0.5 * difficulty)
        if start_from_left:
            car.center_x = -60
            car.change_x = speed
            # PNG faces up; rotate to face forward (toward movement)
            try:
                car.angle = 90
            except Exception:
                pass
        else:
            car.center_x = width + 60
            car.change_x = -speed
            # Rotate to face forward (toward movement)
            try:
                car.angle = -90
            except Exception:
                pass
        # Use texture-derived hitbox for accurate collisions
        self._set_texture_hitbox(car)
        self.cars.append(car)

    def _update_cars(self, dt: float):
        if not self.window:
            return
        self.cars.update()
        # Remove off-screen cars
        lane_padding = 50
        road_top = self.window.height - ROAD_MARGIN - lane_padding
        road_bottom = ROAD_MARGIN + lane_padding
        for car in list(self.cars):
            # Clamp Y to the road band just in case
            if car.center_y > road_top:
                car.center_y = road_top
            elif car.center_y < road_bottom:
                car.center_y = road_bottom
            if car.center_x < -100 or car.center_x > self.window.width + 100:
                car.remove_from_sprite_lists()

    def _check_car_collisions(self):
        if not self.dog:
            return
        hit_cars = arcade.check_for_collision_with_list(self.dog, self.cars)
        if hit_cars:
            # Spawn explosion midway between dog and each car
            for car in hit_cars:
                mid_x = (self.dog.center_x + car.center_x) / 2.0
                mid_y = (self.dog.center_y + car.center_y) / 2.0
                size = 1.1 * max(self.dog.width, self.dog.height, car.width, car.height)
                self._spawn_paf(mid_x, mid_y, size)
            self.game_over = True

    # ----- Asset helpers -----
    def _make_owner_sprite(self) -> arcade.Sprite:
        img = self.asset_dir / "owner.png"
        if img.exists():
            return self._load_scaled(str(img), target_w=OWNER_TARGET_W)
        return arcade.SpriteSolidColor(28, 28, arcade.color.ORANGE)

    def _make_dog_sprite(self) -> arcade.Sprite:
        img = self.asset_dir / "dog.png"
        if img.exists():
            return self._load_scaled(str(img), target_w=DOG_TARGET_W)
        return arcade.SpriteSolidColor(30, 20, arcade.color.DARK_BROWN)

    def _make_bone_sprite(self) -> arcade.Sprite:
        img = self.asset_dir / "bone.png"
        if img.exists():
            return self._load_scaled(str(img), target_w=BONE_TARGET_W)
        return arcade.SpriteSolidColor(24, 12, arcade.color.ORANGE)

    def _make_car_sprite(self, color: str) -> arcade.Sprite:
        img = self.asset_dir / f"car_{color}.png"
        if img.exists():
            return self._load_scaled(str(img), target_w=CAR_TARGET_W)
        color_map = {
            "red": arcade.color.RED,
            "blue": arcade.color.BLUE,
            "yellow": arcade.color.YELLOW,
        }
        return arcade.SpriteSolidColor(52, 26, color_map.get(color, arcade.color.RED))

    def _load_scaled(self, path: str, target_w: int) -> arcade.Sprite:
        """Load a sprite and scale it so its width equals target_w pixels.

        Keeps original aspect ratio. Falls back to scale 1.0 if texture not ready.
        """
        sprite = arcade.Sprite(path, scale=1.0)
        # Some Arcade versions load texture lazily; ensure texture exists
        texture = sprite.texture
        if texture and texture.width:
            sprite.scale = target_w / float(texture.width)
        # Prefer detailed/texture hit box when available
        self._set_texture_hitbox(sprite)
        return sprite

    def _shrink_hitbox(self, sprite: arcade.Sprite, shrink_px: int = 6):
        """Make a smaller rectangular hitbox inside the sprite to reduce false positives.

        Deprecated in favor of _set_hitbox_factor.
        """
        try:
            tex = sprite.texture
            if not tex:
                return
            w = tex.width * sprite.scale
            h = tex.height * sprite.scale
            half_w = max(1.0, w / 2 - shrink_px)
            half_h = max(1.0, h / 2 - shrink_px)
            points = [
                (-half_w, -half_h),
                (half_w, -half_h),
                (half_w, half_h),
                (-half_w, half_h),
            ]
            # Older Arcade: set_hit_box; newer: hit_box algorithm or set_hit_box
            if hasattr(sprite, "set_hit_box"):
                sprite.set_hit_box(points)
        except Exception:
            pass

    def _set_hitbox_factor(self, sprite: arcade.Sprite, factor: float = 0.7):
        """Set a rectangular hitbox as a percentage of the sprite's visual size."""
        try:
            tex = sprite.texture
            if not tex:
                return
            w = tex.width * sprite.scale * factor
            h = tex.height * sprite.scale * factor
            half_w = max(1.0, w / 2)
            half_h = max(1.0, h / 2)
            points = [
                (-half_w, -half_h),
                (half_w, -half_h),
                (half_w, half_h),
                (-half_w, half_h),
            ]
            if hasattr(sprite, "set_hit_box"):
                sprite.set_hit_box(points)
        except Exception:
            pass

    def _set_texture_hitbox(self, sprite: arcade.Sprite):
        """Use the texture's hit box points if available for near-perfect collisions."""
        try:
            tex = sprite.texture
            if tex is not None:
                points = None
                # Many Arcade versions expose precomputed hit box points
                if hasattr(tex, "hit_box_points"):
                    points = tex.hit_box_points
                # Fallback: use factor rectangle if not available
                if points and hasattr(sprite, "set_hit_box"):
                    sprite.set_hit_box(points)
                else:
                    self._set_hitbox_factor(sprite, factor=0.8)
        except Exception:
            pass

    def _repulse_owner_from_cars(self):
        """If a car is about to intersect the owner horizontally, push the owner vertically
        by approximately the car height to avoid getting crushed.
        """
        if not self.owner or self._repulse_cooldown > 0:
            return
        for car in self.cars:
            # Close in X (car approaching the owner horizontally)
            near_x = abs(car.center_x - self.owner.center_x) < (car.width / 2 + self.owner.width / 2 + 10)
            # Almost same lane in Y
            near_y = abs(car.center_y - self.owner.center_y) < (car.height * 0.6)
            if near_x and near_y:
                # Move owner away from car along Y by one car height
                move_up = self.owner.center_y <= car.center_y
                delta_y = -car.height if move_up else car.height
                new_y = self.owner.center_y + delta_y
                # Keep owner within allowed sidewalk range
                sidewalk_allowance = 30
                road_top = (self.window.height if self.window else 600) - ROAD_MARGIN + sidewalk_allowance
                road_bottom = ROAD_MARGIN - sidewalk_allowance
                new_y = max(road_bottom + 16, min(road_top - 16, new_y))
                # Set glide target instead of teleporting
                self._owner_repulse_target_y = new_y
                self._repulse_cooldown = 0.45
                break

    # ----- Effects -----
    def _spawn_paf(self, x: float, y: float, target_w: float):
        img = self.asset_dir / "paf.png"
        if img.exists():
            sprite = self._load_scaled(str(img), target_w=int(target_w))
        else:
            sprite = arcade.SpriteSolidColor(int(target_w), int(target_w), arcade.color.YELLOW_ORANGE)
        sprite.center_x = x
        sprite.center_y = y
        self._effects.append(sprite)

