"""
Entity Component System module.

This module provides the core ECS architecture for the game.
"""

from .component import Component
from .entity import Entity
from .system import System
from .world import World

__all__ = ['Component', 'Entity', 'System', 'World']