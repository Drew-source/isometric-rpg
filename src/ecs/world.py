"""
World class for the Entity Component System.
"""

from collections import defaultdict
from .entity import Entity
from ..events.event_types import EventType

class World:
    """
    World class that manages entities and systems.
<<<<<<< HEAD

    The World is the main container for the ECS. It keeps track of all
    entities and systems, and handles their creation, destruction, and updates.
    """

    def __init__(self, event_manager):
        """
        Initialize the world.

=======
    
    The World is the main container for the ECS. It keeps track of all
    entities and systems, and handles their creation, destruction, and updates.
    """
    
    def __init__(self, event_manager):
        """
        Initialize the world.
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Args:
            event_manager: Event manager for emitting events
        """
        self.entities = {}  # Entity ID -> Entity
        self.systems = []  # List of systems
        self.component_entities = defaultdict(set)  # Component type -> Set of entity IDs
        self.tag_entities = defaultdict(set)  # Tag -> Set of entity IDs
        self.event_manager = event_manager
        self.component_registry = {}  # Component name -> Component class
        self.pending_entities = []  # Entities to be added next update
        self.pending_removals = []  # Entities to be removed next update
        self.current_map_id = None  # Current map ID
        self.game_time = 0.0  # Game time in seconds
        self.flags = {}  # Global game flags
<<<<<<< HEAD

    def register_component(self, component_class):
        """
        Register a component class with the world.

=======
    
    def register_component(self, component_class):
        """
        Register a component class with the world.
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Args:
            component_class: The component class to register
        """
        self.component_registry[component_class.__name__] = component_class
<<<<<<< HEAD

    def create_entity(self):
        """
        Create a new entity.

=======
    
    def create_entity(self):
        """
        Create a new entity.
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Returns:
            Entity: The created entity
        """
        entity = Entity(self)
        self.pending_entities.append(entity)
        return entity
<<<<<<< HEAD

    def destroy_entity(self, entity):
        """
        Destroy an entity.

=======
    
    def destroy_entity(self, entity):
        """
        Destroy an entity.
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Args:
            entity: The entity to destroy
        """
        if entity.id in self.entities:
            self.pending_removals.append(entity)
<<<<<<< HEAD

    def add_system(self, system):
        """
        Add a system to the world.

        Args:
            system: The system to add

=======
    
    def add_system(self, system):
        """
        Add a system to the world.
        
        Args:
            system: The system to add
            
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Returns:
            System: The added system
        """
        self.systems.append(system)
        self.sort_systems()
        system.initialize()
        return system
<<<<<<< HEAD

    def remove_system(self, system):
        """
        Remove a system from the world.

        Args:
            system: The system to remove

=======
    
    def remove_system(self, system):
        """
        Remove a system from the world.
        
        Args:
            system: The system to remove
            
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Returns:
            System: The removed system, or None if not found
        """
        if system in self.systems:
            system.shutdown()
            self.systems.remove(system)
            return system
        return None
<<<<<<< HEAD

    def sort_systems(self):
        """Sort systems by priority."""
        self.systems.sort(key=lambda s: s.priority, reverse=True)

    def update(self, dt):
        """
        Update the world.

=======
    
    def sort_systems(self):
        """Sort systems by priority."""
        self.systems.sort(key=lambda s: s.priority, reverse=True)
    
    def update(self, dt):
        """
        Update the world.
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Args:
            dt: Delta time in seconds
        """
        # Update game time
        self.game_time += dt
<<<<<<< HEAD

=======
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        # Process pending entity additions
        for entity in self.pending_entities:
            self._add_entity(entity)
        self.pending_entities.clear()
<<<<<<< HEAD

=======
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        # Process pending entity removals
        for entity in self.pending_removals:
            self._remove_entity(entity)
        self.pending_removals.clear()
