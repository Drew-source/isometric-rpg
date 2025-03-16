"""
Transform Component for the isometric RPG.

This component represents the spatial position and orientation of entities.
"""

import math
import json
from copy import deepcopy

from ..ecs.component import Component


class Vector3:
    """
    A 3D vector class for position, scale, and direction.
    """
    
    def __init__(self, x=0.0, y=0.0, z=0.0):
        """
        Initialize the Vector3 with x, y, z coordinates.
        
        Args:
            x (float): X coordinate
            y (float): Y coordinate
            z (float): Z coordinate
        """
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    
    def __str__(self):
        """Return string representation of the vector."""
        return f"Vector3({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"
    
    def __eq__(self, other):
        """Check if two vectors are equal."""
        if isinstance(other, Vector3):
            return (
                math.isclose(self.x, other.x) and
                math.isclose(self.y, other.y) and
                math.isclose(self.z, other.z)
            )
        return False
    
    def distance_to(self, other):
        """Calculate the distance to another vector."""
        return math.sqrt(
            (self.x - other.x) ** 2 +
            (self.y - other.y) ** 2 +
            (self.z - other.z) ** 2
        )
    
    def distance_to_xz(self, other):
        """Calculate the distance to another vector on the X-Z plane."""
        return math.sqrt(
            (self.x - other.x) ** 2 +
            (self.z - other.z) ** 2
        )
    
    def distance_to_xy(self, other):
        """Calculate the distance to another vector on the X-Y plane."""
        return math.sqrt(
            (self.x - other.x) ** 2 +
            (self.y - other.y) ** 2
        )
    
    def normalize(self):
        """Normalize the vector to a unit vector."""
        magnitude = math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
        if magnitude > 0:
            self.x /= magnitude
            self.y /= magnitude
            self.z /= magnitude
        return self
    
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a Vector3 from dictionary data."""
        return cls(
            x=data.get("x", 0.0),
            y=data.get("y", 0.0),
            z=data.get("z", 0.0)
        )


class TransformComponent(Component):
    """
    Component representing position and orientation of an entity.
    """
    
    def __init__(self, position=None, rotation=None, scale=None):
        """
        Initialize the transform component.
        
        Args:
            position (Vector3): Position in 3D space
            rotation (Vector3): Rotation in degrees around each axis
            scale (Vector3): Scale in each dimension
        """
        super().__init__()
        self.position = position if position is not None else Vector3(0, 0, 0)
        self.rotation = rotation if rotation is not None else Vector3(0, 0, 0)
        self.scale = scale if scale is not None else Vector3(1, 1, 1)
    
    def serialize(self):
        """Serialize the component to a dictionary."""
        return {
            "position": self.position.to_dict(),
            "rotation": self.rotation.to_dict(),
            "scale": self.scale.to_dict()
        }
    
    @classmethod
    def deserialize(cls, data):
        """Deserialize from a dictionary to create a component."""
        return cls(
            position=Vector3.from_dict(data.get("position", {})),
            rotation=Vector3.from_dict(data.get("rotation", {})),
            scale=Vector3.from_dict(data.get("scale", {}))
        )
    
    def copy(self):
        """Create a deep copy of this component."""
        return TransformComponent(
            position=deepcopy(self.position),
            rotation=deepcopy(self.rotation),
            scale=deepcopy(self.scale)
        )