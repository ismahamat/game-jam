"""
Gestionnaire centralisé des effets sonores pour le jeu OUT OF SCALE.

Ce module gère le chargement, la lecture et le contrôle du volume des effets sonores.
Il utilise arcade.Sound pour une intégration optimale avec le framework.
"""

import arcade
import os
from pathlib import Path
from typing import Dict, Optional
import logging

# Configuration du logging pour déboguer les sons
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SoundManager:
    """Gestionnaire centralisé des sons du jeu."""
    
    def __init__(self, sounds_directory: str = "sounds"):
        """
        Initialise le gestionnaire de sons.
        
        Args:
            sounds_directory: Chemin vers le dossier contenant les fichiers audio
        """
        self.sounds_directory = Path(sounds_directory)
        self.sounds: Dict[str, arcade.Sound] = {}
        self.master_volume = 1.0
        self.sfx_volume = 0.7
        self.music_volume = 0.5
        self.muted = False
        
        # Catégories de sons pour un contrôle granulaire
        self.sound_categories = {
            'ui': ['ClickSound'],
            'gameplay': ['CarCrashSound', 'Impact_Laser', 'ExplosionSound', 'DogBarkSound', 'DogSound', 'FootstepSound'],
            'ambient': ['ALIEN_Ambiance', 'AntSound', 'AtomSound'],
            'feedback': ['ExplosionSound']
        }
        
        self._load_sounds()
    
    def _load_sounds(self):
        """Charge tous les fichiers audio du dossier sounds."""
        if not self.sounds_directory.exists():
            logger.warning(f"Le dossier {self.sounds_directory} n'existe pas. Création du dossier...")
            self.sounds_directory.mkdir(parents=True, exist_ok=True)
            self._create_sample_sounds()
            return
        
        # Extensions audio supportées
        audio_extensions = ['.mp3', '.wav', '.ogg']
        
        for audio_file in self.sounds_directory.iterdir():
            if audio_file.suffix.lower() in audio_extensions:
                try:
                    sound_name = audio_file.stem  # nom sans extension
                    sound = arcade.Sound(str(audio_file))
                    self.sounds[sound_name] = sound
                    logger.info(f"Son chargé: {sound_name}")
                except Exception as e:
                    logger.error(f"Erreur lors du chargement de {audio_file}: {e}")
    
    def _create_sample_sounds(self):
        """Crée des fichiers d'exemple pour les développeurs."""
        sample_sounds_info = """
# Ajoutez vos fichiers audio dans ce dossier
# Formats supportés: .mp3, .wav, .ogg

Exemples de noms recommandés:
- menu_select.wav
- menu_confirm.wav
- menu_back.wav
- button_click.wav
- jump.wav
- collect.wav
- hit.wav
- explosion.wav
- shoot.wav
- background_music.mp3
- level_complete.wav
- success.wav
- failure.wav
"""
        with open(self.sounds_directory / "README.txt", "w", encoding="utf-8") as f:
            f.write(sample_sounds_info)
    
    def play_sound(self, sound_name: str, volume: Optional[float] = None) -> bool:
        """
        Joue un effet sonore.
        
        Args:
            sound_name: Nom du fichier audio (sans extension)
            volume: Volume spécifique pour ce son (0.0 à 1.0)
        
        Returns:
            bool: True si le son a été joué, False sinon
        """
        if self.muted:
            return False
            
        if sound_name not in self.sounds:
            logger.warning(f"Son non trouvé: {sound_name}")
            return False
        
        try:
            effective_volume = self._calculate_volume(sound_name, volume)
            arcade.play_sound(self.sounds[sound_name], volume=effective_volume)
            logger.debug(f"Son joué: {sound_name} (volume: {effective_volume:.2f})")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la lecture de {sound_name}: {e}")
            return False
    
    def _calculate_volume(self, sound_name: str, custom_volume: Optional[float] = None) -> float:
        """Calcule le volume effectif en tenant compte des catégories et paramètres."""
        base_volume = custom_volume if custom_volume is not None else self.sfx_volume
        
        # Ajustement par catégorie
        category_multiplier = 1.0
        for category, sounds in self.sound_categories.items():
            if sound_name in sounds:
                if category == 'ambient':
                    category_multiplier = self.music_volume / self.sfx_volume
                elif category == 'ui':
                    category_multiplier = 0.8  # Sons UI un peu plus faibles
                break
        
        return min(1.0, base_volume * category_multiplier * self.master_volume)
    
    def play_ui_sound(self, action: str) -> bool:
        """
        Joue un son d'interface utilisateur.
        
        Args:
            action: Type d'action ('select', 'confirm', 'back', 'click')
        """
        sound_map = {
            'select': 'ClickSound',
            'confirm': 'ClickSound',
            'back': 'ClickSound',
            'click': 'ClickSound'
        }
        
        sound_name = sound_map.get(action, 'ClickSound')
        return self.play_sound(sound_name)
    
    def play_gameplay_sound(self, action: str, volume: Optional[float] = None) -> bool:
        """
        Joue un son de gameplay.
        
        Args:
            action: Type d'action ('jump', 'collect', 'hit', 'explosion', 'shoot')
            volume: Volume spécifique
        """
        return self.play_sound(action, volume)
    
    def play_dog_sound(self, action: str = "bark", volume: Optional[float] = None) -> bool:
        """
        Joue un son de chien.
        
        Args:
            action: 'bark' pour aboiement, 'general' pour son général
            volume: Volume spécifique
        """
        sound_map = {
            'bark': 'DogBarkSound',
            'general': 'DogSound'
        }
        sound_name = sound_map.get(action, 'DogSound')
        return self.play_sound(sound_name, volume)
    
    def play_car_crash(self, volume: Optional[float] = None) -> bool:
        """Joue le son de crash de voiture."""
        return self.play_sound('CarCrashSound', volume)
    
    def play_explosion(self, volume: Optional[float] = None) -> bool:
        """Joue le son d'explosion."""
        return self.play_sound('ExplosionSound', volume)
    
    def play_laser_impact(self, volume: Optional[float] = None) -> bool:
        """Joue le son d'impact laser."""
        return self.play_sound('Impact_Laser', volume)
    
    def play_footstep(self, volume: Optional[float] = None) -> bool:
        """Joue le son de pas."""
        return self.play_sound('FootstepSound', volume)
    
    def play_ambient_sound(self, scene: str, volume: Optional[float] = None) -> bool:
        """
        Joue un son d'ambiance selon la scène.
        
        Args:
            scene: 'alien', 'ant', 'atom'
            volume: Volume spécifique
        """
        sound_map = {
            'alien': 'ALIEN_Ambiance',
            'ant': 'AntSound',
            'atom': 'AtomSound'
        }
        sound_name = sound_map.get(scene, 'ALIEN_Ambiance')
        return self.play_sound(sound_name, volume)
    
    def set_master_volume(self, volume: float):
        """Définit le volume principal (0.0 à 1.0)."""
        self.master_volume = max(0.0, min(1.0, volume))
        logger.info(f"Volume principal: {self.master_volume:.2f}")
    
    def set_sfx_volume(self, volume: float):
        """Définit le volume des effets sonores (0.0 à 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, volume))
        logger.info(f"Volume SFX: {self.sfx_volume:.2f}")
    
    def set_music_volume(self, volume: float):
        """Définit le volume de la musique (0.0 à 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        logger.info(f"Volume musique: {self.music_volume:.2f}")
    
    def toggle_mute(self) -> bool:
        """Active/désactive le son. Retourne l'état actuel."""
        self.muted = not self.muted
        logger.info(f"Sons {'désactivés' if self.muted else 'activés'}")
        return self.muted
    
    def is_muted(self) -> bool:
        """Retourne True si les sons sont désactivés."""
        return self.muted
    
    def get_available_sounds(self) -> list:
        """Retourne la liste des sons disponibles."""
        return list(self.sounds.keys())
    
    def reload_sounds(self):
        """Recharge tous les sons depuis le dossier."""
        self.sounds.clear()
        self._load_sounds()
        logger.info("Sons rechargés")


# Instance globale du gestionnaire de sons
_sound_manager = None


def get_sound_manager() -> SoundManager:
    """Retourne l'instance globale du gestionnaire de sons."""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager


def play_sound(sound_name: str, volume: Optional[float] = None) -> bool:
    """Fonction utilitaire pour jouer un son rapidement."""
    return get_sound_manager().play_sound(sound_name, volume)


def play_ui_sound(action: str) -> bool:
    """Fonction utilitaire pour jouer un son d'UI."""
    return get_sound_manager().play_ui_sound(action)


def play_gameplay_sound(action: str, volume: Optional[float] = None) -> bool:
    """Fonction utilitaire pour jouer un son de gameplay."""
    return get_sound_manager().play_gameplay_sound(action, volume)


def play_dog_sound(action: str = "bark", volume: Optional[float] = None) -> bool:
    """Fonction utilitaire pour jouer un son de chien."""
    return get_sound_manager().play_dog_sound(action, volume)


def play_car_crash(volume: Optional[float] = None) -> bool:
    """Fonction utilitaire pour jouer le son de crash de voiture."""
    return get_sound_manager().play_car_crash(volume)


def play_explosion(volume: Optional[float] = None) -> bool:
    """Fonction utilitaire pour jouer le son d'explosion."""
    return get_sound_manager().play_explosion(volume)


def play_laser_impact(volume: Optional[float] = None) -> bool:
    """Fonction utilitaire pour jouer le son d'impact laser."""
    return get_sound_manager().play_laser_impact(volume)


def play_footstep(volume: Optional[float] = None) -> bool:
    """Fonction utilitaire pour jouer le son de pas."""
    return get_sound_manager().play_footstep(volume)


def play_ambient_sound(scene: str, volume: Optional[float] = None) -> bool:
    """Fonction utilitaire pour jouer un son d'ambiance."""
    return get_sound_manager().play_ambient_sound(scene, volume)
