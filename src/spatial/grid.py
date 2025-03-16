"""
Spatial grid for efficient entity queries.

This module provides spatial partitioning to efficiently find entities in proximity
to each other without having to check every entity in the world.
"""

import math
from collections import defaultdict


class SpatialGrid:
    """
    A spatial partitioning grid for efficient proximity queries.
    
    This grid divides the world into cells and keeps track of which entities are in
    which cells, allowing for fast queries like "find all entities near this position"
    without having to check every entity in the world.
    """
    
    def __init__(self, cell_size=4.0):
        """
        Initialize the spatial grid.
        
        Args:
            cell_size: Size of each cell in world units (default: 4.0)
        """
        self.cell_size = cell_size
        self.cells = defaultdict(set)  # (cell_x, cell_y) -> set of entity IDs
        self.entity_positions = {}  # entity_id -> (x, y)
        
    def _get_cell_coords(self, x, y):
        """
        Get the cell coordinates for a world position.
        
        Args:
            x: X coordinate in world space
            y: Y coordinate in world space
            
        Returns:
            tuple: (cell_x, cell_y)
        """
        cell_x = math.floor(x / self.cell_size)
        cell_y = math.floor(y / self.cell_size)
        return (cell_x, cell_y)
    
    def add_entity(self, entity_id, x, y):
        """
        Add an entity to the grid at the specified position.
        
        Args:
            entity_id: ID of the entity
            x: X coordinate in world space
            y: Y coordinate in world space
            
        Returns:
            SpatialGrid: Self for method chaining
        """
        # Remove entity from its current cell if it exists
        self.remove_entity(entity_id)
        
        # Add entity to the appropriate cell
        cell_coords = self._get_cell_coords(x, y)
        self.cells[cell_coords].add(entity_id)
        
        # Store the entity's position
        self.entity_positions[entity_id] = (x, y)
        
        return self
    
    def remove_entity(self, entity_id):
        """
        Remove an entity from the grid.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            SpatialGrid: Self for method chaining
        """
        # Skip if entity isn't in the grid
        if entity_id not in self.entity_positions:
            return self
        
        # Get the entity's current cell
        x, y = self.entity_positions[entity_id]
        cell_coords = self._get_cell_coords(x, y)
        
        # Remove entity from the cell
        if cell_coords in self.cells and entity_id in self.cells[cell_coords]:
            self.cells[cell_coords].remove(entity_id)
            
            # Clean up empty cells
            if not self.cells[cell_coords]:
                del self.cells[cell_coords]
        
        # Remove entity's position
        del self.entity_positions[entity_id]
        
        return self
    
    def move_entity(self, entity_id, new_x, new_y):
        """
        Move an entity to a new position in the grid.
        
        Args:
            entity_id: ID of the entity
            new_x: New X coordinate in world space
            new_y: New Y coordinate in world space
            
        Returns:
            bool: True if the entity was moved, False if not found
        """
        # Skip if entity isn't in the grid
        if entity_id not in self.entity_positions:
            return False
        
        # Get the entity's current and new cells
        old_x, old_y = self.entity_positions[entity_id]
        old_cell = self._get_cell_coords(old_x, old_y)
        new_cell = self._get_cell_coords(new_x, new_y)
        
        # If the entity is moving to a different cell, update the grid
        if old_cell != new_cell:
            # Remove from old cell
            self.cells[old_cell].remove(entity_id)
            
            # Clean up empty cells
            if not self.cells[old_cell]:
                del self.cells[old_cell]
            
            # Add to new cell
            self.cells[new_cell].add(entity_id)
        
        # Update the entity's position
        self.entity_positions[entity_id] = (new_x, new_y)
        
        return True
    
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
        # Calculate the bounds of cells to check
        min_cell_x = math.floor((x - radius) / self.cell_size)
        max_cell_x = math.floor((x + radius) / self.cell_size)
        min_cell_y = math.floor((y - radius) / self.cell_size)
        max_cell_y = math.floor((y + radius) / self.cell_size)
        
        # Collect all potential entities
        entities_in_range = set()
        for cell_x in range(min_cell_x, max_cell_x + 1):
            for cell_y in range(min_cell_y, max_cell_y + 1):
                cell_coords = (cell_x, cell_y)
                if cell_coords in self.cells:
                    entities_in_range.update(self.cells[cell_coords])
        
        # Filter entities based on actual distance
        squared_radius = radius * radius
        result = set()
        
        for entity_id in entities_in_range:
            entity_x, entity_y = self.entity_positions[entity_id]
            dx = entity_x - x
            dy = entity_y - y
            distance_squared = dx*dx + dy*dy
            
            if distance_squared <= squared_radius:
                result.add(entity_id)
        
        return result
    
    def get_entities_in_cell(self, cell_x, cell_y):
        """
        Get all entities in a specific cell.
        
        Args:
            cell_x: X coordinate of the cell
            cell_y: Y coordinate of the cell
            
        Returns:
            set: Set of entity IDs in the cell
        """
        cell_coords = (cell_x, cell_y)
        return self.cells.get(cell_coords, set()).copy()
    
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
        # Calculate the bounds of cells to check
        min_cell_x = math.floor(min_x / self.cell_size)
        max_cell_x = math.floor(max_x / self.cell_size)
        min_cell_y = math.floor(min_y / self.cell_size)
        max_cell_y = math.floor(max_y / self.cell_size)
        
        # Collect all potential entities
        entities_in_rect = set()
        for cell_x in range(min_cell_x, max_cell_x + 1):
            for cell_y in range(min_cell_y, max_cell_y + 1):
                cell_coords = (cell_x, cell_y)
                if cell_coords in self.cells:
                    entities_in_rect.update(self.cells[cell_coords])
        
        # Filter entities based on actual position
        result = set()
        
        for entity_id in entities_in_rect:
            entity_x, entity_y = self.entity_positions[entity_id]
            if min_x <= entity_x <= max_x and min_y <= entity_y <= max_y:
                result.add(entity_id)
        
        return result
    
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
        # Start with a small radius and expand until we find something
        search_radius = min(self.cell_size, max_radius)
        
        while search_radius <= max_radius:
            entities = self.get_entities_in_range(x, y, search_radius)
            
            if filter_func:
                entities = {entity_id for entity_id in entities if filter_func(entity_id)}
            
            if entities:
                # Find the nearest entity
                nearest_entity = None
                nearest_distance = float('inf')
                
                for entity_id in entities:
                    entity_x, entity_y = self.entity_positions[entity_id]
                    dx = entity_x - x
                    dy = entity_y - y
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    if distance < nearest_distance:
                        nearest_entity = entity_id
                        nearest_distance = distance
                
                return nearest_entity, nearest_distance
            
            # Double the search radius and try again
            search_radius *= 2
        
        return None, float('inf')
    
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
        # Calculate direction vector
        dx = end_x - start_x
        dy = end_y - start_y
        length = math.sqrt(dx*dx + dy*dy)
        
        # Normalize direction vector
        if length > 0:
            dx /= length
            dy /= length
        
        # Calculate the distance to travel
        travel_distance = min(length, max_distance)
        
        # Calculate endpoint
        actual_end_x = start_x + dx * travel_distance
        actual_end_y = start_y + dy * travel_distance
        
        # Get the bounding box of the ray
        min_x = min(start_x, actual_end_x)
        max_x = max(start_x, actual_end_x)
        min_y = min(start_y, actual_end_y)
        max_y = max(start_y, actual_end_y)
        
        # Add a small buffer to ensure we catch entities near the ray
        buffer = self.cell_size * 0.5
        min_x -= buffer
        max_x += buffer
        min_y -= buffer
        max_y += buffer
        
        # Get all entities in the bounding box
        entities_in_rect = self.get_entities_in_rect(min_x, min_y, max_x, max_y)
        
        # Calculate the nearest point on the ray for each entity
        results = []
        
        for entity_id in entities_in_rect:
            entity_x, entity_y = self.entity_positions[entity_id]
            
            # Calculate vector from start to entity
            to_entity_x = entity_x - start_x
            to_entity_y = entity_y - start_y
            
            # Project this vector onto the ray
            projection = to_entity_x * dx + to_entity_y * dy
            
            # Clamp projection to ray length
            projection = max(0, min(travel_distance, projection))
            
            # Calculate the nearest point on the ray
            nearest_x = start_x + dx * projection
            nearest_y = start_y + dy * projection
            
            # Calculate distance from entity to nearest point
            entity_dx = entity_x - nearest_x
            entity_dy = entity_y - nearest_y
            entity_distance = math.sqrt(entity_dx*entity_dx + entity_dy*entity_dy)
            
            # If entity is close enough to the ray (using half a cell size as threshold)
            if entity_distance <= buffer:
                # Distance along the ray
                ray_distance = projection
                results.append((entity_id, ray_distance))
        
        # Sort results by distance
        results.sort(key=lambda x: x[1])
        
        return results
    
    def clear(self):
        """
        Clear all data in the grid.
        
        Returns:
            SpatialGrid: Self for method chaining
        """
        self.cells.clear()
        self.entity_positions.clear()
        return self
    
    def get_stats(self):
        """
        Get statistics about the grid.
        
        Returns:
            dict: Statistics about the grid
        """
        return {
            "cell_size": self.cell_size,
            "num_cells": len(self.cells),
            "num_entities": len(self.entity_positions),
            "cells_per_entity": len(self.cells) / max(1, len(self.entity_positions)),
            "entities_per_cell": len(self.entity_positions) / max(1, len(self.cells))
        } 