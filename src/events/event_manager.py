"""
Event Manager for the isometric RPG.

This module defines the event system that allows for decoupled communication
between different systems in the game.
"""

from collections import defaultdict
from typing import Dict, List, Callable, Any


class EventManager:
    """
    Event manager that handles the subscription and emission of events.
    
    This class implements a simple pub-sub (publisher-subscriber) pattern
    to allow for decoupled communication between different parts of the game.
    """
    
    def __init__(self):
        """Initialize the event manager."""
        # Dictionary mapping event types to lists of subscribers
        self.subscribers = defaultdict(list)
        
        # Optional queue for deferred events
        self.event_queue = []
        self.process_queue_on_update = False
    
    def subscribe(self, event_type: str, callback: Callable):
        """
        Subscribe to an event type with a callback function.
        
        Args:
            event_type (str): The type of event to subscribe to.
            callback (Callable): The function to call when the event is emitted.
                The callback should accept a single parameter: the event data dictionary.
                
        Returns:
            bool: True if the subscription was successful, False otherwise.
        """
        if not callable(callback):
            return False
            
        # Add the callback to the subscribers list for this event type
        if callback not in self.subscribers[event_type]:
            self.subscribers[event_type].append(callback)
        return True
    
    def unsubscribe(self, event_type: str, callback: Callable) -> bool:
        """
        Unsubscribe from an event type.
        
        Args:
            event_type (str): The type of event to unsubscribe from.
            callback (Callable): The callback function to remove.
            
        Returns:
            bool: True if the unsubscription was successful, False otherwise.
        """
        # Remove the callback from the subscribers list
        if event_type in self.subscribers and callback in self.subscribers[event_type]:
            self.subscribers[event_type].remove(callback)
            return True
        return False
    
    def emit(self, event_type: str, event_data: Dict[str, Any] = None):
        """
        Emit an event to all subscribers immediately.
        
        Args:
            event_type (str): The type of event to emit.
            event_data (Dict[str, Any], optional): Additional data to pass to subscribers.
        """
        if event_data is None:
            event_data = {}
            
        # Add the event type to the data for reference
        event_data['event_type'] = event_type
        
        # If queue processing is enabled, add the event to the queue
        if self.process_queue_on_update:
            self.event_queue.append((event_type, event_data))
            return
            
        # Otherwise, dispatch the event immediately
        self._dispatch_event(event_type, event_data)
    
    def emit_deferred(self, event_type: str, event_data: Dict[str, Any] = None):
        """
        Add an event to the queue for later processing.
        
        Args:
            event_type (str): The type of event to emit.
            event_data (Dict[str, Any], optional): Additional data to pass to subscribers.
        """
        if event_data is None:
            event_data = {}
            
        # Add the event type to the data for reference
        event_data['event_type'] = event_type
        
        # Add the event to the queue
        self.event_queue.append((event_type, event_data))
    
    def _dispatch_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        Dispatch an event to all subscribers.
        
        Args:
            event_type (str): The type of event to dispatch.
            event_data (Dict[str, Any]): Additional data to pass to subscribers.
        """
        # Call each subscriber callback with the event data
        for callback in self.subscribers.get(event_type, []):
            try:
                callback(event_data)
            except Exception as e:
                print(f"Error in event handler for {event_type}: {e}")
    
    def update(self):
        """
        Process all queued events.
        
        This should be called once per game update/frame to process
        deferred events.
        """
        # Process all events in the queue
        while self.event_queue:
            event_type, event_data = self.event_queue.pop(0)
            self._dispatch_event(event_type, event_data)
    
    def enable_queue_processing(self):
        """Enable queue processing for events."""
        self.process_queue_on_update = True
    
    def disable_queue_processing(self):
        """Disable queue processing for events (emit immediately)."""
        self.process_queue_on_update = False
        
    def clear_queue(self):
        """Clear all queued events without processing them."""
        self.event_queue.clear()
        
    def get_subscriber_count(self, event_type: str) -> int:
        """
        Get the number of subscribers for an event type.
        
        Args:
            event_type (str): The event type to check.
            
        Returns:
            int: The number of subscribers.
        """
        return len(self.subscribers.get(event_type, []))