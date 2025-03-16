"""
Entity class for the Entity Component System.
"""

import uuid

class Entity:
    """
    Entity class that serves as a container for components.
<<<<<<< HEAD

    Entities are essentially just IDs with a collection of components
    that define their behavior and data.
    """

    def __init__(self, world=None, entity_id=None):
        """
        Initialize a new entity.

=======
    
    Entities are essentially just IDs with a collection of components
    that define their behavior and data.
    """
    
    def __init__(self, world=None, entity_id=None):
        """
        Initialize a new entity.
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Args:
            world: The world this entity belongs to
            entity_id: Optional ID for the entity (generated if None)
        """
        self.id = entity_id if entity_id is not None else str(uuid.uuid4())
        self.world = world
        self.components = {}  # Component type -> Component instance
        self.tags = set()  # Set of string tags for quick filtering
<<<<<<< HEAD

    def add_component(self, component):
        """
        Add a component to this entity.

        Args:
            component: The component to add

=======
    
    def add_component(self, component):
        """
        Add a component to this entity.
        
        Args:
            component: The component to add
            
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Returns:
            Entity: Self for method chaining
        """
        component_type = component.__class__
        self.components[component_type] = component
        component.on_attach(self)
<<<<<<< HEAD

        # Notify world of component addition
        if self.world:
            self.world.on_component_added(self, component)

        return self

    def remove_component(self, component_type):
        """
        Remove a component from this entity.

        Args:
            component_type: The type of component to remove

=======
        
        # Notify world of component addition
        if self.world:
            self.world.on_component_added(self, component)
        
        return self
    
    def remove_component(self, component_type):
        """
        Remove a component from this entity.
        
        Args:
            component_type: The type of component to remove
            
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Returns:
            Component: The removed component, or None if not found
        """
        if component_type in self.components:
            component = self.components[component_type]
            component.on_detach()
            del self.components[component_type]
<<<<<<< HEAD

            # Notify world of component removal
            if self.world:
                self.world.on_component_removed(self, component)

            return component

        return None

    def get_component(self, component_type):
        """
        Get a component of the specified type.

        Args:
            component_type: The type of component to get

=======
            
            # Notify world of component removal
            if self.world:
                self.world.on_component_removed(self, component)
            
            return component
        
        return None
    
    def get_component(self, component_type):
        """
        Get a component of the specified type.
        
        Args:
            component_type: The type of component to get
            
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Returns:
            Component: The component, or None if not found
        """
        return self.components.get(component_type)
<<<<<<< HEAD

    def has_component(self, component_type):
        """
        Check if the entity has a component of the specified type.

        Args:
            component_type: The type of component to check for

=======
    
    def has_component(self, component_type):
        """
        Check if the entity has a component of the specified type.
        
        Args:
            component_type: The type of component to check for
            
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Returns:
            bool: True if the entity has the component, False otherwise
        """
        return component_type in self.components
<<<<<<< HEAD

    def has_components(self, component_types):
        """
        Check if the entity has all of the specified component types.

        Args:
            component_types: Collection of component types to check for

        Returns:
            bool: True if the entity has all components, False otherwise
        """
        return all(component_type in self.components for component_type in component_types)        

    def add_tag(self, tag):
        """
        Add a tag to this entity.

        Args:
            tag: The tag to add

=======
    
    def has_components(self, component_types):
        """
        Check if the entity has all of the specified component types.
        
        Args:
            component_types: Collection of component types to check for
            
        Returns:
            bool: True if the entity has all components, False otherwise
        """
        return all(component_type in self.components for component_type in component_types)
    
    def add_tag(self, tag):
        """
        Add a tag to this entity.
        
        Args:
            tag: The tag to add
            
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Returns:
            Entity: Self for method chaining
        """
        self.tags.add(tag)
        return self
<<<<<<< HEAD

    def remove_tag(self, tag):
        """
        Remove a tag from this entity.

        Args:
            tag: The tag to remove

=======
    
    def remove_tag(self, tag):
        """
        Remove a tag from this entity.
        
        Args:
            tag: The tag to remove
            
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Returns:
            Entity: Self for method chaining
        """
        if tag in self.tags:
            self.tags.remove(tag)
        return self
<<<<<<< HEAD

    def has_tag(self, tag):
        """
        Check if the entity has the specified tag.

        Args:
            tag: The tag to check for

=======
    
    def has_tag(self, tag):
        """
        Check if the entity has the specified tag.
        
        Args:
            tag: The tag to check for
            
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Returns:
            bool: True if the entity has the tag, False otherwise
        """
        return tag in self.tags
<<<<<<< HEAD

=======
    
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
    def destroy(self):
        """
        Destroy this entity, removing it from the world.
        """
        if self.world:
            self.world.destroy_entity(self)
<<<<<<< HEAD

    def serialize(self):
        """
        Convert entity to a serializable format.

=======
    
    def serialize(self):
        """
        Convert entity to a serializable format.
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Returns:
            dict: Serialized entity data
        """
        serialized = {
            "id": self.id,
            "tags": list(self.tags),
            "components": {}
        }
<<<<<<< HEAD

=======
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        # Serialize each component
        for component_type, component in self.components.items():
            component_name = component_type.__name__
            serialized["components"][component_name] = component.serialize()
<<<<<<< HEAD

        return serialized

=======
        
        return serialized
    
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
    @classmethod
    def deserialize(cls, world, data, component_registry):
        """
        Create an entity from serialized data.
<<<<<<< HEAD

=======
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Args:
            world: The world this entity belongs to
            data: Serialized entity data
            component_registry: Registry of component types by name
<<<<<<< HEAD

=======
            
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        Returns:
            Entity: New entity instance
        """
        entity = cls(world, data.get("id"))
<<<<<<< HEAD

        # Add tags
        for tag in data.get("tags", []):
            entity.add_tag(tag)

=======
        
        # Add tags
        for tag in data.get("tags", []):
            entity.add_tag(tag)
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        # Add components
        for component_name, component_data in data.get("components", {}).items():
            if component_name in component_registry:
                component_type = component_registry[component_name]
                component = component_type.deserialize(component_data)
                entity.add_component(component)
<<<<<<< HEAD

        return entity
=======
        
        return entity 
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