<<<<<<< HEAD

        # Update all systems
        for system in self.systems:
            system.update(dt)

    def _add_entity(self, entity):
        """
        Add an entity to the world.

=======
        
        # Update all systems
        for system in self.systems:
            system.update(dt)
    
    def _add_entity(self, entity):
        """
        Add an entity to the world.
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Args:
            entity: The entity to add
        """
        self.entities[entity.id] = entity
<<<<<<< HEAD

        # Add to component indices
        for component_type, component in entity.components.items():
            self.component_entities[component_type].add(entity.id)

        # Add to tag indices
        for tag in entity.tags:
            self.tag_entities[tag].add(entity.id)

        # Emit entity created event
        self.event_manager.emit(EventType.ENTITY_CREATED, {"entity": entity})

    def _remove_entity(self, entity):
        """
        Remove an entity from the world.

=======
        
        # Add to component indices
        for component_type, component in entity.components.items():
            self.component_entities[component_type].add(entity.id)
        
        # Add to tag indices
        for tag in entity.tags:
            self.tag_entities[tag].add(entity.id)
        
        # Emit entity created event
        self.event_manager.emit(EventType.ENTITY_CREATED, {"entity": entity})
    
    def _remove_entity(self, entity):
        """
        Remove an entity from the world.
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Args:
            entity: The entity to remove
        """
        # Emit entity destroyed event
        self.event_manager.emit(EventType.ENTITY_DESTROYED, {"entity": entity})
<<<<<<< HEAD

=======
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        # Remove from component indices
        for component_type in entity.components:
            if entity.id in self.component_entities[component_type]:
                self.component_entities[component_type].remove(entity.id)
<<<<<<< HEAD

=======
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        # Remove from tag indices
        for tag in entity.tags:
            if entity.id in self.tag_entities[tag]:
                self.tag_entities[tag].remove(entity.id)
<<<<<<< HEAD

        # Remove from entities dict
        if entity.id in self.entities:
            del self.entities[entity.id]

    def on_component_added(self, entity, component):
        """
        Called when a component is added to an entity.

=======
        
        # Remove from entities dict
        if entity.id in self.entities:
            del self.entities[entity.id]
    
    def on_component_added(self, entity, component):
        """
        Called when a component is added to an entity.
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Args:
            entity: The entity the component was added to
            component: The component that was added
        """
        component_type = component.__class__
        self.component_entities[component_type].add(entity.id)
<<<<<<< HEAD

=======
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        # Emit component added event
        self.event_manager.emit(EventType.COMPONENT_ADDED, {
            "entity": entity,
            "component": component
        })
<<<<<<< HEAD

    def on_component_removed(self, entity, component):
        """
        Called when a component is removed from an entity.

=======
    
    def on_component_removed(self, entity, component):
        """
        Called when a component is removed from an entity.
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Args:
            entity: The entity the component was removed from
            component: The component that was removed
        """
        component_type = component.__class__
        if entity.id in self.component_entities[component_type]:
            self.component_entities[component_type].remove(entity.id)
<<<<<<< HEAD

=======
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        # Emit component removed event
        self.event_manager.emit(EventType.COMPONENT_REMOVED, {
            "entity": entity,
            "component": component
        })
<<<<<<< HEAD

    def get_entity(self, entity_id):
        """
        Get an entity by ID.

        Args:
            entity_id: The ID of the entity to get

=======
    
    def get_entity(self, entity_id):
        """
        Get an entity by ID.
        
        Args:
            entity_id: The ID of the entity to get
            
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Returns:
            Entity: The entity, or None if not found
        """
        return self.entities.get(entity_id)
<<<<<<< HEAD

    def get_entities_with_component(self, component_type):
        """
        Get all entities with a specific component type.

        Args:
            component_type: The component type to filter by

        Returns:
            list: List of matching entities
        """
        return [self.entities[entity_id] for entity_id in self.component_entities[component_type]  
                if entity_id in self.entities]

    def get_entities_with_components(self, component_types):
        """
        Get all entities with all of the specified component types.

        Args:
            component_types: Collection of component types to filter by

=======
    
    def get_entities_with_component(self, component_type):
        """
        Get all entities with a specific component type.
        
        Args:
            component_type: The component type to filter by
            
        Returns:
            list: List of matching entities
        """
        return [self.entities[entity_id] for entity_id in self.component_entities[component_type]
                if entity_id in self.entities]
    
    def get_entities_with_components(self, component_types):
        """
        Get all entities with all of the specified component types.
        
        Args:
            component_types: Collection of component types to filter by
            
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Returns:
            list: List of matching entities
        """
        if not component_types:
            return []
