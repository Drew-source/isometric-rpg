"""
Event type constants for the isometric RPG.

This module defines constants for all event types used in the game's event system.
"""

class EventType:
    """
    Event type constants used throughout the game.
    
    These constants are used as keys for the event system to identify
    different types of events.
    """
    
    # System events
    GAME_INITIALIZED = "game_initialized"
    GAME_STARTED = "game_started"
    GAME_PAUSED = "game_paused"
    GAME_RESUMED = "game_resumed"
    GAME_QUIT = "game_quit"
    
    # Input events
    KEY_PRESSED = "key_pressed"
    KEY_RELEASED = "key_released"
    MOUSE_MOVED = "mouse_moved"
    MOUSE_PRESSED = "mouse_pressed"
    MOUSE_RELEASED = "mouse_released"
    
    # Game state events
    GAME_STATE_CHANGED = "game_state_changed"
    SCENE_LOADED = "scene_loaded"
    SCENE_UNLOADED = "scene_unloaded"
    
    # Movement events
    ENTITY_MOVED = "entity_moved"
    ENTITY_TELEPORTED = "entity_teleported"
    ENTITY_COLLISION = "entity_collision"
    ENTITY_STOPPED = "entity_stopped"
    ENTITY_PATH_FOUND = "entity_path_found"
    ENTITY_PATH_FAILED = "entity_path_failed"
    
    # Combat events
    ATTACK_STARTED = "attack_started"
    ATTACK_LANDED = "attack_landed"
    ATTACK_MISSED = "attack_missed"
    DAMAGE_DEALT = "damage_dealt"
    DAMAGE_TAKEN = "damage_taken"
    HEALING_RECEIVED = "healing_received"
    HEALING_PERFORMED = "healing_performed"
    HEALTH_CHANGED = "health_changed"
    MANA_CHANGED = "mana_changed"
    ENTITY_DIED = "entity_died"
    COMBAT_ENTERED = "combat_entered"
    COMBAT_EXITED = "combat_exited"
    COMBAT_STANCE_CHANGED = "combat_stance_changed"
    OPPORTUNITY_ATTACK_USED = "opportunity_attack_used"
    CRITICAL_HIT = "critical_hit"
    EFFECT_APPLIED = "effect_applied"
    EFFECT_REMOVED = "effect_removed"
    THREAT_CHANGED = "threat_changed"
    
    # Inventory events
    ITEM_ADDED = "item_added"
    ITEM_REMOVED = "item_removed"
    ITEM_USED = "item_used"
    ITEM_DROPPED = "item_dropped"
    INVENTORY_CHANGED = "inventory_changed"
    
    # Quest events
    QUEST_STARTED = "quest_started"
    QUEST_COMPLETED = "quest_completed"
    QUEST_FAILED = "quest_failed"
    QUEST_OBJECTIVE_UPDATED = "quest_objective_updated"
    
    # Dialogue events
    DIALOGUE_STARTED = "dialogue_started"
    DIALOGUE_ENDED = "dialogue_ended"
    DIALOGUE_CHOICE_MADE = "dialogue_choice_made"
    
    # UI events
    UI_ELEMENT_CLICKED = "ui_element_clicked"
    UI_ELEMENT_HOVERED = "ui_element_hovered"
    UI_PANEL_OPENED = "ui_panel_opened"
    UI_PANEL_CLOSED = "ui_panel_closed"
    UI_NOTIFICATION = "ui_notification"
    
    # AI events
    AI_STATE_CHANGED = "ai_state_changed"
    AI_TARGET_ACQUIRED = "ai_target_acquired"
    AI_TARGET_LOST = "ai_target_lost"
    
    # Map events
    MAP_CREATED = "map_created"
    MAP_LOADED = "map_loaded"
    MAP_SAVED = "map_saved"
    MAP_CHANGED = "map_changed"
    TILE_CHANGED = "tile_changed"
    ENTITY_SPAWNED = "entity_spawned"
    
    # Collision events
    COLLISION_OCCURRED = "collision_occurred"
    COLLISION_ENDED = "collision_ended"
    TRIGGER_ENTERED = "trigger_entered"
    TRIGGER_EXITED = "trigger_exited"