"""
Entity Component System (ECS) package.

This package contains the core classes for the Entity Component System architecture:
- Entity: Container for components
- Component: Data-only classes representing entity properties
- System: Logic that processes entities with specific components
- World: Central registry for entities and systems
"""

from .component import Component
from .entity import Entity
from .system import System
from .world import World