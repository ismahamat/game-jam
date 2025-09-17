import arcade
from .base import BaseView

PLAYER_MOVEMENT_SPEED = 5
TILE_SCALING = 0.5
scale = 0.3

class AtomView(BaseView):
    def __init__(self):
        super().__init__()

        self.player_list = arcade.SpriteList()         # Les atomes principaux
        self.bigatom_list = arcade.SpriteList()       # Le gros noyau
        self.atoms_exemple_list = arcade.SpriteList() # Mini-atomes en haut à droite


        # Fond
        self.background_color = arcade.color.BLACK

        # Index de l'atome actuellement contrôlé
        self.current_atom_index = 0
        self.background_list = arcade.SpriteList()  # Liste pour le fond


        # Touches pressées
        self.keys_held = {"up": False, "down": False, "left": False, "right": False}

    def setup(self):
        """Créer les atomes et l'UI"""
        self.player_list = arcade.SpriteList()
        atoms_coordinates = [[300,100],[500,200],[800,400],[450,630]]
        
        
        self.background_list = arcade.SpriteList()  # Liste pour le fond
        background = arcade.Sprite("images/bgimg.png")
        background.center_x = self.window.width/2
        background.center_y = self.window.height/2   
        background.width = self.window.width
        background.height = self.window.height
        self.background_list.append(background)    
        
        atom_images = ["images/atome_1.png", "images/atome_2.png", "images/atome_3.png", "images/atome_4.png"]

        # Atomes principaux
        for i, img_path in enumerate(atom_images):
            atom = arcade.Sprite(img_path, scale=TILE_SCALING)  # scale si besoin
            atom.center_x = atoms_coordinates[i][0]
            atom.center_y = atoms_coordinates[i][1]
            self.player_list.append(atom)

        # Gros atome (noyau)
        self.bigatom_list = arcade.SpriteList()
        bigatom = arcade.Sprite("images/atome_centre.png",scale=TILE_SCALING)
        bigatom.center_x = self.window.width/2 - 2
        bigatom.center_y = self.window.height/2 - 2
        self.bigatom_list.append(bigatom)

        # Mini-atoms en haut à droite
        self.atoms_exemple_list = arcade.SpriteList()
        for i, img_path in enumerate(atom_images):
            scale = 0.3 if i == self.current_atom_index else 0.15 # Plus grand pour l'atome actif
            atomex = arcade.Sprite(img_path, scale=scale)
            atomex.center_x = self.window.width - 150 + i*8
            atomex.center_y = self.window.height - 37
            self.atoms_exemple_list.append(atomex)

    def on_draw(self):
        super().on_draw()


        # Dessiner tous les atomes
        self.background_list.draw()
        self.player_list.draw()
        self.bigatom_list.draw()
        self.atoms_exemple_list.draw()

        # UI fixe en haut à gauche
        arcade.draw_rect_outline(arcade.rect.XYWH(120, self.window.height - 30,   # x, y du centre
        200, 40,),
                         arcade.color.WHITE)
    
        arcade.draw_text(
            "Echelle : ",
            70, self.window.height - 30,
            arcade.color.WHITE, 14,
            anchor_x="center", anchor_y="center"
        )
        
        #orbits
        arcade.draw_circle_outline(self.window.width/2, self.window.height/2, 130, arcade.color.YELLOW, 3)
        arcade.draw_circle_outline(self.window.width/2, self.window.height/2, 180, arcade.color.BLUE, 3)
        arcade.draw_circle_outline(self.window.width/2, self.window.height/2, 230, arcade.color.ORANGE, 3)
        arcade.draw_circle_outline(self.window.width/2, self.window.height/2, 280, arcade.color.PURPLE, 3)




        
        #UI Fixe haut droite
        arcade.draw_rect_outline(arcade.rect.XYWH(self.window.width-150, self.window.height - 30,   # x, y du centre
        200, 40,),
                         arcade.color.WHITE)
        
        arcade.draw_rect_outline(arcade.rect.XYWH(self.window.width-220, self.window.height - 30,   # x, y du centre
        40, 25,),
                         arcade.color.WHITE)
    
        arcade.draw_text(
            "Tab",
            self.window.width-220, self.window.height - 30,
            arcade.color.WHITE, 14,
            anchor_x="center", anchor_y="center"
        )
        
        arcade.draw_text(
            "Pour changer de POV",
            self.window.width-130, self.window.height - 20,
            arcade.color.WHITE, 7,
            anchor_x="center", anchor_y="center"
        )
        
        
        # Indiquer quel atome est actif
        active_atom = self.player_list[self.current_atom_index]
        arcade.draw_circle_outline(active_atom.center_x, active_atom.center_y, 20, arcade.color.BLACK, 2)

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.UP, arcade.key.W):
            self.keys_held["up"] = True
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.keys_held["down"] = True
        elif key in (arcade.key.LEFT, arcade.key.A):
            self.keys_held["left"] = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.keys_held["right"] = True
        elif key == arcade.key.TAB:
            # Passer à l'atome suivant
            self.current_atom_index = (self.current_atom_index + 1) % len(self.player_list)
        elif key == arcade.key.ESCAPE:
            self.setup()

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.UP, arcade.key.W):
            self.keys_held["up"] = False
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.keys_held["down"] = False
        elif key in (arcade.key.LEFT, arcade.key.A):
            self.keys_held["left"] = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.keys_held["right"] = False

    def on_update(self, delta_time):
        """Déplacer uniquement l'atome actif"""
        dx = dy = 0
        speed = PLAYER_MOVEMENT_SPEED

        if self.keys_held["up"]:
            dy += speed
        if self.keys_held["down"]:
            dy -= speed
        if self.keys_held["left"]:
            dx -= speed
        if self.keys_held["right"]:
            dx += speed

        # Déplacer l'atome actif
        active_atom = self.player_list[self.current_atom_index]
        active_atom.center_x += dx
        active_atom.center_y += dy

        # Mettre à jour la mini-vue des atomes pour montrer l'actif
        atom_images = ["images/atome_1.png", "images/atome_2.png", "images/atome_3.png", "images/atome_4.png"]

        for i, img_path in enumerate(atom_images):
            scale = 0.3 if i == self.current_atom_index else 0.15  # Plus grand pour l'atome actif
            atomex = arcade.Sprite(img_path, scale=scale)
            atomex.center_x = self.window.width - 150 + i*8
            atomex.center_y = self.window.height - 37
            self.atoms_exemple_list[i] = atomex
