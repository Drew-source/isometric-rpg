"""
Map system for the isometric RPG.

This module provides map representation, loading, and serialization functionality.
"""

import json
import os
import math
from collections import defaultdict
from enum import Enum


class TileType(Enum):
    """Enum representing the different types of tiles."""
    EMPTY = 0
    FLOOR = 1
    WALL = 2
    DOOR = 3
    WATER = 4
    LAVA = 5
    GRASS = 6
    DIRT = 7
    STONE = 8
    WOOD = 9
    CUSTOM = 10


class CollisionType(Enum):
    """Enum representing the different types of collision."""
    NONE = 0  # No collision
    BLOCK = 1  # Completely blocks movement
    SLOW = 2  # Slows movement
    DAMAGE = 3  # Damages entities
    CLIMB = 4  # Requires climbing
    CUSTOM = 5  # Custom collision handler


class Tile:
    """
    Represents a single tile in the map.
    
    A tile has a type, properties, and can contain additional data like
    collision information and rendering details.
    """
    
    def __init__(self, tile_type=TileType.EMPTY, collision_type=CollisionType.NONE):
        """
        Initialize a tile.
        
        Args:
            tile_type: Type of the tile (default: TileType.EMPTY)
            collision_type: Type of collision (default: CollisionType.NONE)
        """
        self.tile_type = tile_type
        self.collision_type = collision_type
        self.properties = {}
        self.elevation = 0.0
        self.texture_index = 0
        self.tint_color = (1.0, 1.0, 1.0, 1.0)  # RGBA
    
    def serialize(self):
        """
        Convert tile data to a serializable format.
        
        Returns:
            dict: Serialized tile data
        """
        return {
            "tile_type": self.tile_type.value,
            "collision_type": self.collision_type.value,
            "properties": self.properties,
            "elevation": self.elevation,
            "texture_index": self.texture_index,
            "tint_color": self.tint_color
        }
    
    @classmethod
    def deserialize(cls, data):
        """
        Create a tile from serialized data.
        
        Args:
            data: Serialized tile data
            
        Returns:
            Tile: New tile instance
        """
        tile = cls(
            tile_type=TileType(data.get("tile_type", TileType.EMPTY.value)),
            collision_type=CollisionType(data.get("collision_type", CollisionType.NONE.value))
        )
        tile.properties = data.get("properties", {})
        tile.elevation = data.get("elevation", 0.0)
        tile.texture_index = data.get("texture_index", 0)
        tile.tint_color = data.get("tint_color", (1.0, 1.0, 1.0, 1.0))
        return tile


