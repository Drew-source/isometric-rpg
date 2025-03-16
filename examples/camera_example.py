"""
Camera system example for the isometric RPG.

This example demonstrates the camera system features, including coordinate transformation,
following entities, and viewport management.
"""

import time
import math
import random

from ..src.ecs.world import World
from ..src.ecs.entity import Entity
from ..src.events.event_manager import EventManager
from ..src.events.event_types import EventType
from ..src.components.transform import TransformComponent, Vector3
from ..src.camera.system import CameraSystem
from ..src.map.map import Map, TileType, CollisionType
from ..src.map.system import MapSystem


def create_player(world, position=(5, 5, 0)):
    """Create a player entity at the specified position."""
    player = Entity()
    transform = TransformComponent(Vector3(position[0], position[1], position[2]))
    player.add_component(transform)
    entity_id = world.add_entity(player)
    
    print(f"Created player entity {entity_id} at position {position}")
    return entity_id


def create_enemies(world, count=5, bounds=(0, 0, 20, 20)):
    """Create enemy entities at random positions within the specified bounds."""
    enemy_ids = []
    min_x, min_y, max_x, max_y = bounds
    
    for i in range(count):
        x = random.uniform(min_x, max_x)
        y = random.uniform(min_y, max_y)
        z = 0
        
        enemy = Entity()
        transform = TransformComponent(Vector3(x, y, z))
        enemy.add_component(transform)
        entity_id = world.add_entity(enemy)
        
        enemy_ids.append(entity_id)
        print(f"Created enemy entity {entity_id} at position ({x:.2f}, {y:.2f}, {z})")
    
    return enemy_ids


def print_entity_positions(world, entity_ids):
    """Print the positions of the specified entities."""
    print("\nEntity Positions:")
    for entity_id in entity_ids:
        entity = world.get_entity(entity_id)
        if entity:
            transform = entity.get_component(TransformComponent)
            if transform:
                pos = transform.position
                print(f"Entity {entity_id}: ({pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f})")


def print_camera_info(camera_system):
    """Print information about the camera."""
    camera = camera_system.get_camera()
    position = camera.get_position()
    zoom = camera.get_zoom()
    rotation = camera.get_rotation()
    
    print(f"\nCamera Info:")
    print(f"Position: ({position[0]:.2f}, {position[1]:.2f})")
    print(f"Zoom: {zoom:.2f}x")
    print(f"Rotation: {rotation:.2f} degrees")
    
    if camera_system.follow_entity_id is not None:
        print(f"Following entity: {camera_system.follow_entity_id}")
    else:
        print("Not following any entity")


def print_world_to_screen_mapping(camera_system, world_coords):
    """Print the mapping from world coordinates to screen coordinates."""
    print("\nWorld to Screen Coordinate Mapping:")
    for world_coord in world_coords:
        x, y, z = world_coord
        screen_coord = camera_system.world_to_screen(x, y, z)
        print(f"World ({x}, {y}, {z}) -> Screen ({screen_coord[0]:.2f}, {screen_coord[1]:.2f})")


def camera_movement_demo(camera_system):
    """Demonstrate camera movement."""
    print("\n--- Camera Movement Demo ---")
    
    # Move camera in different directions
    movements = [
        (2, 0, "right"),
        (0, 2, "down"),
        (-2, 0, "left"),
        (0, -2, "up"),
        (-0.5, -0.5, "diagonal")
    ]
    
    for dx, dy, direction in movements:
        print(f"\nMoving camera {direction} by ({dx}, {dy})")
        camera_system.move_camera(dx, dy)
        print_camera_info(camera_system)
        time.sleep(0.5)  # Pause to simulate animation
    
    # Reset camera position
    print("\nResetting camera position to (0, 0)")
    camera_system.set_camera_position(0, 0)
    print_camera_info(camera_system)


def camera_zoom_demo(camera_system):
    """Demonstrate camera zooming."""
    print("\n--- Camera Zoom Demo ---")
    
    # Zoom levels to demonstrate
    zoom_levels = [1.5, 2.0, 0.8, 0.5, 1.0]
    
    for zoom in zoom_levels:
        print(f"\nSetting zoom to {zoom}x")
        camera_system.set_camera_zoom(zoom)
        print_camera_info(camera_system)
        time.sleep(0.5)  # Pause to simulate animation


def camera_rotation_demo(camera_system):
    """Demonstrate camera rotation."""
    print("\n--- Camera Rotation Demo ---")
    
    # Rotation angles to demonstrate
    rotation_angles = [15, 30, 45, 90, 0]
    
    for angle in rotation_angles:
        print(f"\nSetting rotation to {angle} degrees")
        camera_system.set_camera_rotation(angle)
        print_camera_info(camera_system)
        time.sleep(0.5)  # Pause to simulate animation


