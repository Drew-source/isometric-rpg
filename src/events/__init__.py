"""
Events package for the isometric RPG.

This package contains the event-driven architecture components:
- EventManager: Handles event subscription and emission
- EventType: Constants for all event types
"""

from .event_manager import EventManager
from .event_types import EventType