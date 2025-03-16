"""
Component class for the Entity Component System (ECS).

This module defines the base Component class that all components will inherit from,
providing common serialization and comparison methods.
"""

class Component:
    """
    Base class for all components in the ECS architecture.
    
    Components are pure data containers with no behavior,
    following the principles of ECS architecture.
    """
    
    def __init__(self):
        """Initialize the component."""
        self.owner_id = None  # Will be set when added to an entity
    
    def serialize(self):
        """
        Serialize the component to a dictionary.
        
        This method should be implemented by child classes to enable
        saving and loading component data.
        
        Returns:
            dict: Dictionary representation of the component.
        """
        # Child classes should override this to provide proper serialization
        return {}
    
    @classmethod
    def deserialize(cls, data):
        """
        Deserialize from a dictionary to create a component.
        
        This is a class method that should be implemented by child classes
        to create a component instance from serialized data.
        
        Args:
            data (dict): Dictionary containing component data.
            
        Returns:
            Component: New component instance.
        """
        # Child classes should override this to provide proper deserialization
        return cls()
    
    def copy(self):
        """
        Create a copy of this component.
        
        This method should be implemented by child classes to enable
        deep copying of components.
        
        Returns:
            Component: A new instance of the component with the same data.
        """
        # Child classes should override this with proper deep copying
        return self.__class__()