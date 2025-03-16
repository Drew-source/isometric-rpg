"""
Example demonstrating the combat system.

This example creates a simple combat scenario between two characters,
showing how the combat system interacts with other components.
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
from src.components import AIComponent, CharacterStatsComponent, TransformComponent, CombatComponent, CombatStance, AttackType
from src.systems.ai_system import AISystem
from src.systems.combat_system import CombatSystem

def create_player(world, position):
    """Create a player entity."""
    player = world.create_entity()
    
    # Add transform component
    transform = TransformComponent()
    transform.set_position(position[0], position[1])
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
    
    # Add combat component
    combat = CombatComponent()
    combat.set_stance(CombatStance.AGGRESSIVE)
    combat.set_preferred_attack_type(AttackType.MELEE)
    combat.melee_range = 2.0  # 2 tiles
    combat.damage_multiplier = 1.2  # 20% bonus damage
    world.add_component(player, combat)
    
    return player

def create_enemy(world, position, personality=None):
    """Create an enemy entity with AI and combat components."""
    enemy = world.create_entity()
    
    # Add transform component
    transform = TransformComponent()
    transform.set_position(position[0], position[1])
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
    
    # Add combat component
    combat = CombatComponent()
    # Set stance based on personality
    if personality and "aggression" in personality:
        if personality["aggression"] > 0.7:
            combat.set_stance(CombatStance.AGGRESSIVE)
        elif personality["aggression"] < 0.3:
            combat.set_stance(CombatStance.DEFENSIVE)
    
    # Set preferred attack type
    combat.set_preferred_attack_type(AttackType.MELEE)
    
    # Enable auto-attack
    combat.auto_attack_enabled = True
    combat.auto_attack_interval = 1.5  # Auto-attack every 1.5 seconds
    world.add_component(enemy, combat)
    
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
    combat = world.get_component(entity_id, CombatComponent)
    
    position = transform.position if transform else "Unknown"
    health = f"{stats.health:.1f}/{stats.current_stats['max_health']}" if stats else "Unknown"
    
    combat_status = "In Combat" if combat and combat.in_combat else "Not In Combat"
    target = combat.current_target_id if combat and combat.current_target_id else "None"
    stance = combat.stance.name if combat else "Unknown"
    
    print(f"{name} - Position: {position}, Health: {health}, Status: {combat_status}, Target: {target}, Stance: {stance}")
    
    if combat:
        print(f"  Damage dealt: {combat.damage_dealt:.1f}, Taken: {combat.damage_taken:.1f}")
        print(f"  Hits: {combat.attacks_landed}, Misses: {combat.attacks_missed}, Crits: {combat.critical_hits}")

def handle_combat_event(event_type, event_data):
    """Print combat event information."""
    if event_type == EventType.ATTACK_STARTED:
        attacker_id = event_data.get("attacker_id")
        target_id = event_data.get("target_id")
        print(f"Attack started: {attacker_id} -> {target_id}")
    
    elif event_type == EventType.ATTACK_LANDED:
        attacker_id = event_data.get("attacker_id")
        target_id = event_data.get("target_id")
        damage = event_data.get("damage", 0)
        is_critical = event_data.get("is_critical", False)
        crit_text = "CRITICAL HIT! " if is_critical else ""
        print(f"{crit_text}Attack landed: {attacker_id} -> {target_id} for {damage:.1f} damage")
    
    elif event_type == EventType.ATTACK_MISSED:
        attacker_id = event_data.get("attacker_id")
        target_id = event_data.get("target_id")
        print(f"Attack missed: {attacker_id} -> {target_id}")
    
    elif event_type == EventType.ENTITY_DIED:
        entity_id = event_data.get("entity_id")
        killer_id = event_data.get("killer_id")
        print(f"Entity died: {entity_id}, killed by: {killer_id}")
    
    elif event_type == EventType.COMBAT_ENTERED:
        entity_id = event_data.get("entity_id")
        print(f"Entity entered combat: {entity_id}")
    
    elif event_type == EventType.COMBAT_EXITED:
        entity_id = event_data.get("entity_id")
        print(f"Entity exited combat: {entity_id}")

def simulate_combat(world, ai_system, combat_system, player_id, enemy_id, duration=10.0):
    """Simulate combat between player and enemy for a duration."""
    start_time = time.time()
    elapsed = 0.0
    
    print("\n=== Starting Combat Simulation ===\n")
    
    # Have player target enemy
    player_combat = world.get_component(player_id, CombatComponent)
    if player_combat:
        player_combat.set_target(enemy_id)
        player_combat.auto_attack_enabled = True
        player_combat.auto_attack_interval = 2.0  # Auto-attack every 2 seconds
    
    # Have enemy target player
    enemy_combat = world.get_component(enemy_id, CombatComponent)
    enemy_ai = world.get_component(enemy_id, AIComponent)
    if enemy_combat and enemy_ai:
        enemy_combat.set_target(player_id)
        enemy_ai.set_target(player_id)
    
    while elapsed < duration:
        # Calculate delta time (in a real game, this would come from the game loop)
        current_time = time.time()
        dt = min(current_time - start_time - elapsed, 0.05)  # Cap at 50ms to prevent physics issues
        elapsed = current_time - start_time
        
        # Update AI system
        ai_system.update(dt)
        
        # Update combat system
        combat_system.update(dt)
        
        # Print status every second
        if int(elapsed) > int(elapsed - dt):
            print(f"\n--- Time: {elapsed:.1f}s ---")
            print_entity_info(world, player_id, "Player")
            print_entity_info(world, enemy_id, "Enemy")
            
            # Occasionally change stance
            if random.random() < 0.2:  # 20% chance per second
                if player_combat:
                    new_stance = random.choice(list(CombatStance))
                    combat_system.change_stance(player_id, new_stance)
                    print(f"Player changed stance to {new_stance.name}")
        
        # Small delay to prevent CPU hogging
        time.sleep(0.016)  # ~60 FPS
    
    print("\n=== Combat Simulation Ended ===\n")

def main():
    """Main function to run the example."""
    # Create event manager
    event_manager = EventManager()
    
    # Subscribe to combat events
    event_manager.subscribe(EventType.ATTACK_STARTED, lambda data: handle_combat_event(EventType.ATTACK_STARTED, data))
    event_manager.subscribe(EventType.ATTACK_LANDED, lambda data: handle_combat_event(EventType.ATTACK_LANDED, data))
    event_manager.subscribe(EventType.ATTACK_MISSED, lambda data: handle_combat_event(EventType.ATTACK_MISSED, data))
    event_manager.subscribe(EventType.ENTITY_DIED, lambda data: handle_combat_event(EventType.ENTITY_DIED, data))
    event_manager.subscribe(EventType.COMBAT_ENTERED, lambda data: handle_combat_event(EventType.COMBAT_ENTERED, data))
    event_manager.subscribe(EventType.COMBAT_EXITED, lambda data: handle_combat_event(EventType.COMBAT_EXITED, data))
    
    # Create world
    world = World(event_manager)
    
    # Create AI system
    ai_system = AISystem(world, event_manager)
    
    # Create combat system
    combat_system = CombatSystem(world, event_manager)
    
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
    enemy = create_enemy(world, (2, 2), aggressive_personality)
    
    # Print initial state
    print("\n=== Initial State ===\n")
    print_entity_info(world, player, "Player")
    print_entity_info(world, enemy, "Enemy")
    
    # Simulate combat
    simulate_combat(world, ai_system, combat_system, player, enemy, duration=15.0)
    
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
    
    # Check if player is alive
    player_stats = world.get_component(player, CharacterStatsComponent)
    if player_stats and player_stats.is_alive():
        print("The player survived the encounter!")
    else:
        print("The player was defeated!")

if __name__ == "__main__":
    main() 