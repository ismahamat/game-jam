# import arcade
# from .base import BaseView

# TILE_SCALING = 0.5
# PLAYER_MOVEMENT_SPEED = 5
# GRAVITY = 1
# PLAYER_JUMP_SPEED = 20


# class AtomView(BaseView):
#     def __init__(self):
#         super().__init__()

#         self.player_texture = None
#         self.player_sprite = None

#         # Crée les SpriteList vides par défaut
#         self.player_list = arcade.SpriteList()
#         self.wall_list = arcade.SpriteList(use_spatial_hash=True)

#         self.physics_engine = None
#         self.camera = None




#     def setup(self):
#         """Set up the game here. Call this function to restart the game."""
#                 # Charger la texture UNE seule fois
#         self.player_texture = arcade.load_texture(
#             "images/test.png"
#         )
        
#         self.camera = arcade.Camera2D()
        

#         # Créer le sprite UNE seule fois
#         self.player_sprite = arcade.Sprite(self.player_texture)
#         self.player_sprite.center_x = 64
#         self.player_sprite.center_y = 128
        
#         self.player_list = arcade.SpriteList()
#         self.player_list.append(self.player_sprite)
        
#         self.wall_list = arcade.SpriteList(use_spatial_hash=True)

#         for x in range(0, 1250, 64):
#             wall = arcade.Sprite(":resources:images/tiles/grassMid.png", scale=TILE_SCALING)
#             wall.center_x = x
#             wall.center_y = 32
#             self.wall_list.append(wall)
        
#         coordinate_list = [[512, 96], [256, 96], [768, 96]]
#         for coordinate in coordinate_list:
#             wall = arcade.Sprite(
#                 ":resources:images/tiles/boxCrate_double.png", scale=TILE_SCALING)
#             wall.position = coordinate
#             self.wall_list.append(wall)
            
#         self.physics_engine = arcade.PhysicsEnginePlatformer(
#             self.player_sprite, walls=self.wall_list, gravity_constant=GRAVITY
#         )
        
#         self.background_color = arcade.color.WHITE



#     def on_draw(self):
#         super().on_draw()
#         self.show_text_center("Atom - Prototype")

#         self.camera.use()

#         # Dessiner le sprite
#         self.player_list.draw()
#         self.wall_list.draw()
        

        
#     def on_key_press(self, key, modifiers):
#         """Called whenever a key is pressed."""

#         if key == arcade.key.ESCAPE:
#             self.setup()

#         if key == arcade.key.UP or key == arcade.key.W:
#             if self.physics_engine.can_jump():
#                 self.player_sprite.change_y = PLAYER_JUMP_SPEED

#         if key == arcade.key.LEFT or key == arcade.key.A:
#             self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
#         elif key == arcade.key.RIGHT or key == arcade.key.D:
#             self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

#     def on_key_release(self, key, modifiers):
#         """Called whenever a key is released."""

#         if key == arcade.key.LEFT or key == arcade.key.A:
#             self.player_sprite.change_x = 0
#         elif key == arcade.key.RIGHT or key == arcade.key.D:
#             self.player_sprite.change_x = 0
            
#     def on_update(self, delta_time):
#         """Movement and Game Logic"""
#         self.physics_engine.update()
#         self.camera.position = self.player_sprite.position


