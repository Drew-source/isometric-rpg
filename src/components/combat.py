"""
Combat component for the Entity Component System.

This component stores combat-related data and state for entities.
"""

import random
import time
from enum import Enum
from ..ecs.component import Component

class CombatStance(Enum):
    """Combat stance enumeration."""
    NEUTRAL = 0
    AGGRESSIVE = 1
    DEFENSIVE = 2

class AttackType(Enum):
    """Attack type enumeration."""
    MELEE = 0
    RANGED = 1
    SPELL = 2

class CombatComponent(Component):
    """
    Component that manages combat state and actions.
    
    This component stores data needed for combat such as attack cooldowns,
    combat stance, target information, and combat state.
    """
    
    def __init__(self):
        """Initialize the combat component."""
        super().__init__()
        
        # Combat state
        self.in_combat = False
        self.combat_start_time = 0
        self.last_combat_action_time = 0
        self.last_damage_taken_time = 0
        self.last_damage_dealt_time = 0
        
        # Combat properties
        self.stance = CombatStance.NEUTRAL
        self.preferred_attack_type = AttackType.MELEE
        self.attack_cooldowns = {}  # Attack ID -> cooldown remaining
        self.global_cooldown = 0.0
        self.opportunity_attacks = 3  # Opportunity attacks per round
        self.opportunity_attacks_used = 0
        
        # Targeting
        self.current_target_id = None
        self.targeted_by = set()  # Set of entity IDs targeting this entity
        self.threat_table = {}  # Entity ID -> threat value
        
        # Combat statistics (for this session)
        self.damage_dealt = 0
        self.damage_taken = 0
        self.healing_done = 0
        self.critical_hits = 0
        self.attacks_landed = 0
        self.attacks_missed = 0
        self.kills = 0
        
        # Temporary combat modifiers
        self.damage_multiplier = 1.0
        self.defense_multiplier = 1.0
        self.critical_chance_bonus = 0.0
        self.dodge_chance_bonus = 0.0
        
        # Combat range
        self.melee_range = 1.5  # Default melee range in tiles
        self.ranged_range = 10.0  # Default ranged attack range in tiles
        self.spell_range = 8.0  # Default spell range in tiles
        
        # Auto-attack settings
        self.auto_attack_enabled = False
        self.auto_attack_interval = 2.0  # Seconds between auto-attacks
        self.last_auto_attack_time = 0
    
    def serialize(self):
        """
        Convert component data to a serializable format.
        
        Returns:
            dict: Serialized component data
        """
        return {
            "in_combat": self.in_combat,
            "combat_start_time": self.combat_start_time,
            "last_combat_action_time": self.last_combat_action_time,
            "stance": self.stance.value,
            "preferred_attack_type": self.preferred_attack_type.value,
            "global_cooldown": self.global_cooldown,
            "opportunity_attacks": self.opportunity_attacks,
            "opportunity_attacks_used": self.opportunity_attacks_used,
            "current_target_id": self.current_target_id,
            "targeted_by": list(self.targeted_by),
            "threat_table": self.threat_table,
            "damage_dealt": self.damage_dealt,
            "damage_taken": self.damage_taken,
            "healing_done": self.healing_done,
            "critical_hits": self.critical_hits,
            "attacks_landed": self.attacks_landed,
            "attacks_missed": self.attacks_missed,
            "kills": self.kills,
            "damage_multiplier": self.damage_multiplier,
            "defense_multiplier": self.defense_multiplier,
            "critical_chance_bonus": self.critical_chance_bonus,
            "dodge_chance_bonus": self.dodge_chance_bonus,
            "melee_range": self.melee_range,
            "ranged_range": self.ranged_range,
            "spell_range": self.spell_range,
            "auto_attack_enabled": self.auto_attack_enabled,
            "auto_attack_interval": self.auto_attack_interval
        }
    
    @classmethod
    def deserialize(cls, data):
        """
        Create a component from serialized data.
        
        Args:
            data: Serialized component data
            
        Returns:
            CombatComponent: New component instance
        """
        component = cls()
        component.in_combat = data.get("in_combat", False)
        component.combat_start_time = data.get("combat_start_time", 0)
        component.last_combat_action_time = data.get("last_combat_action_time", 0)
        component.stance = CombatStance(data.get("stance", CombatStance.NEUTRAL.value))
        component.preferred_attack_type = AttackType(data.get("preferred_attack_type", AttackType.MELEE.value))
        component.global_cooldown = data.get("global_cooldown", 0.0)
        component.opportunity_attacks = data.get("opportunity_attacks", 3)
        component.opportunity_attacks_used = data.get("opportunity_attacks_used", 0)
        component.current_target_id = data.get("current_target_id")
        component.targeted_by = set(data.get("targeted_by", []))
        component.threat_table = data.get("threat_table", {})
        component.damage_dealt = data.get("damage_dealt", 0)
        component.damage_taken = data.get("damage_taken", 0)
        component.healing_done = data.get("healing_done", 0)
        component.critical_hits = data.get("critical_hits", 0)
        component.attacks_landed = data.get("attacks_landed", 0)
        component.attacks_missed = data.get("attacks_missed", 0)
        component.kills = data.get("kills", 0)
        component.damage_multiplier = data.get("damage_multiplier", 1.0)
        component.defense_multiplier = data.get("defense_multiplier", 1.0)
        component.critical_chance_bonus = data.get("critical_chance_bonus", 0.0)
        component.dodge_chance_bonus = data.get("dodge_chance_bonus", 0.0)
        component.melee_range = data.get("melee_range", 1.5)
        component.ranged_range = data.get("ranged_range", 10.0)
        component.spell_range = data.get("spell_range", 8.0)
        component.auto_attack_enabled = data.get("auto_attack_enabled", False)
        component.auto_attack_interval = data.get("auto_attack_interval", 2.0)
        return component
    
    def enter_combat(self):
        """
        Enter combat state.
        
        Returns:
            bool: True if entered combat, False if already in combat
        """
        if not self.in_combat:
            self.in_combat = True
            self.combat_start_time = time.time()
            self.opportunity_attacks_used = 0
            return True
        return False
    
    def exit_combat(self):
        """
        Exit combat state.
        
        Returns:
            bool: True if exited combat, False if not in combat
        """
        if self.in_combat:
            self.in_combat = False
            self.current_target_id = None
            self.reset_threat_table()
            return True
        return False
    
    def set_target(self, target_id):
        """
        Set current combat target.
        
        Args:
            target_id: ID of the target entity
            
        Returns:
            CombatComponent: Self for method chaining
        """
        self.current_target_id = target_id
        return self
    
    def clear_target(self):
        """
        Clear current combat target.
        
        Returns:
            CombatComponent: Self for method chaining
        """
        self.current_target_id = None
        return self
    
    def add_targeted_by(self, entity_id):
        """
        Add an entity that is targeting this entity.
        
        Args:
            entity_id: ID of the entity targeting this entity
            
        Returns:
            CombatComponent: Self for method chaining
        """
        self.targeted_by.add(entity_id)
        return self
    
    def remove_targeted_by(self, entity_id):
        """
        Remove an entity that was targeting this entity.
        
        Args:
            entity_id: ID of the entity no longer targeting this entity
            
        Returns:
            CombatComponent: Self for method chaining
        """
        if entity_id in self.targeted_by:
            self.targeted_by.remove(entity_id)
        return self
    
    def is_targeted_by(self, entity_id):
        """
        Check if an entity is targeting this entity.
        
        Args:
            entity_id: ID of the entity to check
            
        Returns:
            bool: True if the entity is targeting this entity
        """
        return entity_id in self.targeted_by
    
    def add_threat(self, entity_id, amount):
        """
        Add threat for an entity.
        
        Args:
            entity_id: ID of the entity to add threat for
            amount: Amount of threat to add
            
        Returns:
            CombatComponent: Self for method chaining
        """
        current = self.threat_table.get(entity_id, 0)
        self.threat_table[entity_id] = current + amount
        return self
    
    def get_threat(self, entity_id):
        """
        Get the threat value for an entity.
        
        Args:
            entity_id: ID of the entity to get threat for
            
        Returns:
            float: Threat value
        """
        return self.threat_table.get(entity_id, 0)
    
    def get_highest_threat_entity(self):
        """
        Get the entity with the highest threat.
        
        Returns:
            tuple: (entity_id, threat_value) or (None, 0) if no threats
        """
        if not self.threat_table:
            return None, 0
        
        highest_entity = max(self.threat_table.items(), key=lambda x: x[1])
        return highest_entity
    
    def reset_threat_table(self):
        """
        Reset the threat table.
        
        Returns:
            CombatComponent: Self for method chaining
        """
        self.threat_table.clear()
        return self
    
    def set_stance(self, stance):
        """
        Set combat stance.
        
        Args:
            stance: The stance to set
            
        Returns:
            CombatComponent: Self for method chaining
        """
        self.stance = stance
        return self
    
    def set_preferred_attack_type(self, attack_type):
        """
        Set preferred attack type.
        
        Args:
            attack_type: The attack type to set
            
        Returns:
            CombatComponent: Self for method chaining
        """
        self.preferred_attack_type = attack_type
        return self
    
    def update_cooldowns(self, dt):
        """
        Update all cooldowns.
        
        Args:
            dt: Delta time in seconds
            
        Returns:
            CombatComponent: Self for method chaining
        """
        # Update global cooldown
        self.global_cooldown = max(0.0, self.global_cooldown - dt)
        
        # Update attack cooldowns
        for attack_id in list(self.attack_cooldowns.keys()):
            self.attack_cooldowns[attack_id] -= dt
            if self.attack_cooldowns[attack_id] <= 0:
                del self.attack_cooldowns[attack_id]
        
        return self
    
    def is_on_cooldown(self, attack_id):
        """
        Check if an attack is on cooldown.
        
        Args:
            attack_id: ID of the attack to check
            
        Returns:
            bool: True if the attack is on cooldown
        """
        return attack_id in self.attack_cooldowns or self.global_cooldown > 0
    
    def start_cooldown(self, attack_id, duration):
        """
        Start a cooldown for an attack.
        
        Args:
            attack_id: ID of the attack
            duration: Duration of the cooldown in seconds
            
        Returns:
            CombatComponent: Self for method chaining
        """
        self.attack_cooldowns[attack_id] = duration
        return self
    
    def start_global_cooldown(self, duration=1.0):
        """
        Start the global cooldown.
        
        Args:
            duration: Duration of the global cooldown in seconds
            
        Returns:
            CombatComponent: Self for method chaining
        """
        self.global_cooldown = duration
        return self
    
    def reset_opportunity_attacks(self):
        """
        Reset opportunity attacks.
        
        Returns:
            CombatComponent: Self for method chaining
        """
        self.opportunity_attacks_used = 0
        return self
    
    def use_opportunity_attack(self):
        """
        Use an opportunity attack.
        
        Returns:
            bool: True if an opportunity attack was available and used
        """
        if self.opportunity_attacks_used < self.opportunity_attacks:
            self.opportunity_attacks_used += 1
            return True
        return False
    
    def can_use_opportunity_attack(self):
        """
        Check if an opportunity attack can be used.
        
        Returns:
            bool: True if an opportunity attack is available
        """
        return self.opportunity_attacks_used < self.opportunity_attacks
    
    def record_damage_dealt(self, amount, critical=False):
        """
        Record damage dealt in combat statistics.
        
        Args:
            amount: Amount of damage dealt
            critical: Whether it was a critical hit
            
        Returns:
            CombatComponent: Self for method chaining
        """
        self.damage_dealt += amount
        self.attacks_landed += 1
        self.last_damage_dealt_time = time.time()
        
        if critical:
            self.critical_hits += 1
        
        return self
    
    def record_damage_taken(self, amount):
        """
        Record damage taken in combat statistics.
        
        Args:
            amount: Amount of damage taken
            
        Returns:
            CombatComponent: Self for method chaining
        """
        self.damage_taken += amount
        self.last_damage_taken_time = time.time()
        return self
    
    def record_healing_done(self, amount):
        """
        Record healing done in combat statistics.
        
        Args:
            amount: Amount of healing done
            
        Returns:
            CombatComponent: Self for method chaining
        """
        self.healing_done += amount
        return self
    
    def record_attack_missed(self):
        """
        Record a missed attack in combat statistics.
        
        Returns:
            CombatComponent: Self for method chaining
        """
        self.attacks_missed += 1
        return self
    
    def record_kill(self):
        """
        Record a kill in combat statistics.
        
        Returns:
            CombatComponent: Self for method chaining
        """
        self.kills += 1
        return self
    
    def toggle_auto_attack(self):
        """
        Toggle auto-attack on/off.
        
        Returns:
            bool: New auto-attack state
        """
        self.auto_attack_enabled = not self.auto_attack_enabled
        return self.auto_attack_enabled
    
    def should_auto_attack(self, current_time):
        """
        Check if an auto-attack should occur.
        
        Args:
            current_time: Current time
            
        Returns:
            bool: True if an auto-attack should occur
        """
        if not self.auto_attack_enabled or not self.in_combat or not self.current_target_id:
            return False
        
        return current_time - self.last_auto_attack_time >= self.auto_attack_interval
    
    def update_last_auto_attack_time(self):
        """
        Update the last auto-attack time to the current time.
        
        Returns:
            CombatComponent: Self for method chaining
        """
        self.last_auto_attack_time = time.time()
        return self
    
    def update_last_combat_action_time(self):
        """
        Update the last combat action time to the current time.
        
        Returns:
            CombatComponent: Self for method chaining
        """
        self.last_combat_action_time = time.time()
        return self
    
    def time_since_last_combat_action(self):
        """
        Get time since the last combat action.
        
        Returns:
            float: Time in seconds since the last combat action
        """
        return time.time() - self.last_combat_action_time
    
    def time_in_combat(self):
        """
        Get time in current combat.
        
        Returns:
            float: Time in seconds in current combat, or 0 if not in combat
        """
        if not self.in_combat:
            return 0
        return time.time() - self.combat_start_time
    
    def get_attack_range(self, attack_type=None):
        """
        Get the range for an attack type.
        
        Args:
            attack_type: The attack type to get range for, or None for preferred type
            
        Returns:
            float: Attack range in tiles
        """
        if attack_type is None:
            attack_type = self.preferred_attack_type
        
        if attack_type == AttackType.MELEE:
            return self.melee_range
        elif attack_type == AttackType.RANGED:
            return self.ranged_range
        elif attack_type == AttackType.SPELL:
            return self.spell_range
        
        return self.melee_range
    
    def set_attack_range(self, attack_type, range_value):
        """
        Set the range for an attack type.
        
        Args:
            attack_type: The attack type to set range for
            range_value: The range value in tiles
            
        Returns:
            CombatComponent: Self for method chaining
        """
        if attack_type == AttackType.MELEE:
            self.melee_range = range_value
        elif attack_type == AttackType.RANGED:
            self.ranged_range = range_value
        elif attack_type == AttackType.SPELL:
            self.spell_range = range_value
        
        return self 