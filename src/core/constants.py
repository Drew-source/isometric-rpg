"""
Game constants that don't change during gameplay.
"""

# Display settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TARGET_FPS = 60
WINDOW_TITLE = "Baldur's Gate-Style RPG"

# Isometric tile settings
TILE_WIDTH = 64
TILE_HEIGHT = 32
TILE_Z_HEIGHT = 16  # Height of a single Z-level in pixels

# Colors
BACKGROUND_COLOR = (0, 0, 0)
UI_BACKGROUND_COLOR = (20, 20, 40, 200)
UI_TEXT_COLOR = (220, 220, 220)
UI_HIGHLIGHT_COLOR = (255, 255, 100)
UI_BORDER_COLOR = (100, 100, 140)

# Gameplay constants
MOVEMENT_SPEED = 3.0  # Base movement speed (tiles per second)
COMBAT_RANGE = 1.5    # Default melee combat range (in tiles)
ITEM_PICKUP_RANGE = 1.0  # Range at which items can be picked up
INTERACTION_RANGE = 2.0  # Range for NPC interactions

# Path to asset directories
ASSET_DIR = "assets"
IMAGE_DIR = f"{ASSET_DIR}/images"
DATA_DIR = f"{ASSET_DIR}/data"
AUDIO_DIR = f"{ASSET_DIR}/audio"
FONT_DIR = f"{ASSET_DIR}/fonts"

# Save system
SAVE_DIR = "saves"
<<<<<<< HEAD
AUTO_SAVE_INTERVAL = 300  # Seconds between auto-saves
=======
AUTO_SAVE_INTERVAL = 300  # Seconds between auto-saves 
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
