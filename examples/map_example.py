"""
Example demonstrating the map system.

This example creates a map, adds tiles and entity spawns, saves it to a file,
and then loads it back, spawning entities and demonstrating pathfinding.
"""

import sys
import os
import time
import random
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.ecs.world import World
from src.ecs.entity import Entity
from src.events.event_manager import EventManager
from src.events.event_types import EventType
from src.components.transform import TransformComponent
from src.map.map import Map, Tile, TileType, CollisionType
from src.map.system import MapSystem


def create_entity_at_position(world, position):
    """Create an entity at the specified position."""
    entity = world.create_entity()
    
    # Add transform component
    transform = TransformComponent()
    transform.set_position(position[0], position[1])
    world.add_component(entity, transform)
    
    return entity


def print_entity_position(world, entity_id):
    """Print the position of an entity."""
    transform = world.get_component(entity_id, TransformComponent)
    if transform:
        print(f"Entity {entity_id} position: ({transform.position.x}, {transform.position.y})")
    else:
        print(f"Entity {entity_id} has no transform component")


def move_entity(world, event_manager, entity_id, new_x, new_y):
    """Move an entity to a new position."""
    transform = world.get_component(entity_id, TransformComponent)
    if transform:
        old_x, old_y = transform.position.x, transform.position.y
        transform.set_position(new_x, new_y)
        
        # Emit entity moved event
        entity = world.entities[entity_id]
        event_manager.emit(EventType.ENTITY_MOVED, {
            "entity": entity,
            "old_position": (old_x, old_y),
            "new_position": (new_x, new_y)
        })
        
        print(f"Moved entity {entity_id} from ({old_x}, {old_y}) to ({new_x}, {new_y})")
    else:
        print(f"Entity {entity_id} has no transform component, cannot move")


def create_test_map(map_system, width=20, height=20):
    """Create a test map with walls, floors, and some special tiles."""
    # Create the map
    game_map = map_system.create_map(width, height, TileType.FLOOR, "test_map")
    
    # Add walls around the perimeter
    for x in range(width):
        game_map.set_tile_type(x, 0, TileType.WALL)
        game_map.set_collision_type(x, 0, CollisionType.BLOCK)
        
        game_map.set_tile_type(x, height - 1, TileType.WALL)
        game_map.set_collision_type(x, height - 1, CollisionType.BLOCK)
    
    for y in range(height):
        game_map.set_tile_type(0, y, TileType.WALL)
        game_map.set_collision_type(0, y, CollisionType.BLOCK)
        
        game_map.set_tile_type(width - 1, y, TileType.WALL)
        game_map.set_collision_type(width - 1, y, CollisionType.BLOCK)
    
    # Add some interior walls to make it interesting
    for x in range(5, 15):
        game_map.set_tile_type(x, 5, TileType.WALL)
        game_map.set_collision_type(x, 5, CollisionType.BLOCK)
    
    for y in range(10, 15):
        game_map.set_tile_type(10, y, TileType.WALL)
        game_map.set_collision_type(10, y, CollisionType.BLOCK)
    
    # Add some water
    game_map.fill_rect(2, 2, 4, 4, TileType.WATER, CollisionType.SLOW)
    
    # Add some lava
    game_map.fill_rect(width - 5, height - 5, width - 2, height - 2, TileType.LAVA, CollisionType.DAMAGE)
    
    # Add some entity spawn points
    game_map.add_entity_spawn("player", 5, 5, {"name": "Player", "health": 100})
    game_map.add_entity_spawn("enemy", 15, 15, {"name": "Enemy", "health": 50})
    
    return game_map


def print_map(game_map):
    """Print a simple ASCII representation of the map."""
    # Define ASCII characters for different tile types
    tile_chars = {
        TileType.EMPTY: ' ',
        TileType.FLOOR: '.',
        TileType.WALL: '#',
        TileType.DOOR: '+',
        TileType.WATER: '~',
        TileType.LAVA: '^',
        TileType.GRASS: '"',
        TileType.DIRT: ',',
        TileType.STONE: ':',
        TileType.WOOD: '=',
        TileType.CUSTOM: '?'
    }
    
    print(f"\n=== Map: {game_map.name} ({game_map.width}x{game_map.height}) ===")
    
    for y in range(game_map.height - 1, -1, -1):  # Print from top to bottom
        row = ""
        for x in range(game_map.width):
            tile = game_map.get_tile(x, y)
            if tile:
                row += tile_chars.get(tile.tile_type, '?')
            else:
                row += ' '
        print(row)


