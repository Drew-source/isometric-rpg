"""
Camera system for the isometric RPG.

This module provides the CameraSystem class that integrates the camera
with the Entity Component System (ECS) architecture.
"""

from ..ecs.system import System
from ..components.transform import TransformComponent
from ..events.event_types import EventType
from .camera import Camera


class CameraSystem(System):
    """
    System for managing the camera in the game world.
    
    This system handles camera movement, following entities, and culling
    entities outside the viewport for rendering optimization.
    """
    
    def __init__(self, world, event_manager, viewport_width, viewport_height):
        """
        Initialize the camera system.
        
        Args:
            world: The game world
            event_manager: The event manager
            viewport_width: Width of the viewport in pixels
            viewport_height: Height of the viewport in pixels
        """
        super().__init__(world, event_manager)
        self.camera = Camera(viewport_width, viewport_height)
        
        # Entity that the camera is following
        self.follow_entity_id = None
        self.follow_offset = (0, 0)  # Offset when following an entity
        
        # Camera movement speed
        self.move_speed = 10.0  # World units per second
        self.zoom_speed = 0.1   # Zoom factor per second
        self.rotation_speed = 45.0  # Degrees per second
        
        # Subscribe to relevant events
        self.event_manager.subscribe(EventType.WINDOW_RESIZED, self._on_window_resized)
        self.event_manager.subscribe(EventType.ENTITY_SPAWNED, self._on_entity_spawned)
        self.event_manager.subscribe(EventType.ENTITY_DIED, self._on_entity_died)
    
    def _on_window_resized(self, event_data):
        """Handle window resize events."""
        width = event_data.get("width", self.camera.viewport_width)
        height = event_data.get("height", self.camera.viewport_height)
        self.camera.resize_viewport(width, height)
    
    def _on_entity_spawned(self, event_data):
        """
        Handle entity spawn events.
        
        This could be used to focus the camera on newly spawned important entities.
        """
        entity_id = event_data.get("entity_id")
        entity_type = event_data.get("entity_type")
        
        # If it's the player entity and we're not following anything yet,
        # start following it automatically
        if entity_type == "player" and self.follow_entity_id is None:
            self.set_follow_entity(entity_id)
    
    def _on_entity_died(self, event_data):
        """
        Handle entity death events.
        
        If we're following an entity that died, stop following it.
        """
        entity_id = event_data.get("entity_id")
        if entity_id == self.follow_entity_id:
            self.stop_following()
    
    def update(self, delta_time):
        """
        Update the camera system.
        
        Args:
            delta_time: Time elapsed since the last update in seconds
        """
        # Update camera position if following an entity
        if self.follow_entity_id is not None:
            entity = self.world.get_entity(self.follow_entity_id)
            if entity:
                transform = entity.get_component(TransformComponent)
                if transform:
                    # Set camera position to entity position plus offset
                    self.camera.set_position(
                        transform.position.x + self.follow_offset[0],
                        transform.position.y + self.follow_offset[1]
                    )
    
    def set_follow_entity(self, entity_id, offset=(0, 0)):
        """
        Set the camera to follow an entity.
        
        Args:
            entity_id: ID of the entity to follow
            offset: (x, y) offset from the entity position
        """
        self.follow_entity_id = entity_id
        self.follow_offset = offset
        
        # Immediately update camera position
        entity = self.world.get_entity(entity_id)
        if entity:
            transform = entity.get_component(TransformComponent)
            if transform:
                self.camera.set_position(
                    transform.position.x + offset[0],
                    transform.position.y + offset[1]
                )
    
    def stop_following(self):
        """Stop the camera from following an entity."""
        self.follow_entity_id = None
    
    def move_camera(self, dx, dy):
        """
        Move the camera by the specified delta.
        
        Args:
            dx: Change in X coordinate
            dy: Change in Y coordinate
        """
        self.camera.move(dx, dy)
        
        # If we move the camera manually, stop following
        if self.follow_entity_id is not None and (dx != 0 or dy != 0):
            self.stop_following()
    
    def set_camera_position(self, x, y):
        """
        Set the camera position.
        
        Args:
            x: X coordinate in world space
            y: Y coordinate in world space
        """
        self.camera.set_position(x, y)
        
        # If we set camera position manually, stop following
        if self.follow_entity_id is not None:
            self.stop_following()
    
    def zoom_camera(self, delta_zoom):
        """
        Zoom the camera by the specified delta.
        
        Args:
            delta_zoom: Change in zoom level (positive = zoom in, negative = zoom out)
        """
        current_zoom = self.camera.get_zoom()
        if delta_zoom > 0:
            self.camera.zoom_in(1.0 + delta_zoom)
        elif delta_zoom < 0:
            self.camera.zoom_out(1.0 - delta_zoom)
    
    def set_camera_zoom(self, zoom):
        """
        Set the camera zoom level.
        
        Args:
            zoom: Zoom level (1.0 = 100%)
        """
        self.camera.set_zoom(zoom)
    
    def rotate_camera(self, delta_degrees):
        """
        Rotate the camera by the specified delta.
        
        Args:
            delta_degrees: Change in rotation in degrees
        """
        self.camera.rotate(delta_degrees)
    
    def set_camera_rotation(self, degrees):
        """
        Set the camera rotation.
        
        Args:
            degrees: Rotation in degrees
        """
        self.camera.set_rotation(degrees)
    
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
        return self.camera.world_to_screen(world_x, world_y, world_z)
    
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
        return self.camera.screen_to_world(screen_x, screen_y, world_z)
    
    def get_visible_entities(self):
        """
        Get a list of entities that are visible in the current viewport.
        
        This is used for optimization to avoid processing entities that
        aren't visible.
        
        Returns:
            list: List of entity IDs that are visible in the viewport
        """
        visible_entities = []
        
        # Get all entities with a TransformComponent
        entities = self.world.get_entities_with_component(TransformComponent)
        
        for entity_id in entities:
            entity = self.world.get_entity(entity_id)
            if not entity:
                continue
                
            transform = entity.get_component(TransformComponent)
            if not transform:
                continue
            
            # Check if the entity is visible in the viewport
            # For simplicity, we assume all entities are 1 world unit in radius
            if self.camera.is_visible(
                transform.position.x,
                transform.position.y,
                transform.position.z,
                1.0  # Default radius
            ):
                visible_entities.append(entity_id)
        
        return visible_entities
    
    def get_visible_tiles(self, map_width, map_height):
        """
        Get the range of map tiles that are visible in the viewport.
        
        Args:
            map_width: Width of the map in tiles
            map_height: Height of the map in tiles
            
        Returns:
            tuple: (min_x, min_y, max_x, max_y) bounds of visible tiles
        """
        return self.camera.get_visible_tiles(map_width, map_height)
    
    def get_camera(self):
        """
        Get the camera object.
        
        Returns:
            Camera: The camera object
        """
        return self.camera