class Map:
    """
    Represents a game map with tiles and entities.
    
    The map stores a grid of tiles, as well as information about entities
    that should be spawned when the map is loaded.
    """
    
    def __init__(self, width, height, default_tile_type=TileType.EMPTY):
        """
        Initialize a map.
        
        Args:
            width: Width of the map in tiles
            height: Height of the map in tiles
            default_tile_type: Type to use for all tiles by default
        """
        self.width = width
        self.height = height
        self.tiles = {}  # (x, y) -> Tile
        self.entity_spawns = []  # List of entity spawn data
        self.properties = {}  # Map-level properties
        self.name = "Unnamed Map"
        self.tileset_name = "default"
        
        # Initialize all tiles to the default type
        for x in range(width):
            for y in range(height):
                self.tiles[(x, y)] = Tile(tile_type=default_tile_type)
    
    def get_tile(self, x, y):
        """
        Get the tile at a specific position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Tile: The tile at the specified position, or None if out of bounds
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles.get((x, y))
        return None
    
    def set_tile(self, x, y, tile):
        """
        Set the tile at a specific position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            tile: The tile to set
            
        Returns:
            bool: True if the tile was set, False if out of bounds
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[(x, y)] = tile
            return True
        return False
    
    def set_tile_type(self, x, y, tile_type):
        """
        Set the type of the tile at a specific position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            tile_type: The tile type to set
            
        Returns:
            bool: True if the tile type was set, False if out of bounds
        """
        tile = self.get_tile(x, y)
        if tile:
            tile.tile_type = tile_type
            return True
        return False
    
    def set_collision_type(self, x, y, collision_type):
        """
        Set the collision type of the tile at a specific position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            collision_type: The collision type to set
            
        Returns:
            bool: True if the collision type was set, False if out of bounds
        """
        tile = self.get_tile(x, y)
        if tile:
            tile.collision_type = collision_type
            return True
        return False
    
    def add_entity_spawn(self, entity_type, x, y, properties=None):
        """
        Add an entity spawn point to the map.
        
        Args:
            entity_type: Type of entity to spawn
            x: X coordinate
            y: Y coordinate
            properties: Additional properties for the entity
            
        Returns:
            Map: Self for method chaining
        """
        spawn_data = {
            "entity_type": entity_type,
            "x": x,
            "y": y,
            "properties": properties or {}
        }
        self.entity_spawns.append(spawn_data)
        return self
    
    def remove_entity_spawn(self, index):
        """
        Remove an entity spawn point from the map.
        
        Args:
            index: Index of the spawn point to remove
            
        Returns:
            bool: True if the spawn point was removed, False if index is out of bounds
        """
        if 0 <= index < len(self.entity_spawns):
            del self.entity_spawns[index]
            return True
        return False
    
    def set_property(self, key, value):
        """
        Set a map property.
        
        Args:
            key: Property key
            value: Property value
            
        Returns:
            Map: Self for method chaining
        """
        self.properties[key] = value
        return self
    
    def get_property(self, key, default=None):
        """
        Get a map property.
        
        Args:
            key: Property key
            default: Default value to return if property doesn't exist
            
        Returns:
            The property value, or the default if not found
        """
        return self.properties.get(key, default)
    
    def get_neighbors(self, x, y):
        """
        Get all neighboring tiles of a position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            dict: Dictionary mapping direction names to tiles
        """
        neighbors = {}
        directions = {
            "north": (0, 1),
            "northeast": (1, 1),
            "east": (1, 0),
            "southeast": (1, -1),
            "south": (0, -1),
            "southwest": (-1, -1),
            "west": (-1, 0),
            "northwest": (-1, 1)
        }
        
        for direction, (dx, dy) in directions.items():
            neighbors[direction] = self.get_tile(x + dx, y + dy)
        
        return neighbors
    
    def is_walkable(self, x, y):
        """
        Check if a tile can be walked on.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            bool: True if the tile is walkable, False otherwise
        """
        tile = self.get_tile(x, y)
        if not tile:
            return False
        
        return tile.collision_type not in [CollisionType.BLOCK, CollisionType.DAMAGE]
    
    def get_path(self, start_x, start_y, end_x, end_y, max_distance=float('inf')):
        """
        Find a path from start to end using A* pathfinding.
        
        This is a simple implementation and might not be suitable for all cases.
        For a more complete implementation, consider using a dedicated pathfinding
        module or implementing A* with more features.
        
        Args:
            start_x: Start X coordinate
            start_y: Start Y coordinate
            end_x: End X coordinate
            end_y: End Y coordinate
            max_distance: Maximum distance to search
            
        Returns:
            list: List of (x, y) tuples representing the path, or empty list if no path found
        """
        # Basic A* implementation
        from heapq import heappush, heappop
        
        def heuristic(a, b):
            """Manhattan distance heuristic."""
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        # Check if start and end are valid
        if not self.is_walkable(start_x, start_y) or not self.is_walkable(end_x, end_y):
            return []
        
        # Initialize open and closed sets
        open_set = []
        closed_set = set()
        came_from = {}
        g_score = defaultdict(lambda: float('inf'))
        f_score = defaultdict(lambda: float('inf'))
        
        start = (start_x, start_y)
        end = (end_x, end_y)
        
        g_score[start] = 0
        f_score[start] = heuristic(start, end)
        heappush(open_set, (f_score[start], start))
        
        while open_set:
            _, current = heappop(open_set)
            
            if current == end:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path
            
            closed_set.add(current)
            
            # Check if we've exceeded the maximum distance
            if g_score[current] > max_distance:
                continue
            
            # Check neighbors
            x, y = current
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (x + dx, y + dy)
                neighbor_x, neighbor_y = neighbor
                
                if not self.is_walkable(neighbor_x, neighbor_y):
                    continue
                
                if neighbor in closed_set:
                    continue
                
                tentative_g_score = g_score[current] + 1
                
                if tentative_g_score >= g_score[neighbor]:
                    continue
                
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, end)
                
                # Add to open set if not already there
                if neighbor not in [item[1] for item in open_set]:
                    heappush(open_set, (f_score[neighbor], neighbor))
        
        # No path found
        return []
    
    def get_blocked_line_of_sight(self, start_x, start_y, end_x, end_y):
        """
        Check if there is a clear line of sight between two points.
        
        Uses Bresenham's line algorithm to check for blocking tiles.
        
        Args:
            start_x: Start X coordinate
            start_y: Start Y coordinate
            end_x: End X coordinate
            end_y: End Y coordinate
            
        Returns:
            bool: True if line of sight is blocked, False otherwise
        """
        # Bresenham's line algorithm
        dx = abs(end_x - start_x)
        dy = abs(end_y - start_y)
        sx = 1 if start_x < end_x else -1
        sy = 1 if start_y < end_y else -1
        err = dx - dy
        
        x, y = start_x, start_y
        
        while x != end_x or y != end_y:
            # Skip the starting tile
            if x != start_x or y != start_y:
                tile = self.get_tile(x, y)
                if tile and tile.collision_type == CollisionType.BLOCK:
                    return True
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        
        return False
    
    def resize(self, new_width, new_height, default_tile_type=None):
        """
        Resize the map to new dimensions.
        
        Args:
            new_width: New width of the map in tiles
            new_height: New height of the map in tiles
            default_tile_type: Type to use for new tiles (default: None, uses existing default)
            
        Returns:
            Map: Self for method chaining
        """
        if default_tile_type is None:
            # Use the type of the top-left tile as default
            default_tile = self.get_tile(0, 0)
            default_tile_type = default_tile.tile_type if default_tile else TileType.EMPTY
        
        # Create new tiles for expanded areas
        new_tiles = {}
        for x in range(new_width):
            for y in range(new_height):
                if 0 <= x < self.width and 0 <= y < self.height:
                    # Copy existing tile
                    new_tiles[(x, y)] = self.tiles.get((x, y))
                else:
                    # Create new tile with default type
                    new_tiles[(x, y)] = Tile(tile_type=default_tile_type)
        
        self.width = new_width
        self.height = new_height
        self.tiles = new_tiles
        
        return self
    
    def fill_rect(self, start_x, start_y, end_x, end_y, tile_type, collision_type=None):
        """
        Fill a rectangular area with a specific tile type.
        
        Args:
            start_x: Start X coordinate
            start_y: Start Y coordinate
            end_x: End X coordinate
            end_y: End Y coordinate
            tile_type: Type of tile to fill with
            collision_type: Type of collision to set, or None to leave unchanged
            
        Returns:
            Map: Self for method chaining
        """
        # Ensure start is before end
        start_x, end_x = min(start_x, end_x), max(start_x, end_x)
        start_y, end_y = min(start_y, end_y), max(start_y, end_y)
        
        # Clamp to map boundaries
        start_x = max(0, start_x)
        start_y = max(0, start_y)
        end_x = min(self.width - 1, end_x)
        end_y = min(self.height - 1, end_y)
        
        for x in range(start_x, end_x + 1):
            for y in range(start_y, end_y + 1):
                tile = self.get_tile(x, y)
                if tile:
                    tile.tile_type = tile_type
                    if collision_type is not None:
                        tile.collision_type = collision_type
        
        return self
    
    def fill_circle(self, center_x, center_y, radius, tile_type, collision_type=None):
        """
        Fill a circular area with a specific tile type.
        
        Args:
            center_x: Center X coordinate
            center_y: Center Y coordinate
            radius: Radius of the circle
            tile_type: Type of tile to fill with
            collision_type: Type of collision to set, or None to leave unchanged
            
        Returns:
            Map: Self for method chaining
        """
        # Calculate bounds of the circle
        start_x = max(0, int(center_x - radius))
        start_y = max(0, int(center_y - radius))
        end_x = min(self.width - 1, int(center_x + radius))
        end_y = min(self.height - 1, int(center_y + radius))
        
        # Calculate squared radius for faster checks
        squared_radius = radius * radius
        
        for x in range(start_x, end_x + 1):
            for y in range(start_y, end_y + 1):
                # Check if point is within circle
                dx = x - center_x
                dy = y - center_y
                distance_squared = dx*dx + dy*dy
                
                if distance_squared <= squared_radius:
                    tile = self.get_tile(x, y)
                    if tile:
                        tile.tile_type = tile_type
                        if collision_type is not None:
                            tile.collision_type = collision_type
        
        return self
    
    def serialize(self):
        """
        Convert map data to a serializable format.
        
        Returns:
            dict: Serialized map data
        """
        serialized_tiles = {}
        for pos, tile in self.tiles.items():
            serialized_tiles[f"{pos[0]},{pos[1]}"] = tile.serialize()
        
        return {
            "width": self.width,
            "height": self.height,
            "name": self.name,
            "tileset_name": self.tileset_name,
            "properties": self.properties,
            "tiles": serialized_tiles,
            "entity_spawns": self.entity_spawns
        }
    
    @classmethod
    def deserialize(cls, data):
        """
        Create a map from serialized data.
        
        Args:
            data: Serialized map data
            
        Returns:
            Map: New map instance
        """
        width = data.get("width", 1)
        height = data.get("height", 1)
        
        map_instance = cls(width, height)
        map_instance.name = data.get("name", "Unnamed Map")
        map_instance.tileset_name = data.get("tileset_name", "default")
        map_instance.properties = data.get("properties", {})
        map_instance.entity_spawns = data.get("entity_spawns", [])
        
        # Deserialize tiles
        serialized_tiles = data.get("tiles", {})
        for pos_str, tile_data in serialized_tiles.items():
            x, y = map(int, pos_str.split(","))
            map_instance.tiles[(x, y)] = Tile.deserialize(tile_data)
        
        return map_instance
    
    def save_to_file(self, filename):
        """
        Save the map to a file.
        
        Args:
            filename: Path to the file to save to
            
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            with open(filename, 'w') as file:
                json.dump(self.serialize(), file, indent=2)
            return True
        except Exception as e:
            print(f"Error saving map: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filename):
        """
        Load a map from a file.
        
        Args:
            filename: Path to the file to load from
            
        Returns:
            Map: Loaded map instance, or None if load failed
        """
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
            return cls.deserialize(data)
        except Exception as e:
            print(f"Error loading map: {e}")
            return None 