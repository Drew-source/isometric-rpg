"""
User-configurable game settings.
"""

import os
import json
import pygame
import numpy as np
from pathlib import Path

class Settings:
    """Manages user-configurable game settings."""

    def __init__(self, settings_file="settings.json"):
        self.settings_file = settings_file

        # Default settings
        self.settings = {
            "fullscreen": False,
            "resolution": (1280, 720),
            "sound_volume": 0.7,
            "music_volume": 0.5,
            "vsync": True,
            "show_fps": False,
            "auto_pause_triggers": {
                "enemy_spotted": True,
                "character_damaged": True,
                "spell_cast": False,
                "trap_detected": True
            },
            "key_bindings": {
                "move": pygame.K_m,
                "attack": pygame.K_a,
                "inventory": pygame.K_i,
                "character": pygame.K_c,
                "pause": pygame.K_SPACE,
                "select_all": pygame.K_F1,
                "quick_save": pygame.K_F5,
                "quick_load": pygame.K_F9
            },
            "accessibility": {
                "text_size": "medium",
                "high_contrast": False,
                "color_blind_mode": "none"
            }
        }

        # Color blindness filter matrices
        self.color_filters = {
            "none": None,
            "protanopia": [
                [0.567, 0.433, 0.0],
                [0.558, 0.442, 0.0],
                [0.0, 0.242, 0.758]
            ],
            "deuteranopia": [
                [0.625, 0.375, 0.0],
                [0.7, 0.3, 0.0],
                [0.0, 0.3, 0.7]
            ],
            "tritanopia": [
                [0.95, 0.05, 0.0],
                [0.0, 0.433, 0.567],
                [0.0, 0.475, 0.525]
            ]
        }

        # Load settings from file if it exists
        self.load_settings()

    def load_settings(self):
        """Load settings from file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)

                # Update settings with loaded values
                for key, value in loaded_settings.items():
                    if key in self.settings:
                        if isinstance(self.settings[key], dict) and isinstance(value, dict):       
                            # Merge nested dictionaries
                            self.settings[key].update(value)
                        else:
                            self.settings[key] = value

                print(f"Settings loaded from {self.settings_file}")
        except Exception as e:
            print(f"Error loading settings: {e}")

    def save_settings(self):
        """Save settings to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)

            print(f"Settings saved to {self.settings_file}")
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get_resolution(self):
        """Get the current resolution."""
        return self.settings["resolution"]

    def set_resolution(self, width, height):
        """Set the resolution."""
        self.settings["resolution"] = (width, height)
        self.save_settings()

    def is_fullscreen(self):
        """Check if fullscreen is enabled."""
        return self.settings["fullscreen"]

    def set_fullscreen(self, fullscreen):
        """Set fullscreen mode."""
        self.settings["fullscreen"] = fullscreen
        self.save_settings()

    def get_sound_volume(self):
        """Get sound effects volume."""
        return self.settings["sound_volume"]

    def set_sound_volume(self, volume):
        """Set sound effects volume."""
        self.settings["sound_volume"] = max(0.0, min(1.0, volume))
        self.save_settings()

    def get_music_volume(self):
        """Get music volume."""
        return self.settings["music_volume"]

    def set_music_volume(self, volume):
        """Set music volume."""
        self.settings["music_volume"] = max(0.0, min(1.0, volume))
        self.save_settings()

    def get_key_binding(self, action):
        """Get key binding for an action."""
        return self.settings["key_bindings"].get(action)

    def set_key_binding(self, action, key):
        """Set key binding for an action."""
        if action in self.settings["key_bindings"]:
            self.settings["key_bindings"][action] = key
            self.save_settings()

    def get_text_size(self):
        """Get text size setting."""
        return self.settings["accessibility"]["text_size"]

    def set_text_size(self, size):
        """Set text size."""
        if size in ["small", "medium", "large"]:
            self.settings["accessibility"]["text_size"] = size
            self.save_settings()

    def get_high_contrast(self):
        """Check if high contrast is enabled."""
        return self.settings["accessibility"]["high_contrast"]

    def set_high_contrast(self, enabled):
        """Set high contrast mode."""
        self.settings["accessibility"]["high_contrast"] = enabled
        self.save_settings()

    def get_color_filter(self):
        """Get the current color blindness filter matrix."""
        mode = self.settings["accessibility"]["color_blind_mode"]
        return self.color_filters[mode]

    def set_color_blind_mode(self, mode):
        """Set color blindness mode."""
        if mode in self.color_filters:
            self.settings["accessibility"]["color_blind_mode"] = mode
            self.save_settings()

    def apply_color_filter(self, surface):
        """Apply color blindness filter to a surface."""
        filter_matrix = self.get_color_filter()
        if not filter_matrix:
            return surface  # No filter to apply

        # Create a copy of the surface to modify
        filtered = surface.copy()

        # Get pixel array
        pixels = pygame.surfarray.pixels3d(filtered)

        # Apply filter matrix to RGB values
        r = pixels[:,:,0] * filter_matrix[0][0] + pixels[:,:,1] * filter_matrix[0][1] + pixels[:,:,2] * filter_matrix[0][2]
        g = pixels[:,:,0] * filter_matrix[1][0] + pixels[:,:,1] * filter_matrix[1][1] + pixels[:,:,2] * filter_matrix[1][2]
        b = pixels[:,:,0] * filter_matrix[2][0] + pixels[:,:,1] * filter_matrix[2][1] + pixels[:,:,2] * filter_matrix[2][2]

        # Clip values to valid range
        r = np.clip(r, 0, 255)
        g = np.clip(g, 0, 255)
        b = np.clip(b, 0, 255)

        # Update pixel array
        pixels[:,:,0] = r
        pixels[:,:,1] = g
        pixels[:,:,2] = b

        # Release the pixel array
        del pixels

        return filtered

    def should_auto_pause(self, trigger):
        """Check if a specific trigger should cause auto-pause."""
        return self.settings["auto_pause_triggers"].get(trigger, False)