"""
System class for the Entity Component System (ECS) architecture.

This module defines the base System class that all systems will inherit from,
providing common update methods and component requirements.
"""

from typing import List, Type, Set

from .component import Component

class System:
    """
    Base class for all systems in the ECS architecture.
    
    Systems contain the game logic that operates on entities with specific components.
    """
    
    def __init__(self, world=None):
        """
        Initialize the system with an optional world reference.
        
        Args:
            world: Reference to the world containing entities.
        """
        self.world = world
        self.required_components = []  # List[Type[Component]]
        self.active = True
    
    def set_world(self, world):
        """
        Set the world reference.
        
        Args:
            world: The world containing entities.
        """
        self.world = world
    
    def get_required_components(self) -> List[Type[Component]]:
        """
        Get the list of required component types.
        
        Returns:
            List[Type[Component]]: List of component types required by this system.
        """
        return self.required_components
    
    def process_entity(self, entity_id, dt):
        """
        Process a single entity.
        
        Args:
            entity_id: ID of the entity to process.
            dt (float): Time delta since last update in seconds.
        """
        # To be implemented by subclasses
        pass
    
    def update(self, dt):
        """
        Update all relevant entities.
        
        This method is called each frame with the time delta since the last update.
        It should process all entities with the required components.
        
        Args:
            dt (float): Time delta since last update in seconds.
        """
        if not self.world or not self.active:
            return
            
        # Get entities with required components
        for entity_id in self.world.get_entities_with_components(self.required_components):
            entity = self.world.get_entity(entity_id)
            if entity and entity.active:
                self.process_entity(entity_id, dt)
    
    def on_entity_added(self, entity_id):
        """
        Called when an entity is added to the world.
        
        Args:
            entity_id: ID of the added entity.
        """
        # Optional hook for subclasses
        pass
    
    def on_entity_removed(self, entity_id):
        """
        Called when an entity is removed from the world.
        
        Args:
            entity_id: ID of the removed entity.
        """
        # Optional hook for subclasses
        pass
    
    def on_component_added(self, entity_id, component_type):
        """
        Called when a component is added to an entity.
        
        Args:
            entity_id: ID of the entity.
            component_type (Type[Component]): Type of the added component.
        """
        # Optional hook for subclasses
        pass
    
    def on_component_removed(self, entity_id, component_type):
        """
        Called when a component is removed from an entity.
        
        Args:
            entity_id: ID of the entity.
            component_type (Type[Component]): Type of the removed component.
        """
        # Optional hook for subclasses
        pass