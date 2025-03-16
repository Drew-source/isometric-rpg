"""
Spatial system for the Entity Component System.

This system manages the spatial grid and provides spatial query functionality
to other systems in the game.
"""

from ..ecs.system import System
from ..components.transform import TransformComponent
from ..events.event_types import EventType
from .grid import SpatialGrid


class SpatialSystem(System):
    """
    System that manages the spatial grid and provides spatial queries.
    
    This system keeps the spatial grid in sync with entity positions and
    provides methods for other systems to query for entities based on
    spatial relationships.
    """
    
    def __init__(self, world, event_manager, cell_size=4.0):
        """
        Initialize the spatial system.
        
        Args:
            world: The world this system belongs to
            event_manager: The event manager for emitting and subscribing to events
            cell_size: Size of each cell in the spatial grid (default: 4.0)
        """
        super().__init__(world)
        self.event_manager = event_manager
        self.required_components = [TransformComponent]
        
        # Create spatial grid
        self.grid = SpatialGrid(cell_size)
        
        # Track which entities are already in the grid
        self.tracked_entities = set()
        
        # Subscribe to events
        self._subscribe_to_events()
    
    def _subscribe_to_events(self):
        """Subscribe to relevant events."""
        self.event_manager.subscribe(EventType.ENTITY_CREATED, self._on_entity_created)
        self.event_manager.subscribe(EventType.ENTITY_DESTROYED, self._on_entity_destroyed)
        self.event_manager.subscribe(EventType.COMPONENT_ADDED, self._on_component_added)
        self.event_manager.subscribe(EventType.COMPONENT_REMOVED, self._on_component_removed)
        self.event_manager.subscribe(EventType.ENTITY_MOVED, self._on_entity_moved)
        self.event_manager.subscribe(EventType.WORLD_CLEARING, self._on_world_clearing)
    
    def _on_entity_created(self, event_data):
        """
        Handle entity created event.
        
        Args:
            event_data: Event data containing the entity that was created
        """
        entity = event_data.get("entity")
        if not entity:
            return
        
        # Check if entity has a transform component
        transform = self.world.get_component(entity.id, TransformComponent)
        if transform:
            self._add_entity_to_grid(entity.id, transform)
    
    def _on_entity_destroyed(self, event_data):
        """
        Handle entity destroyed event.
        
        Args:
            event_data: Event data containing the entity that was destroyed
        """
        entity_id = event_data.get("entity_id")
        if entity_id in self.tracked_entities:
            self.grid.remove_entity(entity_id)
            self.tracked_entities.remove(entity_id)
    
    def _on_component_added(self, event_data):
        """
        Handle component added event.
        
        Args:
            event_data: Event data containing the entity and component type
        """
        entity_id = event_data.get("entity_id")
        component_type = event_data.get("component_type")
        
        if component_type == TransformComponent.__name__:
            transform = self.world.get_component(entity_id, TransformComponent)
            if transform:
                self._add_entity_to_grid(entity_id, transform)
    
    def _on_component_removed(self, event_data):
        """
        Handle component removed event.
        
        Args:
            event_data: Event data containing the entity and component type
        """
        entity_id = event_data.get("entity_id")
        component_type = event_data.get("component_type")
        
        if component_type == TransformComponent.__name__ and entity_id in self.tracked_entities:
            self.grid.remove_entity(entity_id)
            self.tracked_entities.remove(entity_id)
    
    def _on_entity_moved(self, event_data):
        """
        Handle entity moved event.
        
        Args:
            event_data: Event data containing the entity that moved
        """
        entity = event_data.get("entity")
        if not entity or entity.id not in self.tracked_entities:
            return
        
        # Update entity position in the grid
        transform = self.world.get_component(entity.id, TransformComponent)
        if transform:
            self.grid.move_entity(entity.id, transform.position.x, transform.position.y)
    
    def _on_world_clearing(self, event_data):
        """
        Handle world clearing event.
        
        Args:
            event_data: Event data (unused)
        """
        self.grid.clear()
        self.tracked_entities.clear()
    
    def _add_entity_to_grid(self, entity_id, transform):
        """
        Add an entity to the spatial grid.
        
        Args:
            entity_id: ID of the entity to add
            transform: Transform component of the entity
        """
        if entity_id not in self.tracked_entities:
            self.grid.add_entity(entity_id, transform.position.x, transform.position.y)
            self.tracked_entities.add(entity_id)
    
    def update(self, dt):
        """
        Update the spatial system.
        
        In a real implementation, we would update the grid in response to
        specific events. For this example, we're doing a full synchronization
        each frame to ensure the grid is always up to date.
        
        Args:
            dt: Delta time in seconds
        """
        # Get all entities with transform components
        entities = self.world.get_entities_with_components([TransformComponent])
        
        # Update tracked entities
        for entity_id in entities:
            if entity_id not in self.tracked_entities:
                transform = self.world.get_component(entity_id, TransformComponent)
                self._add_entity_to_grid(entity_id, transform)
        
        # Ensure all tracked entities still exist and have transform components
        for entity_id in list(self.tracked_entities):
            transform = self.world.get_component(entity_id, TransformComponent)
            if not transform:
                self.grid.remove_entity(entity_id)
                self.tracked_entities.remove(entity_id)
    
    def get_entities_in_range(self, x, y, radius):
        """
        Get all entities within a certain radius of a position.
        
        Args:
            x: X coordinate in world space
            y: Y coordinate in world space
            radius: Radius to search within
            
        Returns:
            set: Set of entity IDs within range
        """
        return self.grid.get_entities_in_range(x, y, radius)
    
    def get_entities_in_rect(self, min_x, min_y, max_x, max_y):
        """
        Get all entities within a rectangular area.
        
        Args:
            min_x: Minimum X coordinate
            min_y: Minimum Y coordinate
            max_x: Maximum X coordinate
            max_y: Maximum Y coordinate
            
        Returns:
            set: Set of entity IDs within the rectangle
        """
        return self.grid.get_entities_in_rect(min_x, min_y, max_x, max_y)
    
    def get_nearest_entity(self, x, y, max_radius=float('inf'), filter_func=None):
        """
        Get the nearest entity to a position.
        
        Args:
            x: X coordinate in world space
            y: Y coordinate in world space
            max_radius: Maximum radius to search within (default: infinite)
            filter_func: Optional function to filter entities (takes entity_id, returns bool)
            
        Returns:
            tuple: (entity_id, distance) or (None, float('inf')) if no entity found
        """
        return self.grid.get_nearest_entity(x, y, max_radius, filter_func)
    
    def get_entities_along_ray(self, start_x, start_y, end_x, end_y, max_distance=float('inf')):
        """
        Get all entities along a ray from start to end point, ordered by distance.
        
        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            max_distance: Maximum distance to check along the ray
            
        Returns:
            list: List of (entity_id, distance) tuples, sorted by distance
        """
        return self.grid.get_entities_along_ray(start_x, start_y, end_x, end_y, max_distance)
    
    def get_entity_position(self, entity_id):
        """
        Get the position of an entity in the grid.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            tuple: (x, y) position, or None if entity not in grid
        """
        return self.grid.entity_positions.get(entity_id)
    
    def get_stats(self):
        """
        Get statistics about the spatial grid.
        
        Returns:
            dict: Statistics about the grid
        """
        return self.grid.get_stats() 