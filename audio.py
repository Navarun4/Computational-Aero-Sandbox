import pygame
import os

def load_game_sounds(sound_dir):
    """Loads and returns all game sound effects with safe error handling."""
    try:
        # Handles the double extension added by Windows file-hiding settings
        launch = pygame.mixer.Sound(os.path.join(sound_dir, "launch.wav.wav"))
        explosion = pygame.mixer.Sound(os.path.join(sound_dir, "explosion.wav.wav"))
        
        # Balance the volume levels
        launch.set_volume(0.5)
        explosion.set_volume(0.7)
        
        print("🔊 SUCCESS: Audio engine loaded completely! Sounds are ready.")
        return launch, explosion
        
    except FileNotFoundError as e:
        print(f"❌ AUDIO ERROR: Could not find sound files. Details: {e}")
        return None, None