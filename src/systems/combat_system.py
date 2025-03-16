"""
Combat system for the Entity Component System.

This system handles combat mechanics, including attacks, damage calculation,
combat state management, and threat.
"""

import math
import random
import time
from ..ecs.system import System
from ..components.combat import CombatComponent, CombatStance, AttackType
from ..components.character_stats import CharacterStatsComponent
from ..components.transform import TransformComponent
from ..events.event_types import EventType

class CombatSystem(System):
    """
    System that manages combat between entities.
    
    This system processes entities with combat components to handle
    combat mechanics like attacking, defending, and combat state management.
    """
    
    def __init__(self, world, event_manager):
        """
        Initialize the combat system.
        
        Args:
            world: The world this system belongs to
            event_manager: The event manager for emitting events
        """
        super().__init__(world)
        self.event_manager = event_manager
        self.required_components = [CombatComponent, CharacterStatsComponent]
        
        # Combat constants
        self.base_hit_chance = 0.8  # 80% base chance to hit
        self.base_crit_chance = 0.05  # 5% base chance for critical hit
        self.base_crit_multiplier = 1.5  # 50% additional damage on crits
        self.base_dodge_chance = 0.05  # 5% base chance to dodge
        self.base_block_chance = 0.05  # 5% base chance to block
        self.base_parry_chance = 0.05  # 5% base chance to parry
        self.base_resist_chance = 0.05  # 5% base chance to resist
        self.global_cooldown_duration = 1.0  # 1 second global cooldown
        
        # Maximum detection range for auto-entering combat
        self.combat_detection_range = 10.0
        
        # Time to exit combat after no combat actions
        self.combat_exit_time = 6.0  # Exit combat after 6 seconds of no actions
        
        # Subscribe to events
        self._subscribe_to_events()
    
    def _subscribe_to_events(self):
        """Subscribe to relevant events."""
        self.event_manager.subscribe(EventType.ENTITY_MOVED, self._on_entity_moved)
        self.event_manager.subscribe(EventType.ENTITY_DIED, self._on_entity_died)
    
    def _on_entity_moved(self, event_data):
        """
        Handle entity moved event.
        
        Args:
            event_data: Event data containing the entity that moved
        """
        entity = event_data.get("entity")
        if not entity:
            return
        
        # Check if entity has combat component
        combat_comp = self.world.get_component(entity.id, CombatComponent)
        if not combat_comp:
            return
        
        # Update positioning relative to target if in combat
        if combat_comp.in_combat and combat_comp.current_target_id:
            self._update_combat_positioning(entity.id, combat_comp)
    
    def _on_entity_died(self, event_data):
        """
        Handle entity died event.
        
        Args:
            event_data: Event data containing the entity that died
        """
        entity = event_data.get("entity")
        killer = event_data.get("killer")
        
        if not entity:
            return
        
        # Mark kill in killer's combat stats if available
        if killer:
            combat_comp = self.world.get_component(killer.id, CombatComponent)
            if combat_comp:
                combat_comp.record_kill()
        
        # Clear all entities targeting the dead entity
        for other_id, other_entity in self.world.entities.items():
            other_combat = self.world.get_component(other_id, CombatComponent)
            if other_combat and other_combat.current_target_id == entity.id:
                other_combat.clear_target()
    
    def update(self, dt):
        """
        Update all entities with combat components.
        
        Args:
            dt: Delta time in seconds
        """
        # Get entities with required components
        entities = self.world.get_entities_with_components(self.required_components)
        
        current_time = time.time()
        
        for entity_id in entities:
            combat_comp = self.world.get_component(entity_id, CombatComponent)
            
            # Update cooldowns
            combat_comp.update_cooldowns(dt)
            
            # Check if we should exit combat due to inactivity
            if combat_comp.in_combat and current_time - combat_comp.last_combat_action_time > self.combat_exit_time:
                # No combat action for a while, exit combat
                self._exit_combat(entity_id, combat_comp)
            
            # Process auto-attacks
            if combat_comp.should_auto_attack(current_time):
                self._process_auto_attack(entity_id, combat_comp)
            
            # Update combat state based on targets
            self._update_combat_state(entity_id, combat_comp)
    
    def _update_combat_state(self, entity_id, combat_comp):
        """
        Update the combat state of an entity.
        
        Args:
            entity_id: ID of the entity
            combat_comp: Combat component of the entity
        """
        # If has target but not in combat, enter combat
        if not combat_comp.in_combat and combat_comp.current_target_id:
            self._enter_combat(entity_id, combat_comp)
        
        # If in combat but no target and not targeted by anyone, consider exiting combat
        if combat_comp.in_combat and not combat_comp.current_target_id and not combat_comp.targeted_by:
            # Keep in combat if there are nearby enemies
            nearby_enemies = self._find_nearby_enemies(entity_id, self.combat_detection_range)
            if not nearby_enemies:
                self._exit_combat(entity_id, combat_comp)
    
    def _update_combat_positioning(self, entity_id, combat_comp):
        """
        Update combat positioning relative to target.
        
        Args:
            entity_id: ID of the entity
            combat_comp: Combat component of the entity
        """
        # Get target entity
        target_id = combat_comp.current_target_id
        if not target_id or target_id not in self.world.entities:
            return
        
        # Get transform components
        entity_transform = self.world.get_component(entity_id, TransformComponent)
        target_transform = self.world.get_component(target_id, TransformComponent)
        
        if not entity_transform or not target_transform:
            return
        
        # Calculate distance to target
        dx = target_transform.position.x - entity_transform.position.x
        dy = target_transform.position.y - entity_transform.position.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # AI components might use this information to decide whether to
        # move closer, maintain distance, etc.
        # This is just a hook for now - actual movement is handled by AI
    
    def _enter_combat(self, entity_id, combat_comp):
        """
        Enter combat state.
        
        Args:
            entity_id: ID of the entity
            combat_comp: Combat component of the entity
        """
        if combat_comp.enter_combat():
            # Reset opportunity attacks
            combat_comp.reset_opportunity_attacks()
            
            # Update last combat action time
            combat_comp.update_last_combat_action_time()
            
            # Emit enter combat event
            self.event_manager.emit(EventType.COMBAT_ENTERED, {
                "entity_id": entity_id,
                "target_id": combat_comp.current_target_id
            })
    
    def _exit_combat(self, entity_id, combat_comp):
        """
        Exit combat state.
        
        Args:
            entity_id: ID of the entity
            combat_comp: Combat component of the entity
        """
        if combat_comp.exit_combat():
            # Emit exit combat event
            self.event_manager.emit(EventType.COMBAT_EXITED, {
                "entity_id": entity_id
            })
    
    def _process_auto_attack(self, entity_id, combat_comp):
        """
        Process auto-attack.
        
        Args:
            entity_id: ID of the entity
            combat_comp: Combat component of the entity
        """
        target_id = combat_comp.current_target_id
        if not target_id or target_id not in self.world.entities:
            return
        
        # Check if in range
        in_range = self._is_in_attack_range(entity_id, target_id, combat_comp)
        if not in_range:
            return
        
        # Perform auto-attack
        self.perform_attack(entity_id, target_id)
        
        # Update last auto-attack time
        combat_comp.update_last_auto_attack_time()
    
    def _is_in_attack_range(self, attacker_id, target_id, combat_comp=None):
        """
        Check if a target is in attack range.
        
        Args:
            attacker_id: ID of the attacker
            target_id: ID of the target
            combat_comp: Combat component of the attacker, or None to get it
            
        Returns:
            bool: True if the target is in range
        """
        if not combat_comp:
            combat_comp = self.world.get_component(attacker_id, CombatComponent)
            if not combat_comp:
                return False
        
        # Get transform components
        attacker_transform = self.world.get_component(attacker_id, TransformComponent)
        target_transform = self.world.get_component(target_id, TransformComponent)
        
        if not attacker_transform or not target_transform:
            return False
        
        # Calculate distance
        dx = target_transform.position.x - attacker_transform.position.x
        dy = target_transform.position.y - attacker_transform.position.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Check if in range based on attack type
        attack_range = combat_comp.get_attack_range()
        return distance <= attack_range
    
    def _find_nearby_enemies(self, entity_id, max_range):
        """
        Find nearby enemy entities.
        
        Args:
            entity_id: ID of the entity
            max_range: Maximum range to search
            
        Returns:
            list: List of nearby enemy entity IDs
        """
        # Get all entities with combat components
        all_combat_entities = self.world.get_entities_with_components([CombatComponent])
        
        # Get entity transform
        entity_transform = self.world.get_component(entity_id, TransformComponent)
        if not entity_transform:
            return []
        
        nearby_enemies = []
        
        for other_id in all_combat_entities:
            # Skip self
            if other_id == entity_id:
                continue
            
            # Get other entity transform
            other_transform = self.world.get_component(other_id, TransformComponent)
            if not other_transform:
                continue
            
            # Calculate distance
            dx = other_transform.position.x - entity_transform.position.x
            dy = other_transform.position.y - entity_transform.position.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Check if in range
            if distance <= max_range:
                # For now, we'll consider all entities as potential enemies
                # In a real implementation, you would check factions, etc.
                nearby_enemies.append(other_id)
        
        return nearby_enemies
    
    def perform_attack(self, attacker_id, target_id, attack_id="melee_attack"):
        """
        Perform an attack from one entity to another.
        
        Args:
            attacker_id: ID of the attacking entity
            target_id: ID of the target entity
            attack_id: ID of the attack to perform
            
        Returns:
            bool: True if the attack was performed, False otherwise
        """
        # Get components
        attacker_combat = self.world.get_component(attacker_id, CombatComponent)
        attacker_stats = self.world.get_component(attacker_id, CharacterStatsComponent)
        target_combat = self.world.get_component(target_id, CombatComponent)
        target_stats = self.world.get_component(target_id, CharacterStatsComponent)
        
        if not all([attacker_combat, attacker_stats, target_combat, target_stats]):
            return False
        
        # Check if attack is on cooldown
        if attacker_combat.is_on_cooldown(attack_id):
            return False
        
        # Check if target is alive
        if not target_stats.is_alive():
            return False
        
        # Enter combat for both entities
        self._enter_combat(attacker_id, attacker_combat)
        self._enter_combat(target_id, target_combat)
        
        # Set targeting relationships
        attacker_combat.set_target(target_id)
        target_combat.add_targeted_by(attacker_id)
        
        # Update last combat action time
        attacker_combat.update_last_combat_action_time()
        
        # Start attack cooldown and global cooldown
        attacker_combat.start_cooldown(attack_id, 2.0)  # Default 2 second cooldown
        attacker_combat.start_global_cooldown(self.global_cooldown_duration)
        
        # Emit attack started event
        self.event_manager.emit(EventType.ATTACK_STARTED, {
            "attacker_id": attacker_id,
            "target_id": target_id,
            "attack_id": attack_id
        })
        
        # Calculate hit chance
        hit_chance = self._calculate_hit_chance(attacker_stats, target_stats, attacker_combat, target_combat)
        
        # Check if attack hits
        if random.random() > hit_chance:
            # Attack missed
            attacker_combat.record_attack_missed()
            
            # Emit attack missed event
            self.event_manager.emit(EventType.ATTACK_MISSED, {
                "attacker_id": attacker_id,
                "target_id": target_id,
                "attack_id": attack_id
            })
            
            return False
        
        # Calculate critical hit chance
        crit_chance = self._calculate_crit_chance(attacker_stats, target_stats, attacker_combat)
        is_critical = random.random() <= crit_chance
        
        # Calculate damage
        damage = self._calculate_damage(attacker_stats, target_stats, attacker_combat, target_combat, is_critical)
        
        # Apply damage
        actual_damage = target_stats.take_damage(damage)
        
        # Update combat statistics
        attacker_combat.record_damage_dealt(actual_damage, is_critical)
        target_combat.record_damage_taken(actual_damage)
        
        # Add threat
        target_combat.add_threat(attacker_id, actual_damage)
        
        # Emit attack landed event
        self.event_manager.emit(EventType.ATTACK_LANDED, {
            "attacker_id": attacker_id,
            "target_id": target_id,
            "attack_id": attack_id,
            "damage": actual_damage,
            "is_critical": is_critical
        })
        
        # Check if target died
        if not target_stats.is_alive():
            self.event_manager.emit(EventType.ENTITY_DIED, {
                "entity_id": target_id,
                "killer_id": attacker_id
            })
        
        return True
    
    def _calculate_hit_chance(self, attacker_stats, target_stats, attacker_combat, target_combat):
        """
        Calculate the chance to hit.
        
        Args:
            attacker_stats: Character stats of the attacker
            target_stats: Character stats of the target
            attacker_combat: Combat component of the attacker
            target_combat: Combat component of the target
            
        Returns:
            float: Chance to hit (0.0 to 1.0)
        """
        # Start with base hit chance
        hit_chance = self.base_hit_chance
        
        # Adjust based on attacker's dexterity and target's dexterity
        attacker_dex = attacker_stats.current_stats.get("dexterity", 10)
        target_dex = target_stats.current_stats.get("dexterity", 10)
        
        # Dexterity difference adjustment
        dex_factor = 0.01  # Each point of difference adjusts hit chance by 1%
        dex_diff = attacker_dex - target_dex
        hit_chance += dex_diff * dex_factor
        
        # Apply stance modifiers
        if attacker_combat.stance == CombatStance.AGGRESSIVE:
            hit_chance += 0.1  # +10% hit chance in aggressive stance
        elif attacker_combat.stance == CombatStance.DEFENSIVE:
            hit_chance -= 0.05  # -5% hit chance in defensive stance
        
        if target_combat.stance == CombatStance.DEFENSIVE:
            hit_chance -= 0.1  # -10% hit chance against defensive stance
        
        # Calculate dodge chance
        dodge_chance = self._calculate_dodge_chance(target_stats, target_combat)
        
        # Final hit chance is base hit chance minus dodge chance
        final_hit_chance = hit_chance - dodge_chance
        
        # Clamp to 0.0-0.95 range (always at least 5% chance to miss)
        return max(0.0, min(0.95, final_hit_chance))
    
    def _calculate_dodge_chance(self, target_stats, target_combat):
        """
        Calculate the chance to dodge an attack.
        
        Args:
            target_stats: Character stats of the target
            target_combat: Combat component of the target
            
        Returns:
            float: Chance to dodge (0.0 to 1.0)
        """
        # Start with base dodge chance
        dodge_chance = self.base_dodge_chance
        
        # Adjust based on target's dexterity
        target_dex = target_stats.current_stats.get("dexterity", 10)
        dodge_factor = 0.005  # Each point of dexterity adds 0.5% dodge chance
        dodge_chance += target_dex * dodge_factor
        
        # Apply stance modifiers
        if target_combat.stance == CombatStance.DEFENSIVE:
            dodge_chance += 0.1  # +10% dodge chance in defensive stance
        
        # Apply dodge chance bonus from combat component
        dodge_chance += target_combat.dodge_chance_bonus
        
        # Clamp to 0.0-0.75 range (max 75% dodge chance)
        return max(0.0, min(0.75, dodge_chance))
    
    def _calculate_crit_chance(self, attacker_stats, target_stats, attacker_combat):
        """
        Calculate the chance for a critical hit.
        
        Args:
            attacker_stats: Character stats of the attacker
            target_stats: Character stats of the target
            attacker_combat: Combat component of the attacker
            
        Returns:
            float: Chance for a critical hit (0.0 to 1.0)
        """
        # Start with base crit chance
        crit_chance = self.base_crit_chance
        
        # Adjust based on attacker's dexterity
        attacker_dex = attacker_stats.current_stats.get("dexterity", 10)
        crit_factor = 0.003  # Each point of dexterity adds 0.3% crit chance
        crit_chance += attacker_dex * crit_factor
        
        # Apply stance modifiers
        if attacker_combat.stance == CombatStance.AGGRESSIVE:
            crit_chance += 0.05  # +5% crit chance in aggressive stance
        
        # Apply crit chance bonus from combat component
        crit_chance += attacker_combat.critical_chance_bonus
        
        # Clamp to 0.05-0.5 range (5% to 50% crit chance)
        return max(0.05, min(0.5, crit_chance))
    
    def _calculate_damage(self, attacker_stats, target_stats, attacker_combat, target_combat, is_critical):
        """
        Calculate damage for an attack.
        
        Args:
            attacker_stats: Character stats of the attacker
            target_stats: Character stats of the target
            attacker_combat: Combat component of the attacker
            target_combat: Combat component of the target
            is_critical: Whether the attack is a critical hit
            
        Returns:
            float: Damage amount
        """
        # Get base attack power and armor class
        attack_power = attacker_stats.current_stats.get("attack_power", 10)
        armor_class = target_stats.current_stats.get("armor_class", 10)
        
        # Add strength bonus to attack power
        strength = attacker_stats.current_stats.get("strength", 10)
        attack_power += (strength - 10) * 0.5  # Each point above 10 adds 0.5 to attack
        
        # Apply stance modifiers
        if attacker_combat.stance == CombatStance.AGGRESSIVE:
            attack_power *= 1.2  # +20% damage in aggressive stance
        elif attacker_combat.stance == CombatStance.DEFENSIVE:
            attack_power *= 0.8  # -20% damage in defensive stance
        
        if target_combat.stance == CombatStance.DEFENSIVE:
            armor_class *= 1.2  # +20% armor in defensive stance
        
        # Calculate damage reduction from armor
        # Formula: Damage reduction percentage = armor / (armor + 50)
        damage_reduction = armor_class / (armor_class + 50)
        
        # Base damage calculation
        base_damage = attack_power * (1.0 - damage_reduction)
        
        # Apply critical multiplier if critical hit
        if is_critical:
            base_damage *= self.base_crit_multiplier
        
        # Apply damage multiplier from combat component
        base_damage *= attacker_combat.damage_multiplier
        
        # Apply defense multiplier from target combat component
        base_damage /= target_combat.defense_multiplier
        
        # Add randomness (-10% to +10%)
        randomness = 0.9 + random.random() * 0.2  # 0.9 to 1.1
        final_damage = base_damage * randomness
        
        # Ensure minimum damage of 1
        return max(1, final_damage)
    
    def get_potential_damage(self, attacker_id, target_id, is_critical=False):
        """
        Calculate the potential damage for an attack without performing it.
        
        Args:
            attacker_id: ID of the attacking entity
            target_id: ID of the target entity
            is_critical: Whether to calculate for a critical hit
            
        Returns:
            float: Potential damage amount
        """
        # Get components
        attacker_combat = self.world.get_component(attacker_id, CombatComponent)
        attacker_stats = self.world.get_component(attacker_id, CharacterStatsComponent)
        target_combat = self.world.get_component(target_id, CombatComponent)
        target_stats = self.world.get_component(target_id, CharacterStatsComponent)
        
        if not all([attacker_combat, attacker_stats, target_combat, target_stats]):
            return 0
        
        # Calculate damage
        return self._calculate_damage(attacker_stats, target_stats, attacker_combat, target_combat, is_critical)
    
    def get_hit_chance(self, attacker_id, target_id):
        """
        Calculate the hit chance for an attack without performing it.
        
        Args:
            attacker_id: ID of the attacking entity
            target_id: ID of the target entity
            
        Returns:
            float: Hit chance (0.0 to 1.0)
        """
        # Get components
        attacker_combat = self.world.get_component(attacker_id, CombatComponent)
        attacker_stats = self.world.get_component(attacker_id, CharacterStatsComponent)
        target_combat = self.world.get_component(target_id, CombatComponent)
        target_stats = self.world.get_component(target_id, CharacterStatsComponent)
        
        if not all([attacker_combat, attacker_stats, target_combat, target_stats]):
            return 0
        
        # Calculate hit chance
        return self._calculate_hit_chance(attacker_stats, target_stats, attacker_combat, target_combat)
    
    def change_stance(self, entity_id, stance):
        """
        Change the combat stance of an entity.
        
        Args:
            entity_id: ID of the entity
            stance: The new stance to set
            
        Returns:
            bool: True if stance was changed, False otherwise
        """
        combat_comp = self.world.get_component(entity_id, CombatComponent)
        if not combat_comp:
            return False
        
        # Set new stance
        old_stance = combat_comp.stance
        combat_comp.set_stance(stance)
        
        # Emit stance changed event
        self.event_manager.emit(EventType.COMBAT_STANCE_CHANGED, {
            "entity_id": entity_id,
            "old_stance": old_stance,
            "new_stance": stance
        })
        
        return True 