def spawn_entity_handler(world, event_data):
    """Handle entity spawn events."""
    entity = event_data.get("entity")
    x = event_data.get("x", 0)
    y = event_data.get("y", 0)
    properties = event_data.get("properties", {})
    
    print(f"Entity spawned: {entity.id} at ({x}, {y}) with properties: {properties}")


def entity_spawner(world, entity_type):
    """Create a spawner function for a specific entity type."""
    def spawner(x, y, properties):
        entity = world.create_entity()
        
        # Add transform component
        transform = TransformComponent()
        transform.set_position(x, y)
        world.add_component(entity, transform)
        
        # Additional processing based on entity type and properties could go here
        print(f"Spawned {entity_type} entity {entity} at ({x}, {y}) with properties: {properties}")
        
        return entity
    
    return spawner


def test_pathfinding(map_system, start_x, start_y, end_x, end_y):
    """Test pathfinding between two points."""
    print(f"\n=== Testing pathfinding from ({start_x}, {start_y}) to ({end_x}, {end_y}) ===")
    
    path = map_system.find_path(start_x, start_y, end_x, end_y)
    
    if path:
        print(f"Path found with {len(path)} steps:")
        for i, (x, y) in enumerate(path):
            print(f"  Step {i+1}: ({x}, {y})")
    else:
        print("No path found")


def test_line_of_sight(map_system, start_x, start_y, end_x, end_y):
    """Test line of sight between two points."""
    print(f"\n=== Testing line of sight from ({start_x}, {start_y}) to ({end_x}, {end_y}) ===")
    
    has_los = map_system.check_line_of_sight(start_x, start_y, end_x, end_y)
    
    if has_los:
        print("Line of sight is clear")
    else:
        print("Line of sight is blocked")


def main():
    """Main function to run the example."""
    # Create event manager
    event_manager = EventManager()
    
    # Subscribe to entity spawn events
    event_manager.subscribe(EventType.ENTITY_SPAWNED, 
                           lambda data: spawn_entity_handler(None, data))
    
    # Create world
    world = World(event_manager)
    
    # Create map system
    map_system = MapSystem(world, event_manager)
    
    # Set maps directory
    map_dir = "maps"
    os.makedirs(map_dir, exist_ok=True)
    map_system.set_maps_directory(map_dir)
    
    # Register entity spawners
    map_system.register_entity_spawner("player", entity_spawner(world, "player"))
    map_system.register_entity_spawner("enemy", entity_spawner(world, "enemy"))
    
    # Create a test map
    game_map = create_test_map(map_system)
    
    # Print the map
    print_map(game_map)
    
    # Save the map
    success = map_system.save_current_map()
    print(f"\nMap saved: {success}")
    
    # Clear the world
    world.clear()
    
    # Load the map back
    loaded_map = map_system.load_map("test_map", spawn_entities=True)
    
    if loaded_map:
        print("\nMap loaded successfully")
        print_map(loaded_map)
    else:
        print("\nFailed to load map")
        return
    
    # Test pathfinding
    test_pathfinding(map_system, 5, 5, 15, 15)
    test_pathfinding(map_system, 1, 1, 18, 18)
    
    # Test line of sight
    test_line_of_sight(map_system, 5, 5, 15, 15)
    test_line_of_sight(map_system, 5, 5, 5, 15)
    
    # Create a player entity manually
    player = create_entity_at_position(world, (5, 5))
    print(f"\nCreated player entity: {player}")
    
    # Try to move the player to different locations
    print("\n=== Testing movement and collision ===")
    
    # This should succeed (floor tile)
    move_entity(world, event_manager, player, 6, 6)
    
    # This should fail (wall tile)
    move_entity(world, event_manager, player, 10, 10)
    
    # Check final position
    print("\nFinal player position:")
    print_entity_position(world, player)


if __name__ == "__main__":
    main() 