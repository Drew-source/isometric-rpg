"""
AI system for the Entity Component System.

This system processes AI components to make decisions for NPCs.
"""

import math
import time
from ..ecs.system import System
from ..components import AIComponent, CharacterStatsComponent, TransformComponent
from ..events.event_types import EventType

class AISystem(System):
    """
    System that processes AI components to control NPCs.
    
    This system handles AI decision making, including combat decisions,
    movement, and other behaviors.
    """
    
    def __init__(self, world, event_manager):
        """
        Initialize the AI system.
        
        Args:
            world: The game world
            event_manager: The event manager for emitting events
        """
        super().__init__(world)
        self.required_components = [AIComponent]
        self.event_manager = event_manager
        self.spatial_grid = None  # Will be set during initialization
        self.action_handlers = {
            "attack": self._handle_attack_action,
            "defend": self._handle_defend_action,
            "heal": self._handle_heal_action,
            "flee": self._handle_flee_action,
            "idle": self._handle_idle_action,
            "patrol": self._handle_patrol_action,
            "follow": self._handle_follow_action
        }
    
    def initialize(self, spatial_grid=None):
        """
        Initialize the system.
        
        Args:
            spatial_grid: Reference to the spatial grid for efficient entity queries
        """
        self.spatial_grid = spatial_grid
    
    def update(self, dt):
        """
        Update all AI entities.
        
        Args:
            dt: Delta time in seconds
        """
        # Get all entities with AI components
        entities = self.world.get_entities_with_components(self.required_components)
        
        for entity_id in entities:
            # Get the AI component
            ai_component = self.world.get_component(entity_id, AIComponent)
            
            # Skip if AI is disabled
            if not ai_component.enabled:
                continue
            
            # Update cooldowns
            ai_component.update_cooldowns(dt)
            
            # Update perception (in a real implementation, this would be done by a perception system)
            self._update_perception(entity_id, ai_component)
            
            # Forget old entities
            ai_component.forget_old_entities()
            
            # Process AI based on its type
            if ai_component.ai_type == "utility":
                self._process_utility_ai(entity_id, ai_component, dt)
            elif ai_component.ai_type == "state":
                self._process_state_machine(entity_id, ai_component, dt)
            elif ai_component.ai_type == "behavior_tree":
                self._process_behavior_tree(entity_id, ai_component, dt)
    
    def _update_perception(self, entity_id, ai_component):
        """
        Update the AI's perception of the world.
        
        Args:
            entity_id: The ID of the entity
            ai_component: The AI component
        """
        # Clear current perception
        ai_component.clear_perception()
        
        # Get the entity's position
        transform_component = self.world.get_component(entity_id, TransformComponent)
        if not transform_component:
            return
        
        entity_position = (transform_component.position[0], transform_component.position[1], transform_component.z)
        
        # Get all entities with transform components
        entities = self.world.get_entities_with_components([TransformComponent])
        
        for other_id in entities:
            # Skip self
            if other_id == entity_id:
                continue
            
            # Get the other entity's position
            other_transform = self.world.get_component(other_id, TransformComponent)
            other_position = (other_transform.position[0], other_transform.position[1], other_transform.z)
            
            # Calculate distance
            distance = ai_component.calculate_distance(entity_position, other_position)
            
            # Check if within perception radius
            if distance <= ai_component.perception_radius:
                # Determine entity type (in a real implementation, this would use faction or team components)
                entity_type = self._determine_entity_type(entity_id, other_id)
                
                # Add to perception
                if entity_type == "enemy":
                    # Get stats if available
                    stats = None
                    stats_component = self.world.get_component(other_id, CharacterStatsComponent)
                    if stats_component:
                        stats = stats_component
                    
                    ai_component.perception["enemies"].append({
                        "id": other_id,
                        "position": other_position,
                        "distance": distance,
                        "stats": stats
                    })
                    
                    # Remember entity
                    ai_component.remember_entity(other_id, other_position)
                
                elif entity_type == "ally":
                    # Get stats if available
                    stats = None
                    stats_component = self.world.get_component(other_id, CharacterStatsComponent)
                    if stats_component:
                        stats = stats_component
                    
                    ai_component.perception["allies"].append({
                        "id": other_id,
                        "position": other_position,
                        "distance": distance,
                        "stats": stats
                    })
                    
                    # Remember entity
                    ai_component.remember_entity(other_id, other_position)
                
                elif entity_type == "neutral":
                    ai_component.perception["neutrals"].append({
                        "id": other_id,
                        "position": other_position,
                        "distance": distance
                    })
                    
                    # Remember entity
                    ai_component.remember_entity(other_id, other_position)
                
                elif entity_type == "item":
                    ai_component.perception["items"].append({
                        "id": other_id,
                        "position": other_position,
                        "distance": distance
                    })
                
                elif entity_type == "hazard":
                    ai_component.perception["hazards"].append({
                        "id": other_id,
                        "position": other_position,
                        "distance": distance
                    })
    
    def _determine_entity_type(self, entity_id, other_id):
        """
        Determine the type of an entity in relation to another.
        
        Args:
            entity_id: The ID of the entity
            other_id: The ID of the other entity
            
        Returns:
            str: The type of the other entity ("enemy", "ally", "neutral", "item", "hazard")
        """
        # In a real implementation, this would use faction or team components
        # For now, we'll use a simple placeholder implementation
        
        # Check if the other entity has an AI component (is an NPC)
        other_ai = self.world.get_component(other_id, AIComponent)
        
        if other_ai:
            # For now, all NPCs are enemies
            return "enemy"
        
        # Check if the other entity has a character stats component (is a character)
        other_stats = self.world.get_component(other_id, CharacterStatsComponent)
        
        if other_stats:
            # For now, all characters without AI are allies
            return "ally"
        
        # Default to neutral
        return "neutral"
    
    def _process_utility_ai(self, entity_id, ai_component, dt):
        """
        Process utility-based AI.
        
        Args:
            entity_id: The ID of the entity
            ai_component: The AI component
            dt: Delta time in seconds
        """
        # Get the entity's position
        transform_component = self.world.get_component(entity_id, TransformComponent)
        if not transform_component:
            return
        
        entity_position = (transform_component.position[0], transform_component.position[1], transform_component.z)
        
        # Get the entity's stats
        stats_component = self.world.get_component(entity_id, CharacterStatsComponent)
        if not stats_component:
            return
        
        # Decide what action to take
        action_decision = ai_component.decide_combat_action(entity_position, stats_component, self.world)
        
        # Handle the action
        action_type = action_decision.get("type", "idle")
        
        if action_type in self.action_handlers:
            self.action_handlers[action_type](entity_id, ai_component, action_decision)
    
    def _process_state_machine(self, entity_id, ai_component, dt):
        """
        Process state machine AI.
        
        Args:
            entity_id: The ID of the entity
            ai_component: The AI component
            dt: Delta time in seconds
        """
        # Get the current state
        current_state_id = ai_component.current_state_id
        
        if current_state_id is None or current_state_id not in ai_component.states:
            # Default to idle state
            ai_component.set_current_state("idle")
            current_state_id = "idle"
        
        # Get the state data
        state = ai_component.states.get(current_state_id)
        
        if state:
            # Execute the state's action
            action_type = state.get("action_type", "idle")
            
            if action_type in self.action_handlers:
                self.action_handlers[action_type](entity_id, ai_component, state)
            
            # Check transitions
            transitions = state.get("transitions", [])
            
            for transition in transitions:
                condition = transition.get("condition")
                target_state_id = transition.get("target_state_id")
                
                # Check if the condition is met
                if self._check_transition_condition(entity_id, ai_component, condition):
                    # Transition to the target state
                    ai_component.set_current_state(target_state_id)
                    break
    
    def _process_behavior_tree(self, entity_id, ai_component, dt):
        """
        Process behavior tree AI.
        
        Args:
            entity_id: The ID of the entity
            ai_component: The AI component
            dt: Delta time in seconds
        """
        # In a real implementation, this would process a behavior tree
        # For now, we'll use a simple placeholder implementation
        pass
    
    def _check_transition_condition(self, entity_id, ai_component, condition):
        """
        Check if a state transition condition is met.
        
        Args:
            entity_id: The ID of the entity
            ai_component: The AI component
            condition: The condition to check
            
        Returns:
            bool: True if the condition is met, False otherwise
        """
        if not condition:
            return False
        
        condition_type = condition.get("type")
        
        if condition_type == "enemy_nearby":
            # Check if there are enemies nearby
            return len(ai_component.perception["enemies"]) > 0
        
        elif condition_type == "health_low":
            # Check if health is low
            stats_component = self.world.get_component(entity_id, CharacterStatsComponent)
            if stats_component:
                health_ratio = stats_component.health / stats_component.current_stats["max_health"]
                threshold = condition.get("threshold", 0.3)
                return health_ratio <= threshold
        
        elif condition_type == "target_dead":
            # Check if the target is dead
            target_id = ai_component.target_entity_id
            if target_id:
                target_stats = self.world.get_component(target_id, CharacterStatsComponent)
                if target_stats:
                    return not target_stats.is_alive()
                return True  # Target doesn't have stats, assume dead
            return True  # No target, assume condition is met
        
        return False
    
    def _handle_attack_action(self, entity_id, ai_component, action_data):
        """
        Handle an attack action.
        
        Args:
            entity_id: The ID of the entity
            ai_component: The AI component
            action_data: The action data
        """
        # Get the target ID
        target_id = action_data.get("target_id")
        
        if not target_id:
            return
        
        # Check if attack is on cooldown
        if ai_component.attack_cooldown > 0:
            return
        
        # Get the entity's position
        transform_component = self.world.get_component(entity_id, TransformComponent)
        if not transform_component:
            return
        
        entity_position = (transform_component.position[0], transform_component.position[1], transform_component.z)
        
        # Get the target's position
        target_transform = self.world.get_component(target_id, TransformComponent)
        if not target_transform:
            return
        
        target_position = (target_transform.position[0], target_transform.position[1], target_transform.z)
        
        # Calculate distance to target
        distance = ai_component.calculate_distance(entity_position, target_position)
        
        # Get attack range
        attack_type = action_data.get("attack_type", "melee")
        attack_range = 1.0  # Default melee range
        
        if attack_type == "ranged":
            attack_range = 5.0  # Default ranged range
        
        # Check if target is in range
        if distance > attack_range:
            # Move towards target
            direction = (
                (target_position[0] - entity_position[0]) / distance,
                (target_position[1] - entity_position[1]) / distance
            )
            
            # Update position
            new_position = (
                transform_component.position[0] + direction[0] * 2.0 * 0.016,  # Assuming 60 FPS
                transform_component.position[1] + direction[1] * 2.0 * 0.016
            )
            
            transform_component.set_position(new_position)
        else:
            # Target is in range, perform attack
            
            # Get the entity's stats
            stats_component = self.world.get_component(entity_id, CharacterStatsComponent)
            if not stats_component:
                return
            
            # Get the target's stats
            target_stats = self.world.get_component(target_id, CharacterStatsComponent)
            if not target_stats:
                return
            
            # Calculate damage
            base_damage = stats_component.current_stats["attack_power"]
            
            # Apply damage to target
            target_stats.take_damage(base_damage)
            
            # Set attack cooldown
            attack_speed = stats_component.current_stats["attack_speed"]
            ai_component.attack_cooldown = 1.0 / attack_speed
    
    def _handle_defend_action(self, entity_id, ai_component, action_data):
        """
        Handle a defend action.
        
        Args:
            entity_id: The ID of the entity
            ai_component: The AI component
            action_data: The action data
        """
        # In a real implementation, this would apply defensive buffs or stance changes
        pass
    
    def _handle_heal_action(self, entity_id, ai_component, action_data):
        """
        Handle a heal action.
        
        Args:
            entity_id: The ID of the entity
            ai_component: The AI component
            action_data: The action data
        """
        heal_type = action_data.get("heal_type", "self")
        
        if heal_type == "self":
            # Heal self
            stats_component = self.world.get_component(entity_id, CharacterStatsComponent)
            if stats_component:
                # Calculate heal amount
                heal_amount = 10.0  # Default heal amount
                
                # Apply healing
                stats_component.heal(heal_amount)
        else:
            # Heal other
            target_id = action_data.get("target_id")
            
            if target_id:
                target_stats = self.world.get_component(target_id, CharacterStatsComponent)
                if target_stats:
                    # Calculate heal amount
                    heal_amount = 10.0  # Default heal amount
                    
                    # Apply healing
                    target_stats.heal(heal_amount)
    
    def _handle_flee_action(self, entity_id, ai_component, action_data):
        """
        Handle a flee action.
        
        Args:
            entity_id: The ID of the entity
            ai_component: The AI component
            action_data: The action data
        """
        # Get the entity's position
        transform_component = self.world.get_component(entity_id, TransformComponent)
        if not transform_component:
            return
        
        entity_position = (transform_component.position[0], transform_component.position[1], transform_component.z)
        
        # Find the nearest enemy
        nearest_enemy_id, nearest_enemy_distance = ai_component.find_nearest_enemy(entity_position)
        
        if nearest_enemy_id:
            # Get the enemy's position
            enemy_transform = self.world.get_component(nearest_enemy_id, TransformComponent)
            if not enemy_transform:
                return
            
            enemy_position = (enemy_transform.position[0], enemy_transform.position[1], enemy_transform.z)
            
            # Calculate direction away from enemy
            direction = (
                (entity_position[0] - enemy_position[0]) / nearest_enemy_distance,
                (entity_position[1] - enemy_position[1]) / nearest_enemy_distance
            )
            
            # Update position
            new_position = (
                transform_component.position[0] + direction[0] * 3.0 * 0.016,  # Faster than normal movement
                transform_component.position[1] + direction[1] * 3.0 * 0.016
            )
            
            transform_component.set_position(new_position)
            
            # Clear target
            ai_component.clear_target()
    
    def _handle_idle_action(self, entity_id, ai_component, action_data):
        """
        Handle an idle action.
        
        Args:
            entity_id: The ID of the entity
            ai_component: The AI component
            action_data: The action data
        """
        # Do nothing
        pass
    
    def _handle_patrol_action(self, entity_id, ai_component, action_data):
        """
        Handle a patrol action.
        
        Args:
            entity_id: The ID of the entity
            ai_component: The AI component
            action_data: The action data
        """
        # In a real implementation, this would move the entity along a patrol path
        pass
    
    def _handle_follow_action(self, entity_id, ai_component, action_data):
        """
        Handle a follow action.
        
        Args:
            entity_id: The ID of the entity
            ai_component: The AI component
            action_data: The action data
        """
        # Get the target ID
        target_id = action_data.get("target_id")
        
        if not target_id:
            return
        
        # Get the entity's position
        transform_component = self.world.get_component(entity_id, TransformComponent)
        if not transform_component:
            return
        
        entity_position = (transform_component.position[0], transform_component.position[1], transform_component.z)
        
        # Get the target's position
        target_transform = self.world.get_component(target_id, TransformComponent)
        if not target_transform:
            return
        
        target_position = (target_transform.position[0], target_transform.position[1], target_transform.z)
        
        # Calculate distance to target
        distance = ai_component.calculate_distance(entity_position, target_position)
        
        # Check if we need to move
        if distance > 2.0:  # Stay within 2 units of target
            # Calculate direction to target
            direction = (
                (target_position[0] - entity_position[0]) / distance,
                (target_position[1] - entity_position[1]) / distance
            )
            
            # Update position
            new_position = (
                transform_component.position[0] + direction[0] * 2.0 * 0.016,  # Assuming 60 FPS
                transform_component.position[1] + direction[1] * 2.0 * 0.016
            )
            
            transform_component.set_position(new_position)
    
    def _get_distance(self, entity1, entity2):
        """
        Calculate distance between two entities.
        
        Args:
            entity1: First entity
            entity2: Second entity
            
        Returns:
            float: Distance between entities
        """
        t1 = entity1.get_component("TransformComponent")
        t2 = entity2.get_component("TransformComponent")
        
        if not t1 or not t2:
            return float('inf')
        
        dx = t1.position.x - t2.position.x
        dy = t1.position.y - t2.position.y
        return math.sqrt(dx*dx + dy*dy)
    
    def _get_health_percent(self, entity):
        """
        Get entity health as percentage.
        
        Args:
            entity: The entity to get health for
            
        Returns:
            float: Health percentage (0-1)
        """
        stats = entity.get_component("CharacterStatsComponent")
        if not stats:
            return 1.0
        
        max_health = stats.current_stats.get("max_health", 1)
        if max_health <= 0:
            return 0
        
        return stats.health / max_health 