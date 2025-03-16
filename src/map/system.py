"""
Map system for the Entity Component System.

This system manages maps, handles loading and serialization, and facilitates
interactions between entities and the map.
"""

import os
import math
from ..ecs.system import System
from ..components.transform import TransformComponent
from ..events.event_types import EventType
from .map import Map, TileType, CollisionType, Tile


class MapSystem(System):
    """
    System that manages maps and map-related operations.
    
    This system handles loading maps, spawning entities defined in maps,
    and providing utility functions for map interactions.
    """
    
    def __init__(self, world, event_manager):
        """
        Initialize the map system.
        
        Args:
            world: The world this system belongs to
            event_manager: The event manager for emitting and subscribing to events
        """
        super().__init__(world)
        self.event_manager = event_manager
        self.required_components = []  # Map system doesn't require specific components
        
        # Current active map
        self.current_map = None
        
        # Map cache for faster loading
        self.map_cache = {}
        
        # Entity spawners registered by type
        self.entity_spawners = {}
        
        # Collision handlers by type
        self.collision_handlers = {}
        
        # Directory for map files
        self.maps_directory = "maps"
        
        # Subscribe to events
        self._subscribe_to_events()
    
    def _subscribe_to_events(self):
        """Subscribe to relevant events."""
        self.event_manager.subscribe(EventType.ENTITY_MOVED, self._on_entity_moved)
        self.event_manager.subscribe(EventType.WORLD_CLEARING, self._on_world_clearing)
    
    def _on_entity_moved(self, event_data):
        """
        Handle entity moved event.
        
        Args:
            event_data: Event data containing the entity that moved
        """
        if not self.current_map:
            return
        
        entity = event_data.get("entity")
        if not entity:
            return
        
        # Check for collision with map tiles
        transform = self.world.get_component(entity.id, TransformComponent)
        if not transform:
            return
        
        # Get tile at entity's new position
        x, y = math.floor(transform.position.x), math.floor(transform.position.y)
        tile = self.current_map.get_tile(x, y)
        
        if not tile:
            return
        
        # Handle collision based on tile's collision type
        collision_type = tile.collision_type
        
        if collision_type == CollisionType.NONE:
            # No collision, do nothing
            pass
        elif collision_type == CollisionType.BLOCK:
            # Block movement, move entity back to old position if possible
            old_position = event_data.get("old_position")
            if old_position:
                transform.set_position(old_position[0], old_position[1])
                
                # Emit collision event
                self.event_manager.emit(EventType.COLLISION_OCCURRED, {
                    "entity": entity,
                    "tile_x": x,
                    "tile_y": y,
                    "collision_type": collision_type
                })
        elif collision_type in self.collision_handlers:
            # Call custom collision handler
            self.collision_handlers[collision_type](entity, x, y, tile)
    
    def _on_world_clearing(self, event_data):
        """
        Handle world clearing event.
        
        Args:
            event_data: Event data (unused)
        """
        # Clear current map
        self.current_map = None
    
    def register_entity_spawner(self, entity_type, spawner_func):
        """
        Register a function to spawn entities of a specific type.
        
        Args:
            entity_type: Type of entity to register spawner for
            spawner_func: Function to call to spawn entity (takes x, y, properties)
            
        Returns:
            MapSystem: Self for method chaining
        """
        self.entity_spawners[entity_type] = spawner_func
        return self
    
    def register_collision_handler(self, collision_type, handler_func):
        """
        Register a function to handle collisions of a specific type.
        
        Args:
            collision_type: Type of collision to register handler for
            handler_func: Function to call to handle collision (takes entity, x, y, tile)
            
        Returns:
            MapSystem: Self for method chaining
        """
        self.collision_handlers[collision_type] = handler_func
        return self
    
    def set_maps_directory(self, directory):
        """
        Set the directory where map files are stored.
        
        Args:
            directory: Path to the maps directory
            
        Returns:
            MapSystem: Self for method chaining
        """
        self.maps_directory = directory
        return self
    
    def load_map(self, map_name, spawn_entities=True):
        """
        Load a map by name.
        
        Args:
            map_name: Name of the map to load
            spawn_entities: Whether to spawn entities defined in the map
            
        Returns:
            Map: The loaded map, or None if load failed
        """
        # Check if map is in cache
        if map_name in self.map_cache:
            self.current_map = self.map_cache[map_name]
            
            # Emit map loaded event
            self.event_manager.emit(EventType.MAP_LOADED, {
                "map_name": map_name,
                "map": self.current_map
            })
            
            # Spawn entities if requested
            if spawn_entities:
                self._spawn_map_entities()
            
            return self.current_map
        
        # Try to load map from file
        file_path = os.path.join(self.maps_directory, f"{map_name}.json")
        
        map_instance = Map.load_from_file(file_path)
        if map_instance:
            # Add to cache
            self.map_cache[map_name] = map_instance
            self.current_map = map_instance
            
            # Emit map loaded event
            self.event_manager.emit(EventType.MAP_LOADED, {
                "map_name": map_name,
                "map": self.current_map
            })
            
            # Spawn entities if requested
            if spawn_entities:
                self._spawn_map_entities()
            
            return map_instance
        
        return None
    
    def create_map(self, width, height, default_tile_type=TileType.EMPTY, name="Unnamed Map"):
        """
        Create a new map.
        
        Args:
            width: Width of the map in tiles
            height: Height of the map in tiles
            default_tile_type: Type to use for all tiles by default
            name: Name of the map
            
        Returns:
            Map: The created map
        """
        map_instance = Map(width, height, default_tile_type)
        map_instance.name = name
        
        self.current_map = map_instance
        
        # Emit map created event
        self.event_manager.emit(EventType.MAP_CREATED, {
            "map": map_instance
        })
        
        return map_instance
    
    def save_current_map(self, map_name=None):
        """
        Save the current map.
        
        Args:
            map_name: Name to save the map as, or None to use the map's current name
            
        Returns:
            bool: True if save successful, False otherwise
        """
        if not self.current_map:
            return False
        
        # Use provided name or map's current name
        name = map_name or self.current_map.name
        
        # Ensure maps directory exists
        os.makedirs(self.maps_directory, exist_ok=True)
        
        # Save map to file
        file_path = os.path.join(self.maps_directory, f"{name}.json")
        success = self.current_map.save_to_file(file_path)
        
        if success:
            # Add to cache
            self.map_cache[name] = self.current_map
            
            # Emit map saved event
            self.event_manager.emit(EventType.MAP_SAVED, {
                "map_name": name,
                "map": self.current_map
            })
        
        return success
    
    def _spawn_map_entities(self):
        """Spawn entities defined in the current map."""
        if not self.current_map:
            return
        
        for spawn_data in self.current_map.entity_spawns:
            entity_type = spawn_data.get("entity_type")
            x = spawn_data.get("x", 0)
            y = spawn_data.get("y", 0)
            properties = spawn_data.get("properties", {})
            
            # Check if we have a spawner for this entity type
            if entity_type in self.entity_spawners:
                spawner = self.entity_spawners[entity_type]
                entity = spawner(x, y, properties)
                
                # Emit entity spawned event
                self.event_manager.emit(EventType.ENTITY_SPAWNED, {
                    "entity": entity,
                    "x": x,
                    "y": y,
                    "properties": properties
                })
    
    def update(self, dt):
        """
        Update the map system.
        
        Args:
            dt: Delta time in seconds
        """
        # Map system doesn't need per-frame updates for now
        pass
    
    def get_tile_at_position(self, x, y):
        """
        Get the tile at a specific world position.
        
        Args:
            x: X coordinate in world space
            y: Y coordinate in world space
            
        Returns:
            Tile: The tile at the specified position, or None if no tile or no map
        """
        if not self.current_map:
            return None
        
        # Convert world position to tile coordinates
        tile_x, tile_y = math.floor(x), math.floor(y)
        return self.current_map.get_tile(tile_x, tile_y)
    
    def is_position_walkable(self, x, y):
        """
        Check if a position is walkable.
        
        Args:
            x: X coordinate in world space
            y: Y coordinate in world space
            
        Returns:
            bool: True if the position is walkable, False otherwise
        """
        if not self.current_map:
            return False
        
        # Convert world position to tile coordinates
        tile_x, tile_y = math.floor(x), math.floor(y)
        return self.current_map.is_walkable(tile_x, tile_y)
    
    def find_path(self, start_x, start_y, end_x, end_y, max_distance=float('inf')):
        """
        Find a path from start to end using the current map's pathfinding.
        
        Args:
            start_x: Start X coordinate in world space
            start_y: Start Y coordinate in world space
            end_x: End X coordinate in world space
            end_y: End Y coordinate in world space
            max_distance: Maximum distance to search
            
        Returns:
            list: List of (x, y) tuples representing the path, or empty list if no path found
        """
        if not self.current_map:
            return []
        
        # Convert world positions to tile coordinates
        start_tile_x, start_tile_y = math.floor(start_x), math.floor(start_y)
        end_tile_x, end_tile_y = math.floor(end_x), math.floor(end_y)
        
        # Get path from the map
        path = self.current_map.get_path(start_tile_x, start_tile_y, end_tile_x, end_tile_y, max_distance)
        
        # Convert tile coordinates to world coordinates (center of tiles)
        world_path = [(x + 0.5, y + 0.5) for x, y in path]
        
        return world_path
    
    def check_line_of_sight(self, start_x, start_y, end_x, end_y):
        """
        Check if there is a clear line of sight between two points.
        
        Args:
            start_x: Start X coordinate in world space
            start_y: Start Y coordinate in world space
            end_x: End X coordinate in world space
            end_y: End Y coordinate in world space
            
        Returns:
            bool: True if line of sight is clear, False if blocked or no map
        """
        if not self.current_map:
            return False
        
        # Convert world positions to tile coordinates
        start_tile_x, start_tile_y = math.floor(start_x), math.floor(start_y)
        end_tile_x, end_tile_y = math.floor(end_x), math.floor(end_y)
        
        # Check if line of sight is blocked
        is_blocked = self.current_map.get_blocked_line_of_sight(
            start_tile_x, start_tile_y, end_tile_x, end_tile_y)
        
        # Return True if NOT blocked
        return not is_blocked 