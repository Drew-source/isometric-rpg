"""
Camera system for the isometric RPG.

This module provides camera functionality for the isometric view, including
coordinate transformations, zooming, rotation, and viewport management.
"""

import math


class Camera:
    """
    Camera for managing the view of the game world.
    
    The camera handles the conversion between world coordinates and screen coordinates,
    as well as providing functionality for zooming, rotating, and moving the view.
    """
    
    def __init__(self, viewport_width, viewport_height, zoom=1.0, rotation=0.0):
        """
        Initialize the camera.
        
        Args:
            viewport_width: Width of the viewport in pixels
            viewport_height: Height of the viewport in pixels
            zoom: Initial zoom level (default: 1.0)
            rotation: Initial rotation in degrees (default: 0.0)
        """
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.position = (0.0, 0.0)  # Camera position in world space (x, y)
        self.zoom = zoom  # Zoom level (1.0 = 100%)
        self.rotation_degrees = rotation  # Rotation in degrees
        
        # Isometric projection settings
        self.tile_width = 64  # Width of a tile in pixels at zoom=1.0
        self.tile_height = 32  # Height of a tile in pixels at zoom=1.0
        self.tile_depth = 16   # Depth (z) of a tile in pixels at zoom=1.0
        
        # Calculate rotational values
        self._update_rotation()
    
    def _update_rotation(self):
        """Update internal rotation values."""
        # Convert rotation from degrees to radians
        self.rotation = math.radians(self.rotation_degrees)
        self.sin_rotation = math.sin(self.rotation)
        self.cos_rotation = math.cos(self.rotation)
    
    def set_position(self, x, y):
        """
        Set the camera position in world space.
        
        Args:
            x: X coordinate in world space
            y: Y coordinate in world space
            
        Returns:
            Camera: Self for method chaining
        """
        self.position = (x, y)
        return self
    
    def move(self, dx, dy):
        """
        Move the camera relative to its current position.
        
        Args:
            dx: Change in X coordinate
            dy: Change in Y coordinate
            
        Returns:
            Camera: Self for method chaining
        """
        x, y = self.position
        self.position = (x + dx, y + dy)
        return self
    
    def set_zoom(self, zoom):
        """
        Set the zoom level.
        
        Args:
            zoom: Zoom level (1.0 = 100%)
            
        Returns:
            Camera: Self for method chaining
        """
        # Clamp zoom to reasonable values
        self.zoom = max(0.1, min(10.0, zoom))
        return self
    
    def zoom_in(self, factor=1.2):
        """
        Zoom in by the specified factor.
        
        Args:
            factor: Zoom in factor (default: 1.2)
            
        Returns:
            Camera: Self for method chaining
        """
        return self.set_zoom(self.zoom * factor)
    
    def zoom_out(self, factor=1.2):
        """
        Zoom out by the specified factor.
        
        Args:
            factor: Zoom out factor (default: 1.2)
            
        Returns:
            Camera: Self for method chaining
        """
        return self.set_zoom(self.zoom / factor)
    
    def set_rotation(self, degrees):
        """
        Set the rotation in degrees.
        
        Args:
            degrees: Rotation in degrees
            
        Returns:
            Camera: Self for method chaining
        """
        self.rotation_degrees = degrees % 360
        self._update_rotation()
        return self
    
    def rotate(self, delta_degrees):
        """
        Rotate by the specified amount.
        
        Args:
            delta_degrees: Change in rotation in degrees
            
        Returns:
            Camera: Self for method chaining
        """
        return self.set_rotation(self.rotation_degrees + delta_degrees)
    
    def world_to_screen(self, world_x, world_y, world_z=0):
        """
        Convert world coordinates to screen coordinates.
        
        Args:
            world_x: X coordinate in world space
            world_y: Y coordinate in world space
            world_z: Z coordinate in world space (default: 0)
            
        Returns:
            tuple: (screen_x, screen_y)
        """
        # Translate world coordinates relative to camera position
        x = world_x - self.position[0]
        y = world_y - self.position[1]
        
        # Apply rotation if needed
        if self.rotation_degrees != 0:
            old_x, old_y = x, y
            x = old_x * self.cos_rotation - old_y * self.sin_rotation
            y = old_x * self.sin_rotation + old_y * self.cos_rotation
        
        # Apply isometric projection
        # Classic isometric projection is at a 2:1 ratio and rotated 45 degrees
        screen_x = (x - y) * (self.tile_width / 2) * self.zoom
        screen_y = (x + y) * (self.tile_height / 2) * self.zoom - world_z * self.tile_depth * self.zoom
        
        # Center on the screen
        screen_x += self.viewport_width / 2
        screen_y += self.viewport_height / 2
        
        return (screen_x, screen_y)
    
    def screen_to_world(self, screen_x, screen_y, world_z=0):
        """
        Convert screen coordinates to world coordinates.
        
        Args:
            screen_x: X coordinate in screen space
            screen_y: Y coordinate in screen space
            world_z: Z coordinate in world space (default: 0)
            
        Returns:
            tuple: (world_x, world_y)
        """
        # Center on the screen
        screen_x -= self.viewport_width / 2
        screen_y -= self.viewport_height / 2
        
        # Adjust for Z
        screen_y += world_z * self.tile_depth * self.zoom
        
        # Reverse isometric projection
        # The isometric transformation matrix is:
        # [ 0.5,  0.5]
        # [-1.0,  1.0]
        # And we need the inverse:
        # [ 1.0,  0.5]
        # [-1.0,  0.5]
        tile_width_scaled = self.tile_width * self.zoom
        tile_height_scaled = self.tile_height * self.zoom
        
        world_x = (screen_x / tile_width_scaled + screen_y / tile_height_scaled) / 1.0
        world_y = (screen_y / tile_height_scaled - screen_x / tile_width_scaled) / 1.0
        
        # Apply reverse rotation if needed
        if self.rotation_degrees != 0:
            old_x, old_y = world_x, world_y
            world_x = old_x * self.cos_rotation + old_y * self.sin_rotation
            world_y = -old_x * self.sin_rotation + old_y * self.cos_rotation
        
        # Translate back to world coordinates
        world_x += self.position[0]
        world_y += self.position[1]
        
        return (world_x, world_y)
    
    def get_visible_tiles(self, map_width, map_height):
        """
        Get the range of map tiles that are visible in the viewport.
        
        This is used for culling invisible tiles for better performance.
        
        Args:
            map_width: Width of the map in tiles
            map_height: Height of the map in tiles
            
        Returns:
            tuple: (min_x, min_y, max_x, max_y) bounds of visible tiles
        """
        # Get the world coordinates of the screen corners
        top_left = self.screen_to_world(0, 0)
        top_right = self.screen_to_world(self.viewport_width, 0)
        bottom_left = self.screen_to_world(0, self.viewport_height)
        bottom_right = self.screen_to_world(self.viewport_width, self.viewport_height)
        
        # Find the minimum and maximum tile coordinates
        points = [top_left, top_right, bottom_left, bottom_right]
        min_x = min(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_x = max(p[0] for p in points)
        max_y = max(p[1] for p in points)
        
        # Add a small buffer to ensure we capture partially visible tiles
        buffer = 1
        min_x = max(0, math.floor(min_x) - buffer)
        min_y = max(0, math.floor(min_y) - buffer)
        max_x = min(map_width - 1, math.ceil(max_x) + buffer)
        max_y = min(map_height - 1, math.ceil(max_y) + buffer)
        
        return (int(min_x), int(min_y), int(max_x), int(max_y))
    
    def is_visible(self, world_x, world_y, world_z=0, object_radius=1.0):
        """
        Check if a point in world space is visible in the viewport.
        
        Args:
            world_x: X coordinate in world space
            world_y: Y coordinate in world space
            world_z: Z coordinate in world space (default: 0)
            object_radius: Radius of the object in world units (default: 1.0)
            
        Returns:
            bool: True if the point is visible in the viewport
        """
        # Convert to screen space
        screen_x, screen_y = self.world_to_screen(world_x, world_y, world_z)
        
        # Calculate the screen radius of the object
        screen_radius = object_radius * self.tile_width * self.zoom
        
        # Check if within viewport bounds (with buffer for object radius)
        return (
            screen_x + screen_radius >= 0 and
            screen_x - screen_radius <= self.viewport_width and
            screen_y + screen_radius >= 0 and
            screen_y - screen_radius <= self.viewport_height
        )
    
    def world_distance_to_screen(self, world_distance):
        """
        Convert a distance in world units to screen pixels.
        
        Args:
            world_distance: Distance in world units
            
        Returns:
            float: Distance in screen pixels
        """
        return world_distance * self.tile_width * self.zoom
    
    def screen_distance_to_world(self, screen_distance):
        """
        Convert a distance in screen pixels to world units.
        
        Args:
            screen_distance: Distance in screen pixels
            
        Returns:
            float: Distance in world units
        """
        return screen_distance / (self.tile_width * self.zoom)
    
    def resize_viewport(self, width, height):
        """
        Resize the viewport.
        
        Args:
            width: New width of the viewport in pixels
            height: New height of the viewport in pixels
            
        Returns:
            Camera: Self for method chaining
        """
        self.viewport_width = width
        self.viewport_height = height
        return self
    
    def set_isometric_projection(self, tile_width, tile_height, tile_depth):
        """
        Set the isometric projection parameters.
        
        Args:
            tile_width: Width of a tile in pixels at zoom=1.0
            tile_height: Height of a tile in pixels at zoom=1.0
            tile_depth: Depth (z) of a tile in pixels at zoom=1.0
            
        Returns:
            Camera: Self for method chaining
        """
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.tile_depth = tile_depth
        return self
    
    def get_zoom(self):
        """
        Get the current zoom level.
        
        Returns:
            float: Current zoom level
        """
        return self.zoom
    
    def get_rotation(self):
        """
        Get the current rotation in degrees.
        
        Returns:
            float: Current rotation in degrees
        """
        return self.rotation_degrees
    
    def get_position(self):
        """
        Get the current camera position in world space.
        
        Returns:
            tuple: (x, y) position in world space
        """
        return self.position
    
    def get_view_rect(self):
        """
        Get the world rectangle that is currently visible.
        
        Returns:
            tuple: (min_x, min_y, max_x, max_y) in world coordinates
        """
        top_left = self.screen_to_world(0, 0)
        bottom_right = self.screen_to_world(self.viewport_width, self.viewport_height)
        
        return (top_left[0], top_left[1], bottom_right[0], bottom_right[1])