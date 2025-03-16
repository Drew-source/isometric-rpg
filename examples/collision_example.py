"""
Collision system example for the isometric RPG.

This example demonstrates the collision system features, including collision detection,
resolution, and ray casting.
"""

import time
import math
import random

from ..src.ecs.world import World
from ..src.ecs.entity import Entity
from ..src.events.event_manager import EventManager
from ..src.events.event_types import EventType
from ..src.components.transform import TransformComponent, Vector3
from ..src.collision.collision import (
    CollisionComponent,
    CircleShape,
    RectangleShape,
    PointShape,
    CollisionShapeType,
    CollisionLayer
)
from ..src.collision.system import CollisionSystem
from ..src.map.map import Map, TileType, CollisionType
from ..src.map.system import MapSystem


def create_player(world, position=(5, 5, 0)):
    """Create a player entity with a circle collision shape."""
    player = Entity()
    
    # Add transform component
    transform = TransformComponent(Vector3(position[0], position[1], position[2]))
    player.add_component(transform)
    
    # Add collision component with a circle shape
    collision_shape = CircleShape(0.4, CollisionLayer.PLAYER)
    collision = CollisionComponent(collision_shape, static=False, layer=CollisionLayer.PLAYER)
    player.add_component(collision)
    
    entity_id = world.add_entity(player)
    print(f"Created player entity {entity_id} at position {position} with circle shape")
    return entity_id


def create_wall(world, position, size=(1, 1)):
    """Create a wall entity with a rectangle collision shape."""
    wall = Entity()
    
    # Add transform component
    transform = TransformComponent(Vector3(position[0], position[1], 0))
    wall.add_component(transform)
    
    # Add collision component with a rectangle shape
    collision_shape = RectangleShape(size[0], size[1], CollisionLayer.TERRAIN)
    collision = CollisionComponent(collision_shape, static=True, layer=CollisionLayer.TERRAIN)
    wall.add_component(collision)
    
    entity_id = world.add_entity(wall)
    print(f"Created wall entity {entity_id} at position {position} with size {size}")
    return entity_id


def create_trigger(world, position, radius=0.5):
    """Create a trigger entity with a circle collision shape."""
    trigger = Entity()
    
    # Add transform component
    transform = TransformComponent(Vector3(position[0], position[1], 0))
    trigger.add_component(transform)
    
    # Add collision component with a circle shape as a trigger
    collision_shape = CircleShape(radius, CollisionLayer.TRIGGER)
    collision = CollisionComponent(collision_shape, static=True, trigger=True, layer=CollisionLayer.TRIGGER)
    trigger.add_component(collision)
    
    entity_id = world.add_entity(trigger)
    print(f"Created trigger entity {entity_id} at position {position} with radius {radius}")
    return entity_id


def create_enemy(world, position, radius=0.3):
    """Create an enemy entity with a circle collision shape."""
    enemy = Entity()
    
    # Add transform component
    transform = TransformComponent(Vector3(position[0], position[1], 0))
    enemy.add_component(transform)
    
    # Add collision component with a circle shape
    collision_shape = CircleShape(radius, CollisionLayer.ENEMY)
    collision = CollisionComponent(collision_shape, static=False, layer=CollisionLayer.ENEMY)
    enemy.add_component(collision)
    
    entity_id = world.add_entity(enemy)
    print(f"Created enemy entity {entity_id} at position {position} with radius {radius}")
    return entity_id


def print_entity_position(world, entity_id):
    """Print the position of an entity."""
    entity = world.get_entity(entity_id)
    if entity:
        transform = entity.get_component(TransformComponent)
        if transform:
            pos = transform.position
            print(f"Entity {entity_id} position: ({pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f})")


def move_entity(world, entity_id, dx, dy):
    """Move an entity by the specified delta."""
    entity = world.get_entity(entity_id)
    if entity:
        transform = entity.get_component(TransformComponent)
        if transform:
            old_pos = (transform.position.x, transform.position.y, transform.position.z)
            transform.position.x += dx
            transform.position.y += dy
            new_pos = (transform.position.x, transform.position.y, transform.position.z)
            
            # Emit entity moved event
            world.event_manager.emit(EventType.ENTITY_MOVED, {
                "entity_id": entity_id,
                "old_position": old_pos,
                "new_position": new_pos
            })
            
            print(f"Moved entity {entity_id} by ({dx}, {dy})")
            print_entity_position(world, entity_id)


