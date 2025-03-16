"""
Event type definitions for the event system.
"""

class EventType:
    """
    Enumeration of event types used in the game.
    
    These constants define the different types of events that can be
    emitted and subscribed to in the event system.
    """
    
    # System events
    ENTITY_CREATED = "entity_created"
    ENTITY_DESTROYED = "entity_destroyed"
    COMPONENT_ADDED = "component_added"
    COMPONENT_REMOVED = "component_removed"
    WORLD_CLEARING = "world_clearing"
    WORLD_CLEARED = "world_cleared"
    FLAG_CHANGED = "flag_changed"
    
    # Input events
    KEY_PRESSED = "key_pressed"
    KEY_RELEASED = "key_released"
    MOUSE_PRESSED = "mouse_pressed"
    MOUSE_RELEASED = "mouse_released"
    MOUSE_MOVED = "mouse_moved"
    
    # Game state events
    GAME_STARTED = "game_started"
    GAME_PAUSED = "game_paused"
    GAME_RESUMED = "game_resumed"
    GAME_SAVED = "game_saved"
    GAME_LOADED = "game_loaded"
    AREA_ENTERED = "area_entered"
    TIME_CHANGED = "time_changed"
    
    # Movement events
    ENTITY_MOVED = "entity_moved"
    PATH_FOUND = "path_found"
    PATH_FAILED = "path_failed"
    COLLISION_OCCURRED = "collision_occurred"
    
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
    ITEM_ACQUIRED = "item_acquired"
    ITEM_USED = "item_used"
    ITEM_EQUIPPED = "item_equipped"
    INVENTORY_CHANGED = "inventory_changed"
    
    # Quest events
    QUEST_STARTED = "quest_started"
    QUEST_UPDATED = "quest_updated"
    QUEST_COMPLETED = "quest_completed"
    OBJECTIVE_COMPLETED = "objective_completed"
    
    # Dialogue events
    DIALOGUE_STARTED = "dialogue_started"
    DIALOGUE_ENDED = "dialogue_ended"
    DIALOGUE_CHOICE_MADE = "dialogue_choice_made"
    
    # UI events
    UI_ELEMENT_CLICKED = "ui_element_clicked"
    UI_ELEMENT_HOVERED = "ui_element_hovered"
    UI_SCREEN_OPENED = "ui_screen_opened"
    UI_SCREEN_CLOSED = "ui_screen_closed"
    WINDOW_RESIZED = "window_resized"
    FULLSCREEN_TOGGLED = "fullscreen_toggled"
    
    # AI events
    AI_STATE_CHANGED = "ai_state_changed"
    AI_TARGET_ACQUIRED = "ai_target_acquired"
    AI_TARGET_LOST = "ai_target_lost"
    AI_ACTION_STARTED = "ai_action_started"
    AI_ACTION_COMPLETED = "ai_action_completed"
    
    # Map events
    MAP_CREATED = "map_created"
    MAP_LOADED = "map_loaded"
    MAP_SAVED = "map_saved"
    MAP_CHANGED = "map_changed"
    TILE_CHANGED = "tile_changed"
    ENTITY_SPAWNED = "entity_spawned"
    
    # Camera events
    CAMERA_MOVED = "camera_moved"
    CAMERA_ZOOMED = "camera_zoomed"
    CAMERA_ROTATED = "camera_rotated"
    CAMERA_TARGET_CHANGED = "camera_target_changed"
    CAMERA_VIEWPORT_CHANGED = "camera_viewport_changed"