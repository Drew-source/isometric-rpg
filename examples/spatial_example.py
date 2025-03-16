"""
Example demonstrating the spatial grid and system.

This example creates a world with multiple entities positioned in different locations
and shows how to use the spatial system to efficiently query for entities based on
spatial relationships.
"""

import sys
import time
import random
import math
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.ecs.world import World
from src.ecs.entity import Entity
from src.events.event_manager import EventManager
from src.events.event_types import EventType
from src.components.transform import TransformComponent
from src.spatial.system import SpatialSystem


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


def test_spatial_queries(world, spatial_system):
    """Test various spatial queries."""
    # Test query by range
    print("\n=== Entities within range 5.0 of (10, 10) ===")
    entities_in_range = spatial_system.get_entities_in_range(10, 10, 5.0)
    for entity_id in entities_in_range:
        print_entity_position(world, entity_id)
    
    # Test query by rectangle
    print("\n=== Entities within rectangle (5,5) to (15,15) ===")
    entities_in_rect = spatial_system.get_entities_in_rect(5, 5, 15, 15)
    for entity_id in entities_in_rect:
        print_entity_position(world, entity_id)
    
    # Test nearest entity query
    print("\n=== Nearest entity to (10, 10) ===")
    nearest_entity, distance = spatial_system.get_nearest_entity(10, 10)
    if nearest_entity is not None:
        print(f"Nearest entity: {nearest_entity}, distance: {distance}")
        print_entity_position(world, nearest_entity)
    else:
        print("No entity found")
    
    # Test ray query
    print("\n=== Entities along ray from (0, 0) to (20, 20) ===")
    entities_along_ray = spatial_system.get_entities_along_ray(0, 0, 20, 20)
    for entity_id, distance in entities_along_ray:
        print(f"Entity {entity_id} at distance {distance}")
        print_entity_position(world, entity_id)


def main():
    """Main function to run the example."""
    # Create event manager
    event_manager = EventManager()
    
    # Create world
    world = World(event_manager)
    
    # Create spatial system
    spatial_system = SpatialSystem(world, event_manager, cell_size=5.0)
    
    # Log when entities move
    event_manager.subscribe(EventType.ENTITY_MOVED, 
                           lambda data: print(f"Entity moved event received: {data['entity'].id}"))
    
    # Create a grid of entities
    entities = []
    for x in range(0, 25, 5):
        for y in range(0, 25, 5):
            entity = create_entity_at_position(world, (x, y))
            entities.append(entity)
            print(f"Created entity {entity} at ({x}, {y})")
    
    # Update spatial system
    spatial_system.update(0.0)
    
    # Print grid stats
    print("\n=== Spatial Grid Stats ===")
    stats = spatial_system.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Test spatial queries
    test_spatial_queries(world, spatial_system)
    
    # Move some entities
    print("\n=== Moving entities ===")
    move_entity(world, event_manager, entities[0], 10, 10)
    move_entity(world, event_manager, entities[1], 12, 8)
    move_entity(world, event_manager, entities[2], 9, 12)
    
    # Update spatial system again
    spatial_system.update(0.0)
    
    # Test spatial queries again after movement
    print("\n=== After movement ===")
    test_spatial_queries(world, spatial_system)
    
    # Test removing an entity
    print("\n=== Removing entity ===")
    entity_to_remove = entities[0]
    print(f"Removing entity {entity_to_remove}")
    world.destroy_entity(entity_to_remove)
    
    # Update spatial system
    spatial_system.update(0.0)
    
    # Test spatial queries after removal
    print("\n=== After removal ===")
    test_spatial_queries(world, spatial_system)


if __name__ == "__main__":
    main() 