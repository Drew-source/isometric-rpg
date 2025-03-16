"""
Component base class for the Entity Component System.
"""

class Component:
    """
    Base class for all components in the ECS.

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

        Returns:
            dict: Serialized component data
        """
        # Base implementation returns an empty dict
        # Subclasses should override this to include their data
        return {}

    @classmethod
    def deserialize(cls, data):
        """
        Create a component from serialized data.

        Args:
            data (dict): Serialized component data

        Returns:
            Component: New component instance
        """
        # Base implementation creates an empty component
        # Subclasses should override this to restore their data
        return cls()

    def clone(self):
        """
        Create a copy of this component.

        Returns:
            Component: New component instance with the same data
        """
        # Default implementation uses serialization
        return self.__class__.deserialize(self.serialize())