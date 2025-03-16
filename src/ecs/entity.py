"""
Entity class for the Entity Component System (ECS) architecture.

This module defines the Entity class that serves as a container for components,
implementing an entity-component system pattern.
"""

import uuid
from typing import Dict, Type, TypeVar, Optional, List, Set

from .component import Component

# TypeVar for better type hints with components
T = TypeVar('T', bound=Component)

class Entity:
    """
    Entity class that serves as a container for components.
    
    In the ECS architecture, entities are essentially just IDs that
    group related components together. They have no behavior themselves.
    """
    
    def __init__(self, entity_id=None):
        """
        Initialize a new entity with an optional ID.
        
        Args:
            entity_id (str, optional): The entity ID. If not provided, a new UUID will be generated.
        """
        self.id = entity_id if entity_id else str(uuid.uuid4())
        self.components = {}  # Dict[Type[Component], Component]
        self.tags = set()  # Set[str]
        self.active = True
        
    def add_component(self, component):
        """
        Add a component to this entity.
        
        Args:
            component (Component): The component to add.
            
        Returns:
            Entity: Self for method chaining.
        """
        component_type = type(component)
        self.components[component_type] = component
        component.owner_id = self.id
        return self
        
    def remove_component(self, component_type):
        """
        Remove a component by type from this entity.
        
        Args:
            component_type (Type[Component]): The type of component to remove.
            
        Returns:
            Component or None: The removed component, or None if not found.
        """
        if component_type in self.components:
            component = self.components[component_type]
            component.owner_id = None
            del self.components[component_type]
            return component
        return None
    
    def get_component(self, component_type: Type[T]) -> Optional[T]:
        """
        Get a component by type.
        
        Args:
            component_type (Type[Component]): The type of component to get.
            
        Returns:
            Component or None: The component if found, otherwise None.
        """
        return self.components.get(component_type)
    
    def has_component(self, component_type: Type[Component]) -> bool:
        """
        Check if the entity has a component of the specified type.
        
        Args:
            component_type (Type[Component]): The type of component to check for.
            
        Returns:
            bool: True if the entity has the component, False otherwise.
        """
        return component_type in self.components
    
    def has_components(self, component_types: List[Type[Component]]) -> bool:
        """
        Check if the entity has all of the specified component types.
        
        Args:
            component_types (List[Type[Component]]): The types of components to check for.
            
        Returns:
            bool: True if the entity has all components, False otherwise.
        """
        return all(component_type in self.components for component_type in component_types)
    
    def add_tag(self, tag: str):
        """
        Add a tag to this entity.
        
        Tags can be used to quickly identify and group entities by purpose.
        
        Args:
            tag (str): The tag to add.
            
        Returns:
            Entity: Self for method chaining.
        """
        self.tags.add(tag)
        return self
    
    def remove_tag(self, tag: str):
        """
        Remove a tag from this entity.
        
        Args:
            tag (str): The tag to remove.
            
        Returns:
            Entity: Self for method chaining.
        """
        self.tags.discard(tag)
        return self
    
    def has_tag(self, tag: str) -> bool:
        """
        Check if the entity has the specified tag.
        
        Args:
            tag (str): The tag to check for.
            
        Returns:
            bool: True if the entity has the tag, False otherwise.
        """
        return tag in self.tags
    
    def serialize(self):
        """
        Serialize the entity to a dictionary.
        
        Returns:
            dict: A dictionary representation of the entity.
        """
        serialized_components = {}
        for component_type, component in self.components.items():
            serialized_components[component_type.__name__] = {
                "type": component_type.__name__,
                "data": component.serialize()
            }
        
        return {
            "id": self.id,
            "tags": list(self.tags),
            "active": self.active,
            "components": serialized_components
        }
    
    @classmethod
    def deserialize(cls, data, component_registry):
        """
        Create an entity from serialized data.
        
        Args:
            data (dict): The serialized entity data.
            component_registry (dict): A mapping of component names to types.
            
        Returns:
            Entity: A new entity with the deserialized components.
        """
        entity = cls(entity_id=data.get("id"))
        entity.active = data.get("active", True)
        
        # Add tags
        for tag in data.get("tags", []):
            entity.add_tag(tag)
        
        # Add components
        for _, component_data in data.get("components", {}).items():
            component_type_name = component_data.get("type")
            component_type = component_registry.get(component_type_name)
            
            if component_type:
                component = component_type.deserialize(component_data.get("data", {}))
                entity.add_component(component)
        
        return entity