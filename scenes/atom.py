import arcade
from .base import BaseView
import random
import math
from .ant import AntView
PLAYER_MOVEMENT_SPEED = 3
TILE_SCALING = 0.5

class AtomView(BaseView):
    def __init__(self):
        super().__init__()
        self.orbit_rotation_angle = 0
        self.shrink_speed = 0.01
        self.sound = arcade.load_sound("music/AtomMusic2.mp3")
        self.successsound = arcade.load_sound("music/success2.mp3")

        self.music_player = None
        self.music_played = False



        self.atom_spawn_timer = 0  # compteur pour spawn
        self.atom_spawn_interval = 60  # frames entre deux spawns (~1 sec à 60 FPS)
        self.camera = arcade.Camera2D()  # caméra principale
        self.shake_duration = 0
        self.shake_magnitude = 5  # force du shake en pixels
        self.camera_base_position = (self.window.width / 2, self.window.height / 2)

        self.player_list = arcade.SpriteList()         # Les atomes principaux
        self.bigatom_list = arcade.SpriteList()       # Le gros noyau
        self.atoms_exemple_list = arcade.SpriteList() # Mini-atomes en haut à droite

        self.blackcolor = 0
        self.atomdanger_list = arcade.SpriteList() 
        self.bigatomdanger_list = arcade.SpriteList()
        self.isWin = False
        self.isFinishedAtom = False
        self.scalevar = 4

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
        self.bigatom_list = arcade.SpriteList()
        self.atoms_exemple_list = arcade.SpriteList()
        self.atomdanger_list = arcade.SpriteList() 
        self.bigatomdanger_list = arcade.SpriteList()


        # Background
        self.background_list = arcade.SpriteList()
        background = arcade.Sprite("images/bgatome2.png")
        background.center_x = self.window.width / 2
        background.center_y = self.window.height / 2
        background.width = self.window.width
        background.height = self.window.height
        self.background_list.append(background)

        # Atomes principaux
        self.atom_images = [
            arcade.load_texture("images/atome_blanc_rouge.png"),
            arcade.load_texture("images/atome_light_blue_rouge.png"),
            arcade.load_texture("images/atome_sky_blue_rouge.png"),
            arcade.load_texture("images/atome_vraibleu_rouge.png")
        ]

        self.special_images = [
            arcade.load_texture("images/atome_blanc_vert.png"),
            arcade.load_texture("images/atome_light_blue_vert.png"),
            arcade.load_texture("images/atome_sky_blue_vert.png"),
            arcade.load_texture("images/atome_vraibleu_vert.png")
        ]

        atoms_coordinates = [[random.randint(100, 900), random.randint(100, 600)] for _ in range(4)]
        for i, texture in enumerate(self.atom_images):
            atom = arcade.Sprite()
            atom.texture = texture
            atom.center_x = atoms_coordinates[i][0]
            atom.center_y = atoms_coordinates[i][1]
            atom.on_orbit = False  # <- flag pour savoir si le son a été joué
            self.player_list.append(atom)
            
        def random_coord(ranges):
            """Choisit un nombre aléatoire dans une liste d'intervalles [(min1,max1), (min2,max2), ...]"""
            # Choisir un intervalle au hasard
            r = random.choice(ranges)
            # Choisir un nombre dans cet intervalle
            return random.randint(r[0], r[1])

        # Exemple pour 4 coordonnées
        atomsdanger_coordinates = [
            [random_coord([(0, 300), (500, 1000)]),  # x : 0-150 ou 750-1000
            random_coord([(0, 300), (500, 700)])]  # y : 0-100 ou 600-700
            for _ in range(30)
        ]    
        
        for i in range(0,30):
            atom = arcade.Sprite("images/react_vert2.png", scale=0.1)
            atom.center_x = atomsdanger_coordinates[i][0]
            atom.center_y = atomsdanger_coordinates[i][1]
            self.atomdanger_list.append(atom)

        # Gros atome
        bigatom = arcade.Sprite("images/atome_centre.png", scale=self.scalevar)
        bigatom.center_x = self.window.width / 2 - 2
        bigatom.center_y = self.window.height / 2 - 2
        self.bigatom_list.append(bigatom)
        
        
        atomsdanger_coordinates = [
            [random_coord([(-300, 150), (750, 1300)]),  # x : 0-150 ou 750-1000
            random_coord([(-150, 100), (600, 1000)])]  # y : 0-100 ou 600-700
        ]    
        
        # Gros atome danger
        bigatomdanger = arcade.Sprite("images/react_red2.png", scale=TILE_SCALING)
        bigatomdanger.center_x = atomsdanger_coordinates[0][0]
        bigatomdanger.center_y = atomsdanger_coordinates[0][1]
        self.bigatomdanger_list.append(bigatomdanger)
        

        # Mini-atoms en haut à droite
        for i, texture in enumerate(self.atom_images):
            atomex = arcade.Sprite()
            atomex.texture = texture
            atomex.center_x = self.window.width - 150 + i*8
            atomex.center_y = self.window.height - 37
            atomex.scale = 0.15 if i == self.current_atom_index else 0.1
            self.atoms_exemple_list.append(atomex)
        
        if not self.music_played:
            arcade.play_sound(self.sound)
            self.music_played = True
        

    def on_draw(self):
        super().on_draw()
        
        self.camera.use()

        # Dessiner tous les atomes
        self.background_list.draw()
        self.player_list.draw()
        self.atoms_exemple_list.draw()
        self.atomdanger_list.draw()
        self.bigatomdanger_list.draw()


        # UI fixe en haut à gauche
        arcade.draw_rect_outline(arcade.rect.XYWH(120, self.window.height - 30,   # x, y du centre
        200, 40,),
                         arcade.color.WHITE)
    
        arcade.draw_text(
            "Echelle : atome",
            120, self.window.height - 30,
            arcade.color.WHITE, 14,
            anchor_x="center", anchor_y="center"
        )
        
        def draw_rotating_orbit(center_x, center_y, radius, base_color, rotation_angle, angle_offset=0, steps=60):
            for i in range(steps):
                angle = (360 / steps) * i + rotation_angle + angle_offset  # on ajoute l'offset ici
                rad1 = math.radians(angle)
                rad2 = math.radians(angle + 360/steps)
                color = (
                    base_color[0],
                    base_color[1],
                    base_color[2],
                    int(255 * i / steps)
                )
                x1 = center_x + math.cos(rad1) * radius
                y1 = center_y + math.sin(rad1) * radius
                x2 = center_x + math.cos(rad2) * radius
                y2 = center_y + math.sin(rad2) * radius
                arcade.draw_line(x1, y1, x2, y2, color, 3)
                
        def draw_rotating_orbit2(center_x, center_y, radius, base_color, rotation_angle, angle_offset=0, steps=60):
            for i in range(steps):
                angle = (360 / steps) * i - rotation_angle + angle_offset  # on ajoute l'offset ici
                rad1 = math.radians(angle)
                rad2 = math.radians(angle + 360/steps)
                color = (
                    base_color[0],
                    base_color[1],
                    base_color[2],
                    int(255 * i / steps)
                )
                x1 = center_x + math.cos(rad1) * radius
                y1 = center_y + math.sin(rad1) * radius
                x2 = center_x + math.cos(rad2) * radius
                y2 = center_y + math.sin(rad2) * radius
                arcade.draw_line(x1, y1, x2, y2, color, 3)
                
                
        draw_rotating_orbit(self.window.width/2, self.window.height/2, 130, arcade.color.LIGHT_BLUE, self.orbit_rotation_angle, angle_offset=0)
        draw_rotating_orbit2(self.window.width/2, self.window.height/2, 180, arcade.color.SKY_BLUE, self.orbit_rotation_angle, angle_offset=90)
        draw_rotating_orbit(self.window.width/2, self.window.height/2, 230, arcade.color.DODGER_BLUE, self.orbit_rotation_angle, angle_offset=180)
        draw_rotating_orbit2(self.window.width/2, self.window.height/2, 280, arcade.color.BLUE, self.orbit_rotation_angle, angle_offset=270)

    



        
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
        
        
        #ESCP
        
        arcade.draw_rect_outline(arcade.rect.XYWH(self.window.width-150, self.window.height - 75,   # x, y du centre
        200, 40,),
                         arcade.color.WHITE)
        
        arcade.draw_rect_outline(arcade.rect.XYWH(self.window.width-220, self.window.height - 75,   # x, y du centre
        40, 25,),
                         arcade.color.WHITE)
        
        arcade.draw_text(
            "Esc",
            self.window.width-220, self.window.height - 75,
            arcade.color.WHITE, 14,
            anchor_x="center", anchor_y="center"
        )
        
        arcade.draw_text(
            "Pour recommencer",
            self.window.width-120, self.window.height - 75,
            arcade.color.WHITE, 7,
            anchor_x="center", anchor_y="center"
        )
        
        
        # Indiquer quel atome est actif
        active_atom = self.player_list[self.current_atom_index]
        arcade.draw_circle_outline(active_atom.center_x, active_atom.center_y, 20, arcade.color.BLACK, 2)
        self.bigatom_list.draw()
        if self.blackcolor > 0:
            cam_x, cam_y = self.camera.position
            arcade.draw_rect_filled(arcade.rect.XYWH(cam_x, cam_y,1280, 720),(0,0,0,self.blackcolor))


    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.setup()
        if key in (arcade.key.UP, arcade.key.W):
            self.keys_held["up"] = True
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.keys_held["down"] = True
        elif key in (arcade.key.LEFT, arcade.key.A):
            self.keys_held["left"] = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.keys_held["right"] = True
        elif key == arcade.key.TAB and not self.isWin:  # seulement bloquer ça
            self.current_atom_index = (self.current_atom_index + 1) % len(self.player_list)


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
        
        # Animation du gros atome
        bigatom = self.bigatom_list[0]

        # Prendre le scale actuel (tuple ou float)
        current_scale = bigatom.scale
        if isinstance(current_scale, tuple):
            current_scale = current_scale[0]  # scale uniforme

        if not self.isFinishedAtom:
            # Rétrécir jusqu'à TILE_SCALING
            self.shrink_speed += 0.0003
            if current_scale > TILE_SCALING:
                current_scale -= self.shrink_speed
                if current_scale < TILE_SCALING:
                    current_scale = TILE_SCALING

        elif self.isFinishedAtom:
            # Grossir après la fin
            self.shrink_speed += 0.00003  # tu peux utiliser une vitesse différente si tu veux
            if current_scale < 6:
                current_scale += self.shrink_speed  # <-- ici on ajoute pour grossir
                if current_scale > 6:
                    current_scale = 6
            if self.blackcolor < 245:
                self.blackcolor += 3
            if self.blackcolor < 254 and self.blackcolor > 244:
                self.blackcolor += 1
            
            if not hasattr(self, "next_scene_timer"):
                self.next_scene_timer = 300  # 5 secondes à 60 FPS

            # Décrémenter le timer
            self.next_scene_timer -= 1
            if self.next_scene_timer <= 0:
                # Passer à la scène suivante
                from .FourmiDialogueScene import FourmiDialogueScene
                self.window.show_view(FourmiDialogueScene())


        # Réappliquer le scale
        bigatom.scale = (current_scale, current_scale)

        self.orbit_rotation_angle += 1  # vitesse de rotation en degrés        
        
        repulsion_distance = 50     # distance à laquelle la répulsion commence
        repulsion_strength = 2      # force de déplacement

        for player in self.player_list:
            for danger in self.atomdanger_list:
                dx = player.center_x - danger.center_x
                dy = player.center_y - danger.center_y
                distance = (dx**2 + dy**2)**0.5

                if distance < repulsion_distance and distance > 0:
                    # Normaliser le vecteur et appliquer la force
                    dx /= distance
                    dy /= distance
                    player.center_x += dx * repulsion_strength
                    player.center_y += dy * repulsion_strength
        
        
        # -------------------
        # Déplacement du joueur
        # -------------------
        dx = dy = 0
        speed = PLAYER_MOVEMENT_SPEED

        if not self.isWin:
            if self.keys_held["up"]:
                dy += speed
            if self.keys_held["down"]:
                dy -= speed
            if self.keys_held["left"]:
                dx -= speed
            if self.keys_held["right"]:
                dx += speed

        active_atom = self.player_list[self.current_atom_index]
        active_atom.center_x += dx
        active_atom.center_y += dy

        # -------------------
        # Paramètres des orbites
        # -------------------
        center_x = self.window.width / 2
        center_y = self.window.height / 2
        orbit_radii = [130, 180, 230, 280]
        orbitsok = [False, False, False, False]

        def all_orbits_ok(tab):
            return all(tab)

        attraction_speed = 0.3
        attraction_speed_big_atom_danger = 0.07

        for i, atom in enumerate(self.player_list):
            distance = ((atom.center_x - center_x) ** 2 + (atom.center_y - center_y) ** 2) ** 0.5
            if abs(distance - orbit_radii[i]) < 5:
                atom.texture = self.special_images[i]
                atom.scale = 0.1
                orbitsok[i] = True  # <- important !
                if not atom.on_orbit:
                    arcade.play_sound(self.successsound)
                    atom.on_orbit = True  # on marque qu'il a déjà joué le son
            else:
                atom.texture = self.atom_images[i]
                atom.scale = 0.1
                atom.on_orbit = False  # reset si l'atome sort de l'orbite

        # Automatiquement passer à l'atome suivant si l'actif est sur son orbite
        active_atom = self.player_list[self.current_atom_index]
        active_index = self.current_atom_index
        distance = ((active_atom.center_x - center_x) ** 2 + (active_atom.center_y - center_y) ** 2) ** 0.5
        if abs(distance - orbit_radii[active_index]) < 5:
            # Simuler "Tab" : passer au prochain atome
            self.current_atom_index = (self.current_atom_index + 1) % len(self.player_list)

        # Boost si toutes les orbites sont OK
        if all_orbits_ok(orbitsok):
            attraction_speed_big_atom_danger = 1.3
            self.isWin = True
            if abs(self.bigatomdanger_list[0].center_x - self.window.width/2) < 1 and abs(self.bigatomdanger_list[0].center_y - self.window.height/2) < 1:
                self.isFinishedAtom = True
            if self.shake_duration == 0:
                self.shake_duration = 20  # frames de shake (~1/3 sec)
        else:
            self.isWin = False

        # Mettre à jour la mini-vue des atomes pour montrer l'actif
        for i, atomex in enumerate(self.atoms_exemple_list):
            atomex.scale = 0.15 if i == self.current_atom_index else 0.1

        # -------------------
        # Déplacement des atomes dangers
        # -------------------
        for i, atom in enumerate(self.atomdanger_list):
            dx = center_x - atom.center_x
            dy = center_y - atom.center_y
            distance = (dx**2 + dy**2)**0.5
            if distance > 1:
                dx /= distance
                dy /= distance
                atom.center_x += dx * attraction_speed
                atom.center_y += dy * attraction_speed
            if i%2 == 0:
                atom.angle -= 1.4
            else:
                atom.angle += 1.4



        for atom in self.bigatomdanger_list:
            dx = center_x - atom.center_x
            dy = center_y - atom.center_y
            distance = (dx**2 + dy**2)**0.5
            if distance > 1:
                dx /= distance
                dy /= distance
                atom.center_x += dx * attraction_speed_big_atom_danger
                atom.center_y += dy * attraction_speed_big_atom_danger
            atom.angle += 0.6
            
            
            
        self.atom_spawn_timer -= 1
        if self.atom_spawn_timer <= 0:
            # Choisir une position aléatoire en dehors du centre
            spawn_x = random.choice([random.randint(-200, 100), random.randint(700, 1300)])
            spawn_y = random.choice([random.randint(-200, 100), random.randint(600, 1000)])

            atom = arcade.Sprite("images/react_vert2.png", scale=0.1)
            atom.center_x = spawn_x
            atom.center_y = spawn_y
            self.atomdanger_list.append(atom)

            # Réinitialiser le timer
            self.atom_spawn_timer = self.atom_spawn_interval
        # -------------------
        # Gestion de la caméra et du shake
        # -------------------
        if self.shake_duration > 0:
            self.shake_duration -= 1
            offset_x = random.randint(-self.shake_magnitude, self.shake_magnitude)
            offset_y = random.randint(-self.shake_magnitude, self.shake_magnitude)
            # Déplacer la caméra autour de sa position de base
            self.camera.position = (
                self.window.width / 2 + offset_x,
                self.window.height / 2 + offset_y
            )
        else:
            # Remettre la caméra au centre
            self.camera.position = (self.window.width / 2, self.window.height / 2)