"""
Component base class for the Entity Component System.
"""

class Component:
    """
    Base class for all components in the ECS.
<<<<<<< HEAD

    Components are pure data containers with no behavior.
    They store the state for entities and are processed by systems.
    """

    def __init__(self):
        """Initialize the component."""
        self.entity = None  # Reference to the owning entity

    def on_attach(self, entity):
        """Called when the component is attached to an entity."""
        self.entity = entity

    def on_detach(self):
        """Called when the component is detached from an entity."""
        self.entity = None

    def serialize(self):
        """
        Convert component data to a serializable format.

=======
    
    Components are pure data containers with no behavior.
    They store the state for entities and are processed by systems.
    """
    
    def __init__(self):
        """Initialize the component."""
        self.entity = None  # Reference to the owning entity
    
    def on_attach(self, entity):
        """Called when the component is attached to an entity."""
        self.entity = entity
    
    def on_detach(self):
        """Called when the component is detached from an entity."""
        self.entity = None
    
    def serialize(self):
        """
        Convert component data to a serializable format.
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Returns:
            dict: Serialized component data
        """
        # Base implementation returns an empty dict
        # Subclasses should override this to include their data
        return {}
<<<<<<< HEAD

=======
    
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
    @classmethod
    def deserialize(cls, data):
        """
        Create a component from serialized data.
<<<<<<< HEAD

        Args:
            data (dict): Serialized component data

=======
        
        Args:
            data (dict): Serialized component data
            
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Returns:
            Component: New component instance
        """
        # Base implementation creates an empty component
        # Subclasses should override this to restore their data
        return cls()
<<<<<<< HEAD

    def clone(self):
        """
        Create a copy of this component.

=======
    
    def clone(self):
        """
        Create a copy of this component.
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Returns:
            Component: New component instance with the same data
        """
        # Default implementation uses serialization
<<<<<<< HEAD
        return self.__class__.deserialize(self.serialize())
=======
        return self.__class__.deserialize(self.serialize()) 
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
