"""
AI component for the Entity Component System.
"""

import time
import math
import random
from ..ecs.component import Component

class AIComponent(Component):
    """
    Component that provides AI behavior for entities.
    
    This component stores the data needed for AI decision making,
    including perception, memory, and available actions.
    """
    
    def __init__(self, ai_type="utility"):
        """
        Initialize the AI component.
        
        Args:
            ai_type: The type of AI to use ("utility", "state", "behavior_tree")
        """
        super().__init__()
        self.ai_type = ai_type
        self.enabled = True
        self.perception_radius = 10.0  # How far the AI can "see"
        self.perception = {  # What the AI currently perceives
            "enemies": [],
            "allies": [],
            "neutrals": [],
            "items": [],
            "hazards": []
        }
        self.memory = {}  # Entity ID -> {position, last_seen}
        self.memory_duration = 30.0  # How long to remember entities (seconds)
        
        # Utility AI specific
        self.actions = {}  # Action ID -> Action data
        self.utility_scores = {}  # Action ID -> Score
        self.current_action_id = None
        self.current_action_state = None
        self.action_threshold = 0.1  # Minimum score to consider an action
        
        # State machine specific
        self.states = {}  # State ID -> State data
        self.current_state_id = None
        self.previous_state_id = None
        
        # Behavior tree specific
        self.behavior_tree = None
        
        # Combat specific
        self.target_entity_id = None
        self.combat_style = "balanced"  # balanced, aggressive, defensive, ranged
        self.aggression_level = 0.5  # 0.0 to 1.0
        self.flee_health_threshold = 0.2  # Flee when health below 20%
        self.attack_cooldown = 0.0
        self.ability_cooldowns = {}  # Ability ID -> cooldown time remaining
        
        # Personality traits (affect decision making)
        self.personality = {
            "bravery": 0.5,        # 0.0 = cowardly, 1.0 = fearless
            "aggression": 0.5,      # 0.0 = passive, 1.0 = aggressive
            "cooperation": 0.5,     # 0.0 = selfish, 1.0 = selfless
            "curiosity": 0.5,       # 0.0 = cautious, 1.0 = curious
            "intelligence": 0.5     # 0.0 = instinctive, 1.0 = strategic
        }
    
    def serialize(self):
        """
        Convert component data to a serializable format.
        
        Returns:
            dict: Serialized component data
        """
        return {
            "ai_type": self.ai_type,
            "enabled": self.enabled,
            "perception_radius": self.perception_radius,
            "memory_duration": self.memory_duration,
            "actions": self.actions,
            "current_action_id": self.current_action_id,
            "current_action_state": self.current_action_state,
            "action_threshold": self.action_threshold,
            "states": self.states,
            "current_state_id": self.current_state_id,
            "previous_state_id": self.previous_state_id,
            "target_entity_id": self.target_entity_id,
            "combat_style": self.combat_style,
            "aggression_level": self.aggression_level,
            "flee_health_threshold": self.flee_health_threshold,
            "personality": self.personality
        }
    
    @classmethod
    def deserialize(cls, data):
        """
        Create a component from serialized data.
        
        Args:
            data: Serialized component data
            
        Returns:
            AIComponent: New component instance
        """
        component = cls(data.get("ai_type", "utility"))
        component.enabled = data.get("enabled", True)
        component.perception_radius = data.get("perception_radius", 10.0)
        component.memory_duration = data.get("memory_duration", 30.0)
        component.actions = data.get("actions", {})
        component.current_action_id = data.get("current_action_id")
        component.current_action_state = data.get("current_action_state")
        component.action_threshold = data.get("action_threshold", 0.1)
        component.states = data.get("states", {})
        component.current_state_id = data.get("current_state_id")
        component.previous_state_id = data.get("previous_state_id")
        component.target_entity_id = data.get("target_entity_id")
        component.combat_style = data.get("combat_style", "balanced")
        component.aggression_level = data.get("aggression_level", 0.5)
        component.flee_health_threshold = data.get("flee_health_threshold", 0.2)
        component.personality = data.get("personality", {
            "bravery": 0.5,
            "aggression": 0.5,
            "cooperation": 0.5,
            "curiosity": 0.5,
            "intelligence": 0.5
        })
        return component
    
    def add_action(self, action_id, action_data):
        """
        Add an action to the AI's repertoire.
        
        Args:
            action_id: Unique identifier for the action
            action_data: Data describing the action
            
        Returns:
            AIComponent: Self for method chaining
        """
        self.actions[action_id] = action_data
        return self
    
    def remove_action(self, action_id):
        """
        Remove an action from the AI's repertoire.
        
        Args:
            action_id: The ID of the action to remove
            
        Returns:
            dict: The removed action data, or None if not found
        """
        if action_id in self.actions:
            action_data = self.actions[action_id]
            del self.actions[action_id]
            return action_data
        return None
    
    def add_state(self, state_id, state_data):
        """
        Add a state to the AI's state machine.
        
        Args:
            state_id: Unique identifier for the state
            state_data: Data describing the state
            
        Returns:
            AIComponent: Self for method chaining
        """
        self.states[state_id] = state_data
        return self
    
    def remove_state(self, state_id):
        """
        Remove a state from the AI's state machine.
        
        Args:
            state_id: The ID of the state to remove
            
        Returns:
            dict: The removed state data, or None if not found
        """
        if state_id in self.states:
            state_data = self.states[state_id]
            del self.states[state_id]
            return state_data
        return None
    
    def set_current_state(self, state_id):
        """
        Set the current state of the AI's state machine.
        
        Args:
            state_id: The ID of the state to set as current
            
        Returns:
            bool: True if the state was set, False if the state doesn't exist
        """
        if state_id in self.states or state_id is None:
            self.previous_state_id = self.current_state_id
            self.current_state_id = state_id
            return True
        return False
    
    def remember_entity(self, entity_id, position):
        """
        Remember an entity's position.
        
        Args:
            entity_id: The ID of the entity to remember
            position: The position of the entity
        """
        self.memory[entity_id] = {
            "position": position,
            "last_seen": time.time()
        }
    
    def forget_old_entities(self):
        """Forget entities that haven't been seen for a while."""
        current_time = time.time()
        to_forget = []
        
        for entity_id, memory in self.memory.items():
            if current_time - memory["last_seen"] > self.memory_duration:
                to_forget.append(entity_id)
        
        for entity_id in to_forget:
            del self.memory[entity_id]
    
    def clear_perception(self):
        """Clear the current perception data."""
        for category in self.perception:
            self.perception[category] = []
    
    def update_cooldowns(self, dt):
        """
        Update all cooldowns.
        
        Args:
            dt: Delta time in seconds
        """
        # Update attack cooldown
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        
        # Update ability cooldowns
        for ability_id in list(self.ability_cooldowns.keys()):
            self.ability_cooldowns[ability_id] -= dt
            if self.ability_cooldowns[ability_id] <= 0:
                del self.ability_cooldowns[ability_id]
    
    def set_target(self, entity_id):
        """
        Set the current combat target.
        
        Args:
            entity_id: The ID of the entity to target
            
        Returns:
            bool: True if the target was set
        """
        self.target_entity_id = entity_id
        return True
    
    def clear_target(self):
        """Clear the current combat target."""
        self.target_entity_id = None
    
    def calculate_distance(self, pos1, pos2):
        """
        Calculate the distance between two positions.
        
        Args:
            pos1: First position (x, y, z)
            pos2: Second position (x, y, z)
            
        Returns:
            float: Distance between the positions
        """
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def find_nearest_enemy(self, own_position):
        """
        Find the nearest enemy in perception.
        
        Args:
            own_position: The AI entity's position
            
        Returns:
            tuple: (entity_id, distance) or (None, None) if no enemies
        """
        nearest_id = None
        nearest_distance = float('inf')
        
        for enemy_data in self.perception["enemies"]:
            enemy_id = enemy_data["id"]
            enemy_pos = enemy_data["position"]
            
            distance = self.calculate_distance(own_position, enemy_pos)
            
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_id = enemy_id
        
        return nearest_id, nearest_distance if nearest_id is not None else None
    
    def find_nearest_ally(self, own_position):
        """
        Find the nearest ally in perception.
        
        Args:
            own_position: The AI entity's position
            
        Returns:
            tuple: (entity_id, distance) or (None, None) if no allies
        """
        nearest_id = None
        nearest_distance = float('inf')
        
        for ally_data in self.perception["allies"]:
            ally_id = ally_data["id"]
            ally_pos = ally_data["position"]
            
            distance = self.calculate_distance(own_position, ally_pos)
            
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_id = ally_id
        
        return nearest_id, nearest_distance if nearest_id is not None else None
    
    def should_flee(self, own_health_ratio):
        """
        Determine if the AI should flee based on health and personality.
        
        Args:
            own_health_ratio: Current health / max health
            
        Returns:
            bool: True if the AI should flee
        """
        # Adjust flee threshold based on bravery
        adjusted_threshold = self.flee_health_threshold * (1.0 - self.personality["bravery"])
        
        # More brave characters will stay in combat longer
        return own_health_ratio <= adjusted_threshold
    
    def calculate_combat_utility(self, action_id, own_stats, target_stats=None, distance_to_target=None):
        """
        Calculate the utility of a combat action.
        
        Args:
            action_id: The ID of the action to evaluate
            own_stats: The AI entity's character stats
            target_stats: The target entity's character stats (if available)
            distance_to_target: Distance to the target (if available)
            
        Returns:
            float: Utility score between 0.0 and 1.0
        """
        if action_id not in self.actions:
            return 0.0
        
        action = self.actions[action_id]
        action_type = action.get("type", "")
        
        # Base utility
        utility = 0.5
        
        # Check if action is on cooldown
        if action_id in self.ability_cooldowns:
            return 0.0
        
        # Get health ratio
        own_health_ratio = own_stats.health / own_stats.current_stats["max_health"]
        
        # Adjust based on action type
        if action_type == "attack":
            # Higher utility when more aggressive or target is weak
            utility += self.personality["aggression"] * 0.3
            
            # If we know target stats, consider them
            if target_stats:
                target_health_ratio = target_stats.health / target_stats.current_stats["max_health"]
                # Higher utility when target is weak
                utility += (1.0 - target_health_ratio) * 0.2
            
            # Consider distance for melee vs ranged attacks
            if distance_to_target is not None:
                attack_range = action.get("range", 1.0)
                if distance_to_target <= attack_range:
                    utility += 0.2
                else:
                    utility -= 0.3
        
        elif action_type == "defend":
            # Higher utility when less aggressive or own health is low
            utility += (1.0 - self.personality["aggression"]) * 0.3
            utility += (1.0 - own_health_ratio) * 0.3
        
        elif action_type == "heal":
            # Higher utility when health is low
            missing_health_ratio = 1.0 - own_health_ratio
            utility += missing_health_ratio * 0.6
        
        elif action_type == "flee":
            # Higher utility when health is low and bravery is low
            utility += (1.0 - own_health_ratio) * 0.4
            utility += (1.0 - self.personality["bravery"]) * 0.3
        
        # Adjust based on intelligence (smarter AIs make better decisions)
        # This simulates the AI making a more optimal choice
        optimal_choice_bonus = random.uniform(0.0, self.personality["intelligence"] * 0.2)
        utility += optimal_choice_bonus
        
        # Clamp utility between 0 and 1
        return max(0.0, min(1.0, utility))
    
    def select_best_combat_action(self, own_stats, target_stats=None, distance_to_target=None):
        """
        Select the best combat action based on utility.
        
        Args:
            own_stats: The AI entity's character stats
            target_stats: The target entity's character stats (if available)
            distance_to_target: Distance to the target (if available)
            
        Returns:
            str: The ID of the best action, or None if no action meets the threshold
        """
        best_action_id = None
        best_utility = self.action_threshold
        
        for action_id in self.actions:
            utility = self.calculate_combat_utility(
                action_id, own_stats, target_stats, distance_to_target
            )
            
            self.utility_scores[action_id] = utility
            
            if utility > best_utility:
                best_utility = utility
                best_action_id = action_id
        
        return best_action_id
    
    def decide_combat_action(self, own_position, own_stats, world):
        """
        Decide what combat action to take.
        
        Args:
            own_position: The AI entity's position
            own_stats: The AI entity's character stats
            world: The game world (for querying entity data)
            
        Returns:
            dict: Action decision with type and parameters
        """
        # Check if we should flee based on health
        own_health_ratio = own_stats.health / own_stats.current_stats["max_health"]
        if self.should_flee(own_health_ratio):
            return {
                "type": "flee",
                "target_position": None  # Will be determined by the AI system
            }
        
        # Find nearest enemy if we don't have a target
        if self.target_entity_id is None:
            self.target_entity_id, _ = self.find_nearest_enemy(own_position)
        
        # If we have a target, get its data
        target_stats = None
        distance_to_target = None
        target_position = None
        
        if self.target_entity_id:
            # In a real implementation, we would query the world for the target entity
            # For now, we'll assume we can get this data from perception
            for enemy_data in self.perception["enemies"]:
                if enemy_data["id"] == self.target_entity_id:
                    target_position = enemy_data["position"]
                    distance_to_target = self.calculate_distance(own_position, target_position)
                    
                    # In a real implementation, we would get the actual stats component
                    # For now, we'll use a placeholder
                    if "stats" in enemy_data:
                        target_stats = enemy_data["stats"]
                    
                    break
        
        # Select the best action
        best_action_id = self.select_best_combat_action(
            own_stats, target_stats, distance_to_target
        )
        
        # If we found a good action, return it
        if best_action_id:
            action = self.actions[best_action_id]
            action_type = action.get("type", "")
            
            self.current_action_id = best_action_id
            
            # Return the action decision
            if action_type == "attack":
                return {
                    "type": "attack",
                    "target_id": self.target_entity_id,
                    "attack_type": action.get("attack_type", "melee"),
                    "ability_id": action.get("ability_id")
                }
            elif action_type == "defend":
                return {
                    "type": "defend",
                    "defense_type": action.get("defense_type", "block")
                }
            elif action_type == "heal":
                return {
                    "type": "heal",
                    "heal_type": action.get("heal_type", "self"),
                    "target_id": self.target_entity_id if action.get("heal_type") == "other" else None
                }
            elif action_type == "flee":
                return {
                    "type": "flee",
                    "target_position": None  # Will be determined by the AI system
                }
        
        # Default to doing nothing
        return {
            "type": "idle"
        }
    
    def set_personality(self, trait, value):
        """
        Set a personality trait value.
        
        Args:
            trait: The trait to set
            value: The value to set (0.0 to 1.0)
            
        Returns:
            bool: True if the trait was set, False if the trait doesn't exist
        """
        if trait in self.personality:
            self.personality[trait] = max(0.0, min(1.0, value))
            return True
        return False
    
    def randomize_personality(self, variance=0.2):
        """
        Randomize personality traits within a variance.
        
        Args:
            variance: How much to vary traits (0.0 to 1.0)
        """
        for trait in self.personality:
            base = self.personality[trait]
            min_val = max(0.0, base - variance)
            max_val = min(1.0, base + variance)
            self.personality[trait] = random.uniform(min_val, max_val) 