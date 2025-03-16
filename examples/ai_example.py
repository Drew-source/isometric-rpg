"""
Example demonstrating the AI system with character stats and transform components.

This example creates a simple scene with an AI-controlled NPC and a player character,
showing how the AI makes decisions based on character stats and positions.
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
from src.components import AIComponent, CharacterStatsComponent, TransformComponent
from src.systems.ai_system import AISystem

def create_player(world, position):
    """Create a player entity."""
    player = world.create_entity()
    
    # Add transform component
    transform = TransformComponent()
    transform.set_position(position)
    world.add_component(player, transform)
    
    # Add character stats component
    stats = CharacterStatsComponent()
    # Customize player stats
    stats.base_stats["strength"] = 15
    stats.base_stats["dexterity"] = 14
    stats.base_stats["constitution"] = 16
    stats.base_stats["max_health"] = 150
    stats.base_stats["attack_power"] = 20
    stats.health = stats.base_stats["max_health"]  # Full health
    stats._apply_modifiers()  # Update current stats
    world.add_component(player, stats)
    
    return player

def create_enemy(world, position, personality=None):
    """Create an enemy entity with AI."""
    enemy = world.create_entity()
    
    # Add transform component
    transform = TransformComponent()
    transform.set_position(position)
    world.add_component(enemy, transform)
    
    # Add character stats component
    stats = CharacterStatsComponent()
    # Customize enemy stats
    stats.base_stats["strength"] = 12
    stats.base_stats["dexterity"] = 13
    stats.base_stats["constitution"] = 14
    stats.base_stats["max_health"] = 100
    stats.base_stats["attack_power"] = 15
    stats.health = stats.base_stats["max_health"]  # Full health
    stats._apply_modifiers()  # Update current stats
    world.add_component(enemy, stats)
    
    # Add AI component
    ai = AIComponent(ai_type="utility")
    
    # Set personality if provided
    if personality:
        for trait, value in personality.items():
            ai.set_personality(trait, value)
    else:
        # Randomize personality
        ai.randomize_personality(variance=0.3)
    
    # Add actions
    ai.add_action("melee_attack", {
        "type": "attack",
        "attack_type": "melee",
        "range": 1.5,
        "cooldown": 1.0
    })
    
    ai.add_action("ranged_attack", {
        "type": "attack",
        "attack_type": "ranged",
        "range": 5.0,
        "cooldown": 2.0
    })
    
    ai.add_action("defend", {
        "type": "defend",
        "defense_type": "block",
        "cooldown": 3.0
    })
    
    ai.add_action("heal_self", {
        "type": "heal",
        "heal_type": "self",
        "cooldown": 10.0
    })
    
    ai.add_action("flee", {
        "type": "flee",
        "cooldown": 5.0
    })
    
    world.add_component(enemy, ai)
    
    return enemy

def print_entity_info(world, entity_id, name):
    """Print information about an entity."""
    transform = world.get_component(entity_id, TransformComponent)
    stats = world.get_component(entity_id, CharacterStatsComponent)
    
    position = transform.position if transform else "Unknown"
    health = f"{stats.health}/{stats.current_stats['max_health']}" if stats else "Unknown"
    
    print(f"{name} - Position: {position}, Health: {health}")

def print_ai_info(world, entity_id):
    """Print information about an entity's AI."""
    ai = world.get_component(entity_id, AIComponent)
    if not ai:
        return
    
    print(f"AI Type: {ai.ai_type}")
    print(f"Personality: {ai.personality}")
    print(f"Current Action: {ai.current_action_id}")
    print(f"Target: {ai.target_entity_id}")
    
    # Print perception
    enemies = len(ai.perception["enemies"])
    allies = len(ai.perception["allies"])
    print(f"Perception: {enemies} enemies, {allies} allies")

def simulate_combat(world, ai_system, player_id, enemy_id, duration=10.0):
    """Simulate combat between player and enemy for a duration."""
    start_time = time.time()
    elapsed = 0.0
    
    print("\n=== Starting Combat Simulation ===\n")
    
    while elapsed < duration:
        # Calculate delta time (in a real game, this would come from the game loop)
        current_time = time.time()
        dt = current_time - start_time - elapsed
        elapsed = current_time - start_time
        
        # Update AI system
        ai_system.update(dt)
        
        # Print status every second
        if int(elapsed) > int(elapsed - dt):
            print(f"\n--- Time: {elapsed:.1f}s ---")
            print_entity_info(world, player_id, "Player")
            print_entity_info(world, enemy_id, "Enemy")
            print_ai_info(world, enemy_id)
            
            # Simulate player attacking enemy
            if random.random() < 0.3:  # 30% chance to attack each second
                player_stats = world.get_component(player_id, CharacterStatsComponent)
                enemy_stats = world.get_component(enemy_id, CharacterStatsComponent)
                
                if player_stats and enemy_stats:
                    damage = player_stats.current_stats["attack_power"]
                    enemy_stats.take_damage(damage)
                    print(f"Player attacks enemy for {damage} damage!")
        
        # Small delay to prevent CPU hogging
        time.sleep(0.016)  # ~60 FPS
    
    print("\n=== Combat Simulation Ended ===\n")

def main():
    """Main function to run the example."""
    # Create world
    world = World()
    
    # Create AI system
    ai_system = AISystem(world)
    
    # Create player
    player = create_player(world, (0, 0))
    
    # Create enemy with aggressive personality
    aggressive_personality = {
        "bravery": 0.8,
        "aggression": 0.9,
        "cooperation": 0.3,
        "curiosity": 0.6,
        "intelligence": 0.7
    }
    enemy = create_enemy(world, (5, 5), aggressive_personality)
    
    # Print initial state
    print("\n=== Initial State ===\n")
    print_entity_info(world, player, "Player")
    print_entity_info(world, enemy, "Enemy")
    print_ai_info(world, enemy)
    
    # Simulate combat
    simulate_combat(world, ai_system, player, enemy, duration=15.0)
    
    # Print final state
    print("\n=== Final State ===\n")
    print_entity_info(world, player, "Player")
    print_entity_info(world, enemy, "Enemy")
    
    # Check if enemy is alive
    enemy_stats = world.get_component(enemy, CharacterStatsComponent)
    if enemy_stats and enemy_stats.is_alive():
        print("The enemy survived the encounter!")
    else:
        print("The enemy was defeated!")

if __name__ == "__main__":
    main() 