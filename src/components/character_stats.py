"""
Character stats component for the Entity Component System.
"""

from ..ecs.component import Component

class CharacterStatsComponent(Component):
    """
    Component that stores character statistics.
    
    This component contains all the stats that define a character's
    capabilities, such as strength, dexterity, health, etc.
    """
    
    def __init__(self, base_stats=None):
        """
        Initialize the character stats component.
        
        Args:
            base_stats: Dictionary of base stat values
        """
        super().__init__()
        
        # Base stats (permanent values)
        self.base_stats = base_stats or {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10,
            "max_health": 100,
            "max_mana": 100,
            "armor_class": 10,
            "attack_power": 10,
            "attack_speed": 1.0,
            "movement_speed": 3.0
        }
        
        # Current stats (base + modifiers)
        self.current_stats = self.base_stats.copy()
        
        # Stat modifiers (temporary effects)
        self.modifiers = {}  # Modifier ID -> {stat, value, duration}
        
        # Current health and mana
        self.health = self.current_stats["max_health"]
        self.mana = self.current_stats["max_mana"]
        
        # Status effects
        self.status_effects = {}  # Effect ID -> {type, duration, strength}
    
    def serialize(self):
        """
        Convert component data to a serializable format.
        
        Returns:
            dict: Serialized component data
        """
        return {
            "base_stats": self.base_stats,
            "current_stats": self.current_stats,
            "modifiers": self.modifiers,
            "health": self.health,
            "mana": self.mana,
            "status_effects": self.status_effects
        }
    
    @classmethod
    def deserialize(cls, data):
        """
        Create a component from serialized data.
        
        Args:
            data: Serialized component data
            
        Returns:
            CharacterStatsComponent: New component instance
        """
        component = cls(data.get("base_stats", {}))
        component.current_stats = data.get("current_stats", component.base_stats.copy())
        component.modifiers = data.get("modifiers", {})
        component.health = data.get("health", component.current_stats.get("max_health", 100))
        component.mana = data.get("mana", component.current_stats.get("max_mana", 100))
        component.status_effects = data.get("status_effects", {})
        return component
    
    def add_modifier(self, modifier_id, stat, value, duration=None):
        """
        Add a stat modifier.
        
        Args:
            modifier_id: Unique identifier for the modifier
            stat: The stat to modify
            value: The value to add to the stat
            duration: Duration in seconds, or None for permanent
            
        Returns:
            CharacterStatsComponent: Self for method chaining
        """
        self.modifiers[modifier_id] = {
            "stat": stat,
            "value": value,
            "duration": duration,
            "start_time": None  # Will be set when applied
        }
        
        # Apply the modifier
        self._apply_modifiers()
        
        return self
    
    def remove_modifier(self, modifier_id):
        """
        Remove a stat modifier.
        
        Args:
            modifier_id: The ID of the modifier to remove
            
        Returns:
            dict: The removed modifier data, or None if not found
        """
        if modifier_id in self.modifiers:
            modifier = self.modifiers[modifier_id]
            del self.modifiers[modifier_id]
            
            # Reapply all modifiers
            self._apply_modifiers()
            
            return modifier
        
        return None
    
    def _apply_modifiers(self):
        """Apply all stat modifiers to calculate current stats."""
        # Reset current stats to base stats
        self.current_stats = self.base_stats.copy()
        
        # Apply each modifier
        for modifier_id, modifier in self.modifiers.items():
            stat = modifier["stat"]
            value = modifier["value"]
            
            if stat in self.current_stats:
                self.current_stats[stat] += value
    
    def update_modifiers(self, dt):
        """
        Update modifiers, removing expired ones.
        
        Args:
            dt: Delta time in seconds
        """
        # Set start time for new modifiers
        import time
        current_time = time.time()
        
        for modifier_id, modifier in self.modifiers.items():
            if modifier["start_time"] is None:
                modifier["start_time"] = current_time
        
        # Check for expired modifiers
        expired = []
        
        for modifier_id, modifier in self.modifiers.items():
            if modifier["duration"] is not None:
                elapsed = current_time - modifier["start_time"]
                if elapsed >= modifier["duration"]:
                    expired.append(modifier_id)
        
        # Remove expired modifiers
        for modifier_id in expired:
            self.remove_modifier(modifier_id)
    
    def add_status_effect(self, effect_id, effect_type, strength=1.0, duration=None):
        """
        Add a status effect.
        
        Args:
            effect_id: Unique identifier for the effect
            effect_type: The type of effect (e.g., "poison", "stun")
            strength: The strength of the effect (0.0 to 1.0)
            duration: Duration in seconds, or None for permanent
            
        Returns:
            CharacterStatsComponent: Self for method chaining
        """
        self.status_effects[effect_id] = {
            "type": effect_type,
            "strength": strength,
            "duration": duration,
            "start_time": None  # Will be set when applied
        }
        
        return self
    
    def remove_status_effect(self, effect_id):
        """
        Remove a status effect.
        
        Args:
            effect_id: The ID of the effect to remove
            
        Returns:
            dict: The removed effect data, or None if not found
        """
        if effect_id in self.status_effects:
            effect = self.status_effects[effect_id]
            del self.status_effects[effect_id]
            return effect
        
        return None
    
    def update_status_effects(self, dt):
        """
        Update status effects, removing expired ones.
        
        Args:
            dt: Delta time in seconds
        """
        # Set start time for new effects
        import time
        current_time = time.time()
        
        for effect_id, effect in self.status_effects.items():
            if effect["start_time"] is None:
                effect["start_time"] = current_time
        
        # Check for expired effects
        expired = []
        
        for effect_id, effect in self.status_effects.items():
            if effect["duration"] is not None:
                elapsed = current_time - effect["start_time"]
                if elapsed >= effect["duration"]:
                    expired.append(effect_id)
        
        # Remove expired effects
        for effect_id in expired:
            self.remove_status_effect(effect_id)
    
    def has_status_effect(self, effect_type):
        """
        Check if the character has a specific type of status effect.
        
        Args:
            effect_type: The type of effect to check for
            
        Returns:
            bool: True if the character has the effect, False otherwise
        """
        for effect in self.status_effects.values():
            if effect["type"] == effect_type:
                return True
        
        return False
    
    def get_status_effect_strength(self, effect_type):
        """
        Get the strength of a specific type of status effect.
        
        Args:
            effect_type: The type of effect to get the strength for
            
        Returns:
            float: The strength of the effect, or 0.0 if not found
        """
        max_strength = 0.0
        
        for effect in self.status_effects.values():
            if effect["type"] == effect_type and effect["strength"] > max_strength:
                max_strength = effect["strength"]
        
        return max_strength
    
    def take_damage(self, amount):
        """
        Reduce health by a specified amount.
        
        Args:
            amount: The amount of damage to take
            
        Returns:
            float: The actual amount of damage taken
        """
        # Ensure amount is positive
        amount = max(0, amount)
        
        # Calculate actual damage (could apply damage reduction here)
        actual_damage = amount
        
        # Reduce health
        self.health = max(0, self.health - actual_damage)
        
        return actual_damage
    
    def heal(self, amount):
        """
        Increase health by a specified amount.
        
        Args:
            amount: The amount to heal
            
        Returns:
            float: The actual amount healed
        """
        # Ensure amount is positive
        amount = max(0, amount)
        
        # Calculate actual healing (could apply healing modifiers here)
        actual_healing = amount
        
        # Increase health, capped at max_health
        old_health = self.health
        self.health = min(self.current_stats["max_health"], self.health + actual_healing)
        
        return self.health - old_health
    
    def use_mana(self, amount):
        """
        Reduce mana by a specified amount.
        
        Args:
            amount: The amount of mana to use
            
        Returns:
            bool: True if enough mana was available, False otherwise
        """
        # Ensure amount is positive
        amount = max(0, amount)
        
        # Check if enough mana is available
        if self.mana < amount:
            return False
        
        # Reduce mana
        self.mana -= amount
        
        return True
    
    def restore_mana(self, amount):
        """
        Increase mana by a specified amount.
        
        Args:
            amount: The amount to restore
            
        Returns:
            float: The actual amount restored
        """
        # Ensure amount is positive
        amount = max(0, amount)
        
        # Calculate actual restoration (could apply mana modifiers here)
        actual_restoration = amount
        
        # Increase mana, capped at max_mana
        old_mana = self.mana
        self.mana = min(self.current_stats["max_mana"], self.mana + actual_restoration)
        
        return self.mana - old_mana
    
    def is_alive(self):
        """
        Check if the character is alive.
        
        Returns:
            bool: True if alive, False if dead
        """
        return self.health > 0 