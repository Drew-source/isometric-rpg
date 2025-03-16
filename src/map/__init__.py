"""
Map package for the isometric RPG.

This package provides map representation, loading, serialization, and system integration
for the game world.
"""

from .map import Map, Tile, TileType, CollisionType
from .system import MapSystem 