def collision_event_handler(event_data):
    """Handle collision events."""
    entity_id = event_data.get("entity_id")
    collision_type = event_data.get("collision_type")
    is_trigger = event_data.get("is_trigger", False)
    
    if collision_type == "ENTITY":
        other_entity_id = event_data.get("other_entity_id")
        if is_trigger:
            print(f"Entity {entity_id} triggered entity {other_entity_id}")
        else:
            print(f"Entity {entity_id} collided with entity {other_entity_id}")
    elif collision_type == "MAP":
        tile_x = event_data.get("tile_x")
        tile_y = event_data.get("tile_y")
        tile_type = event_data.get("tile_type")
        if is_trigger:
            print(f"Entity {entity_id} triggered map tile ({tile_x}, {tile_y}) of type {tile_type}")
        else:
            print(f"Entity {entity_id} collided with map tile ({tile_x}, {tile_y}) of type {tile_type}")


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


def ray_cast_demo(collision_system, start_pos, directions):
    """Demonstrate ray casting."""
    print("\n--- Ray Casting Demo ---")
    
    max_distance = 10.0
    
    for direction in directions:
        # Normalize direction
        length = math.sqrt(direction[0]**2 + direction[1]**2)
        if length > 0:
            normalized_dir = (direction[0] / length, direction[1] / length)
        else:
            normalized_dir = (0, 1)  # Default direction
        
        # Perform ray cast
        hit, hit_pos, hit_normal, hit_entity_id, hit_distance = collision_system.check_ray_collision(
            start_pos, normalized_dir, max_distance
        )
        
        # Print results
        print(f"\nRay from {start_pos} in direction {normalized_dir}:")
        if hit:
            print(f"  Hit at position {hit_pos} with normal {hit_normal}")
            print(f"  Distance: {hit_distance:.2f}")
            if hit_entity_id is not None:
                print(f"  Hit entity: {hit_entity_id}")
            else:
                print("  Hit map tile")
        else:
            print("  No hit within max distance")


def entity_collision_demo(world, collision_system, player_id, entity_ids):
    """Demonstrate entity-entity collisions."""
    print("\n--- Entity Collision Demo ---")
    
    # Move player towards each entity
    player = world.get_entity(player_id)
    player_transform = player.get_component(TransformComponent)
    player_pos = (player_transform.position.x, player_transform.position.y)
    
    for entity_id in entity_ids:
        entity = world.get_entity(entity_id)
        if not entity:
            continue
            
        transform = entity.get_component(TransformComponent)
        if not transform:
            continue
            
        entity_pos = (transform.position.x, transform.position.y)
        
        # Calculate direction from player to entity
        dx = entity_pos[0] - player_pos[0]
        dy = entity_pos[1] - player_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # Normalize and scale
            dx = dx / distance * 0.5
            dy = dy / distance * 0.5
            
            print(f"\nMoving player towards entity {entity_id}")
            print(f"  Player position before: ({player_transform.position.x:.2f}, {player_transform.position.y:.2f})")
            print(f"  Entity position: ({transform.position.x:.2f}, {transform.position.y:.2f})")
            
            # Move player towards entity
            move_entity(world, player_id, dx, dy)
            
            # Update collision system
            collision_system.update(0.1)
            
            print(f"  Player position after: ({player_transform.position.x:.2f}, {player_transform.position.y:.2f})")
            
            # Check if collision occurred
            collision = player.get_component(CollisionComponent)
            if entity_id in collision.colliding_entities:
                print(f"  Collision detected with entity {entity_id}")
            else:
                print(f"  No collision with entity {entity_id}")
            
            # Move player back to original position
            move_entity(world, player_id, -dx, -dy)
            collision_system.update(0.1)