<<<<<<< HEAD

=======
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        # Start with entities that have the first component type
        component_types = list(component_types)
        first_type = component_types[0]
        entity_ids = set(self.component_entities[first_type])
<<<<<<< HEAD

        # Filter by remaining component types
        for component_type in component_types[1:]:
            entity_ids &= set(self.component_entities[component_type])

        return [self.entities[entity_id] for entity_id in entity_ids
                if entity_id in self.entities]

    def get_entities_with_tag(self, tag):
        """
        Get all entities with a specific tag.

        Args:
            tag: The tag to filter by

=======
        
        # Filter by remaining component types
        for component_type in component_types[1:]:
            entity_ids &= set(self.component_entities[component_type])
        
        return [self.entities[entity_id] for entity_id in entity_ids
                if entity_id in self.entities]
    
    def get_entities_with_tag(self, tag):
        """
        Get all entities with a specific tag.
        
        Args:
            tag: The tag to filter by
            
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Returns:
            list: List of matching entities
        """
        return [self.entities[entity_id] for entity_id in self.tag_entities[tag]
                if entity_id in self.entities]
<<<<<<< HEAD

    def get_entities_with_tags(self, tags):
        """
        Get all entities with all of the specified tags.

        Args:
            tags: Collection of tags to filter by

=======
    
    def get_entities_with_tags(self, tags):
        """
        Get all entities with all of the specified tags.
        
        Args:
            tags: Collection of tags to filter by
            
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Returns:
            list: List of matching entities
        """
        if not tags:
            return []
<<<<<<< HEAD

=======
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        # Start with entities that have the first tag
        tags = list(tags)
        first_tag = tags[0]
        entity_ids = set(self.tag_entities[first_tag])
<<<<<<< HEAD

        # Filter by remaining tags
        for tag in tags[1:]:
            entity_ids &= set(self.tag_entities[tag])

        return [self.entities[entity_id] for entity_id in entity_ids
                if entity_id in self.entities]

    def set_flag(self, flag_name, value):
        """
        Set a global game flag.

=======
        
        # Filter by remaining tags
        for tag in tags[1:]:
            entity_ids &= set(self.tag_entities[tag])
        
        return [self.entities[entity_id] for entity_id in entity_ids
                if entity_id in self.entities]
    
    def set_flag(self, flag_name, value):
        """
        Set a global game flag.
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Args:
            flag_name: The name of the flag
            value: The value to set
        """
        self.flags[flag_name] = value
<<<<<<< HEAD

=======
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        # Emit flag changed event
        self.event_manager.emit(EventType.FLAG_CHANGED, {
            "flag_name": flag_name,
            "value": value
        })
<<<<<<< HEAD

    def get_flag(self, flag_name, default=None):
        """
        Get a global game flag.

        Args:
            flag_name: The name of the flag
            default: Default value if flag is not set

=======
    
    def get_flag(self, flag_name, default=None):
        """
        Get a global game flag.
        
        Args:
            flag_name: The name of the flag
            default: Default value if flag is not set
            
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Returns:
            The flag value, or default if not set
        """
        return self.flags.get(flag_name, default)
<<<<<<< HEAD

=======
    
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
    def clear(self):
        """Clear all entities and reset the world state."""
        # Emit world clearing event
        self.event_manager.emit(EventType.WORLD_CLEARING, {})
<<<<<<< HEAD

=======
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        # Clear entities
        self.entities.clear()
        self.component_entities.clear()
        self.tag_entities.clear()
        self.pending_entities.clear()
        self.pending_removals.clear()
<<<<<<< HEAD

=======
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        # Reset state
        self.current_map_id = None
        self.game_time = 0.0
        self.flags.clear()
<<<<<<< HEAD

        # Emit world cleared event
        self.event_manager.emit(EventType.WORLD_CLEARED, {})
=======
        
        # Emit world cleared event
        self.event_manager.emit(EventType.WORLD_CLEARED, {}) 
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
