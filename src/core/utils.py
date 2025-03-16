"""
Utility functions used throughout the game.
"""

import math
import pygame
import time
from ..core.constants import TILE_WIDTH, TILE_HEIGHT, TILE_Z_HEIGHT

class Vector2:
    """2D vector class for positions and directions."""

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide vector by zero")
        return Vector2(self.x / scalar, self.y / scalar)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f"Vector2({self.x}, {self.y})"

    def length(self):
        """Get the length (magnitude) of the vector."""
        return math.sqrt(self.x * self.x + self.y * self.y)

    def length_squared(self):
        """Get the squared length of the vector (faster than length)."""
        return self.x * self.x + self.y * self.y

    def normalize(self):
        """Return a normalized copy of the vector."""
        length = self.length()
        if length == 0:
            return Vector2(0, 0)
        return Vector2(self.x / length, self.y / length)

    def distance_to(self, other):
        """Calculate distance to another vector."""
        return (other - self).length()

    def distance_squared_to(self, other):
        """Calculate squared distance to another vector (faster)."""
        return (other - self).length_squared()

    def dot(self, other):
        """Calculate dot product with another vector."""
        return self.x * other.x + self.y * other.y

    def angle_to(self, other):
        """Calculate angle to another vector in radians."""
        dot = self.normalize().dot(other.normalize())
        # Clamp to avoid floating point errors
        dot = max(-1.0, min(1.0, dot))
        return math.acos(dot)

    def to_tuple(self):
        """Convert to tuple."""
        return (self.x, self.y)

    @staticmethod
    def from_tuple(tuple_value):
        """Create vector from tuple."""
        return Vector2(tuple_value[0], tuple_value[1])


# Isometric conversion functions
def iso_to_screen(iso_x, iso_y, iso_z=0):
    """Convert isometric coordinates to screen coordinates."""
    screen_x = (iso_x - iso_y) * (TILE_WIDTH / 2)
    screen_y = (iso_x + iso_y) * (TILE_HEIGHT / 4) - iso_z * (TILE_HEIGHT / 2)
    return screen_x, screen_y

def screen_to_iso(screen_x, screen_y, iso_z=0):
    """Convert screen coordinates to isometric coordinates (z=0 plane)."""
    # Adjust for z height
    screen_y += iso_z * (TILE_HEIGHT / 2)

    iso_x = (screen_x / (TILE_WIDTH / 2) + screen_y / (TILE_HEIGHT / 4)) / 2
    iso_y = (screen_y / (TILE_HEIGHT / 4) - screen_x / (TILE_WIDTH / 2)) / 2
    return iso_x, iso_y

def tile_to_iso(tile_x, tile_y):
    """Convert tile coordinates to isometric coordinates."""
    return tile_x, tile_y

def iso_to_tile(iso_x, iso_y):
    """Convert isometric coordinates to tile coordinates."""
    return int(iso_x), int(iso_y)

def iso_distance(x1, y1, x2, y2):
    """Calculate distance in isometric space."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def get_depth(iso_x, iso_y, iso_z=0):
    """Calculate depth sorting value for rendering order."""
    return iso_y + iso_x / 1000.0 + iso_z / 1000000.0


# Timer utility
class Timer:
    """Simple timer for tracking elapsed time."""

    def __init__(self):
        self.start_time = time.time()
        self.paused_time = 0
        self.is_paused = False
        self.pause_start = 0

    def reset(self):
        """Reset the timer."""
        self.start_time = time.time()
        self.paused_time = 0
        self.is_paused = False

    def pause(self):
        """Pause the timer."""
        if not self.is_paused:
            self.is_paused = True
            self.pause_start = time.time()

    def resume(self):
        """Resume the timer."""
        if self.is_paused:
            self.is_paused = False
            self.paused_time += time.time() - self.pause_start

    def get_elapsed(self):
        """Get elapsed time in seconds."""
        if self.is_paused:
            return self.pause_start - self.start_time - self.paused_time
        return time.time() - self.start_time - self.paused_time


# Text rendering utilities
def render_text(text, font, color, max_width=None, antialias=True):
    """Render text, optionally wrapping to max_width."""
    if not max_width:
        return font.render(text, antialias, color)

    words = text.split(' ')
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        test_width, _ = font.size(test_line)

        if test_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                # Word is too long for the line, split it
                current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    # Render each line
    line_surfaces = [font.render(line, antialias, color) for line in lines]

    # Calculate total height
    line_height = font.get_linesize()
    total_height = line_height * len(line_surfaces)
    max_line_width = max(surface.get_width() for surface in line_surfaces)

    # Create surface for all lines
    text_surface = pygame.Surface((max_line_width, total_height), pygame.SRCALPHA)

    # Blit each line onto the surface
    for i, line_surface in enumerate(line_surfaces):
        text_surface.blit(line_surface, (0, i * line_height))

    return text_surface


# Debug utilities
def debug_print(message, category="DEBUG"):
    """Print debug message with timestamp."""
    timestamp = time.strftime("%H:%M:%S", time.localtime())
    print(f"[{timestamp}] [{category}] {message}")


# File utilities
def ensure_dir_exists(directory):
    """Ensure a directory exists, creating it if necessary."""
    import os
    if not os.path.exists(directory):
        os.makedirs(directory)
        return True
    return False