def entity_following_demo(world, camera_system, entity_ids):
    """Demonstrate the camera following an entity."""
    print("\n--- Entity Following Demo ---")
    
    player_id = entity_ids[0]
    print(f"\nSetting camera to follow player (Entity {player_id})")
    camera_system.set_follow_entity(player_id)
    print_camera_info(camera_system)
    
    # Move the player around to demonstrate following
    moves = [
        (1, 0, 0, "right"),
        (0, 1, 0, "down"),
        (-1, 0, 0, "left"),
        (0, -1, 0, "up")
    ]
    
    player = world.get_entity(player_id)
    transform = player.get_component(TransformComponent)
    
    for dx, dy, dz, direction in moves:
        print(f"\nMoving player {direction}")
        transform.position.x += dx
        transform.position.y += dy
        transform.position.z += dz
        
        # Manually trigger an event since we're not using a movement system
        world.event_manager.emit(EventType.ENTITY_MOVED, {
            "entity_id": player_id,
            "old_position": (transform.position.x - dx, transform.position.y - dy, transform.position.z - dz),
            "new_position": (transform.position.x, transform.position.y, transform.position.z)
        })
        
        # Update the camera to follow
        camera_system.update(0.1)
        
        print_entity_positions(world, [player_id])
        print_camera_info(camera_system)
        time.sleep(0.5)  # Pause to simulate animation
    
    # Stop following
    print("\nStopping camera from following player")
    camera_system.stop_following()
    print_camera_info(camera_system)


def visible_entities_demo(world, camera_system, entity_ids):
    """Demonstrate culling of entities outside the viewport."""
    print("\n--- Visible Entities Demo ---")
    
    # Position camera at the center
    camera_system.set_camera_position(10, 10)
    
    # Test different zoom levels to show how visibility changes
    zoom_levels = [2.0, 1.0, 0.5]
    
    for zoom in zoom_levels:
        camera_system.set_camera_zoom(zoom)
        visible_entities = camera_system.get_visible_entities()
        
        print(f"\nZoom level: {zoom}x")
        print(f"Visible entities: {len(visible_entities)}/{len(entity_ids)}")
        print(f"Entity IDs: {visible_entities}")
        
        # Print which entities are visible
        print("Visible entity positions:")
        for entity_id in visible_entities:
            entity = world.get_entity(entity_id)
            transform = entity.get_component(TransformComponent)
            pos = transform.position
            print(f"Entity {entity_id}: ({pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f})")
        
        time.sleep(0.5)  # Pause to simulate animation


def viewport_tiles_demo(camera_system, game_map):
    """Demonstrate getting visible tiles in the viewport."""
    print("\n--- Visible Tiles Demo ---")
    
    # Position camera at different points to see different visible tiles
    positions = [(5, 5), (0, 0), (15, 15), (10, 10)]
    
    for pos in positions:
        camera_system.set_camera_position(pos[0], pos[1])
        visible_tiles = camera_system.get_visible_tiles(game_map.width, game_map.height)
        
        print(f"\nCamera position: ({pos[0]}, {pos[1]})")
        print(f"Visible tiles: ({visible_tiles[0]}, {visible_tiles[1]}) to ({visible_tiles[2]}, {visible_tiles[3]})")
        print(f"Total visible tiles: {(visible_tiles[2] - visible_tiles[0] + 1) * (visible_tiles[3] - visible_tiles[1] + 1)}")
        
        time.sleep(0.5)  # Pause to simulate animation


def create_test_map(map_system, width=20, height=20):
    """Create a test map for the example."""
    # Create a new map
    game_map = Map(width, height)
    
    # Set some walls and different tile types for visualization
    for x in range(width):
        for y in range(height):
            # Create border walls
            if x == 0 or y == 0 or x == width - 1 or y == height - 1:
                game_map.set_tile(x, y, TileType.WALL, CollisionType.BLOCKED)
            # Create some internal structures
            elif (x > 5 and x < 10 and y == 5) or (x == 15 and y > 5 and y < 15):
                game_map.set_tile(x, y, TileType.WALL, CollisionType.BLOCKED)
            # Create some water areas
            elif (x > 2 and x < 6 and y > 12 and y < 18):
                game_map.set_tile(x, y, TileType.WATER, CollisionType.DIFFICULT)
            # Create some high ground areas
            elif (x > 10 and x < 15 and y > 2 and y < 7):
                game_map.set_tile(x, y, TileType.HIGH_GROUND, CollisionType.NORMAL)
            else:
                game_map.set_tile(x, y, TileType.FLOOR, CollisionType.NORMAL)
    
    # Register the map with the map system
    map_system.set_current_map(game_map)
    
    return game_map


def main():
    """Run the camera example."""
    # Initialize the world and systems
    event_manager = EventManager()
    world = World(event_manager)
    
    # Set up viewport size (simulating a window)
    viewport_width, viewport_height = 800, 600
    
    # Create camera system
    camera_system = CameraSystem(world, event_manager, viewport_width, viewport_height)
    
    # Create map system
    map_system = MapSystem(world, event_manager)
    
    # Create a test map
    game_map = create_test_map(map_system)
    
    # Create entities
    player_id = create_player(world)
    enemy_ids = create_enemies(world, count=10)
    all_entity_ids = [player_id] + enemy_ids
    
    # Print initial state
    print_entity_positions(world, all_entity_ids)
    print_camera_info(camera_system)
    
    # Test world-to-screen and screen-to-world coordinate conversions
    world_coords = [(5, 5, 0), (10, 10, 0), (0, 0, 0), (15, 7, 1)]
    print_world_to_screen_mapping(camera_system, world_coords)
    
    # Demonstrate camera features
    camera_movement_demo(camera_system)
    camera_zoom_demo(camera_system)
    camera_rotation_demo(camera_system)
    entity_following_demo(world, camera_system, all_entity_ids)
    visible_entities_demo(world, camera_system, all_entity_ids)
    viewport_tiles_demo(camera_system, game_map)
    
    print("\n--- Camera Example Complete ---")


if __name__ == "__main__":
    main()