def map_collision_demo(world, collision_system, map_system, player_id):
    """Demonstrate entity-map collisions."""
    print("\n--- Map Collision Demo ---")
    
    game_map = map_system.get_current_map()
    if not game_map:
        print("No map available")
        return
    
    # Find some blocked tiles to test
    blocked_tiles = []
    for x in range(game_map.width):
        for y in range(game_map.height):
            tile = game_map.get_tile(x, y)
            if tile.collision_type == CollisionType.BLOCKED:
                blocked_tiles.append((x, y))
                if len(blocked_tiles) >= 3:
                    break
        if len(blocked_tiles) >= 3:
            break
    
    player = world.get_entity(player_id)
    player_transform = player.get_component(TransformComponent)
    original_pos = (player_transform.position.x, player_transform.position.y)
    
    for tile_pos in blocked_tiles:
        # Position player near the tile
        target_x = tile_pos[0] + 0.5  # Center of tile
        target_y = tile_pos[1] + 0.5  # Center of tile
        
        # Calculate direction from player to tile
        dx = target_x - original_pos[0]
        dy = target_y - original_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # Normalize and scale
            dx = dx / distance * (distance - 1.0)  # Position player 1 unit away from tile
            dy = dy / distance * (distance - 1.0)
            
            # Move player to position near tile
            player_transform.position.x = original_pos[0] + dx
            player_transform.position.y = original_pos[1] + dy
            
            print(f"\nTesting collision with map tile at ({tile_pos[0]}, {tile_pos[1]})")
            print(f"  Player position: ({player_transform.position.x:.2f}, {player_transform.position.y:.2f})")
            
            # Move player towards tile
            direction_x = (target_x - player_transform.position.x) * 0.8
            direction_y = (target_y - player_transform.position.y) * 0.8
            
            move_entity(world, player_id, direction_x, direction_y)
            
            # Update collision system
            collision_system.update(0.1)
            
            print(f"  Player position after move: ({player_transform.position.x:.2f}, {player_transform.position.y:.2f})")
            
            # Check if player reached the target (collision prevented movement)
            current_x = player_transform.position.x
            current_y = player_transform.position.y
            actual_dx = current_x - (original_pos[0] + dx)
            actual_dy = current_y - (original_pos[1] + dy)
            actual_distance = math.sqrt(actual_dx*actual_dx + actual_dy*actual_dy)
            
            if actual_distance < 0.9 * math.sqrt(direction_x*direction_x + direction_y*direction_y):
                print("  Collision detected with map tile (movement was limited)")
            else:
                print("  No collision with map tile")
    
    # Reset player position
    player_transform.position.x = original_pos[0]
    player_transform.position.y = original_pos[1]
    collision_system.update(0.1)


def main():
    """Run the collision example."""
    # Initialize the world and systems
    event_manager = EventManager()
    world = World(event_manager)
    
    # Create systems
    collision_system = CollisionSystem(world, event_manager)
    map_system = MapSystem(world, event_manager)
    
    # Connect systems
    collision_system.set_map_system(map_system)
    
    # Subscribe to collision events
    event_manager.subscribe(EventType.COLLISION_OCCURRED, collision_event_handler)
    
    # Create a test map
    game_map = create_test_map(map_system)
    
    # Create entities
    player_id = create_player(world, (5, 5, 0))
    
    wall_ids = [
        create_wall(world, (8, 8), (2, 1)),
        create_wall(world, (12, 4), (1, 3)),
        create_wall(world, (3, 10), (1, 1))
    ]
    
    trigger_ids = [
        create_trigger(world, (7, 3), 0.5),
        create_trigger(world, (10, 10), 0.7)
    ]
    
    # Demonstrate ray casting
    ray_cast_demo(
        collision_system,
        (5, 5),
        [
            (1, 0),    # East
            (0, 1),    # South
            (-1, 0),   # West
            (0, -1),   # North
            (1, 1),    # Southeast
            (-1, 1),   # Southwest
            (-1, -1),  # Northwest
            (1, -1)    # Northeast
        ]
    )
    
    # Demonstrate entity-entity collisions
    entity_collision_demo(world, collision_system, player_id, wall_ids + trigger_ids)
    
    # Demonstrate entity-map collisions
    map_collision_demo(world, collision_system, map_system, player_id)
    
    print("\n--- Collision Example Complete ---")


if __name__ == "__main__":
    main()