"""
Transform component for the Entity Component System.
"""

from ..ecs.component import Component
from ..core.utils import Vector2

class TransformComponent(Component):
    """
    Component that stores position, rotation, and scale.
    
    This is a fundamental component that most entities will have.
    It defines where an entity is located in the game world.
    """
    
    def __init__(self, x=0, y=0, z=0, rotation=0, scale=1):
        """
        Initialize the transform component.
        
        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate (height)
            rotation: Rotation in degrees
            scale: Scale factor
        """
        super().__init__()
        self.position = Vector2(x, y)
        self.z = z
        self.rotation = rotation
        self.scale = scale
        self.previous_position = Vector2(x, y)
        self.previous_z = z
    
    def serialize(self):
        """
        Convert component data to a serializable format.
        
        Returns:
            dict: Serialized component data
        """
        return {
            "position": {
                "x": self.position.x,
                "y": self.position.y
            },
            "z": self.z,
            "rotation": self.rotation,
            "scale": self.scale
        }
    
    @classmethod
    def deserialize(cls, data):
        """
        Create a component from serialized data.
        
        Args:
            data: Serialized component data
            
        Returns:
            TransformComponent: New component instance
        """
        position = data.get("position", {})
        x = position.get("x", 0)
        y = position.get("y", 0)
        z = data.get("z", 0)
        rotation = data.get("rotation", 0)
        scale = data.get("scale", 1)
        
        return cls(x, y, z, rotation, scale)
    
    def set_position(self, x, y, z=None):
        """
        Set the position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate (optional)
            
        Returns:
            TransformComponent: Self for method chaining
        """
        self.previous_position.x = self.position.x
        self.previous_position.y = self.position.y
        
        self.position.x = x
        self.position.y = y
        
        if z is not None:
            self.previous_z = self.z
            self.z = z
        
        return self
    
    def set_rotation(self, rotation):
        """
        Set the rotation.
        
        Args:
            rotation: Rotation in degrees
            
        Returns:
            TransformComponent: Self for method chaining
        """
        self.rotation = rotation
        return self
    
    def set_scale(self, scale):
        """
        Set the scale.
        
        Args:
            scale: Scale factor
            
        Returns:
            TransformComponent: Self for method chaining
        """
        self.scale = scale
        return self
    
    def move(self, dx, dy, dz=0):
        """
        Move by a relative amount.
        
        Args:
            dx: Change in X
            dy: Change in Y
            dz: Change in Z (optional)
            
        Returns:
            TransformComponent: Self for method chaining
        """
        self.previous_position.x = self.position.x
        self.previous_position.y = self.position.y
        
        self.position.x += dx
        self.position.y += dy
        
        if dz != 0:
            self.previous_z = self.z
            self.z += dz
        
        return self
    
    def rotate(self, drotation):
        """
        Rotate by a relative amount.
        
        Args:
            drotation: Change in rotation (degrees)
            
        Returns:
            TransformComponent: Self for method chaining
        """
        self.rotation += drotation
        return self
    
    def scale_by(self, factor):
        """
        Scale by a factor.
        
        Args:
            factor: Scale factor
            
        Returns:
            TransformComponent: Self for method chaining
        """
        self.scale *= factor
        return self
    
    def has_moved(self):
        """
        Check if the transform has moved since the last update.
        
        Returns:
            bool: True if moved, False otherwise
        """
        return (self.position.x != self.previous_position.x or
                self.position.y != self.previous_position.y or
                self.z != self.previous_z)
    
    def update_previous_position(self):
        """
        Update the previous position to match the current position.
        
        Returns:
            TransformComponent: Self for method chaining
        """
        self.previous_position.x = self.position.x
        self.previous_position.y = self.position.y
        self.previous_z = self.z
<<<<<<< HEAD
        return self
=======
        return self 
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
