"""
System base class for the Entity Component System.
"""

class System:
    """
    Base class for all systems in the ECS.

    Systems contain the logic to process entities with specific components.
    They are responsible for implementing game behavior and mechanics.
    """

    def __init__(self, world):
        """
        Initialize the system.

        Args:
            world: The world this system belongs to
        """
        self.world = world
        self.required_components = set()  # Component types required for processing
        self.enabled = True  # Whether the system is enabled
        self.priority = 0  # Execution priority (higher = earlier)

    def initialize(self):
        """
        Initialize the system. Called when the system is added to the world.

        Override this method to perform setup tasks.
        """
        pass

    def shutdown(self):
        """
        Shutdown the system. Called when the system is removed from the world.

        Override this method to perform cleanup tasks.
        """
        pass

    def update(self, dt):
        """
        Update the system.

        Args:
            dt: Delta time in seconds
        """
        if not self.enabled:
            return

        # Get entities that match the required components
        entities = self.get_entities()

        # Process the entities
        self.process(entities, dt)

    def process(self, entities, dt):
        """
        Process the entities.

        Args:
            entities: List of entities to process
            dt: Delta time in seconds
        """
        # Base implementation does nothing
        # Subclasses should override this to implement their logic
        pass

    def get_entities(self):
        """
        Get entities that match the required components.

        Returns:
            list: List of matching entities
        """
        if not self.required_components:
            return []

        return self.world.get_entities_with_components(self.required_components)

    def enable(self):
        """Enable the system."""
        self.enabled = True

    def disable(self):
        """Disable the system."""
        self.enabled = False

    def set_priority(self, priority):
        """
        Set the execution priority of the system.

        Args:
            priority: Priority value (higher = earlier execution)
        """
        self.priority = priority

        # Notify world to resort systems
        if self.world:
            self.world.sort_systems()