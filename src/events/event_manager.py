"""
Event manager for the event-driven architecture.
"""

from collections import defaultdict
import uuid

class EventManager:
    """
    Event manager that handles event subscription and emission.
    
    The EventManager is the central hub for the event-driven architecture.
    It allows systems to subscribe to events and emit events to notify
    other systems of changes.
    """
    
    def __init__(self):
        """Initialize the event manager."""
        self.subscribers = defaultdict(list)  # Event type -> List of (handler, subscriber_id)
        self.deferred_events = []  # List of (event_type, data) to process next update
        self.defer_events = False  # Whether to defer events
    
    def subscribe(self, event_type, handler):
        """
        Subscribe to an event type.
        
        Args:
            event_type: The type of event to subscribe to
            handler: The function to call when the event is emitted
            
        Returns:
            function: A function that can be called to unsubscribe
        """
        subscriber_id = str(uuid.uuid4())
        self.subscribers[event_type].append((handler, subscriber_id))
        
        # Return a function that can be called to unsubscribe
        def unsubscribe():
            self._unsubscribe(event_type, subscriber_id)
        
        return unsubscribe
    
    def _unsubscribe(self, event_type, subscriber_id):
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: The type of event to unsubscribe from
            subscriber_id: The ID of the subscriber to remove
        """
        if event_type in self.subscribers:
            self.subscribers[event_type] = [
                (handler, sid) for handler, sid in self.subscribers[event_type]
                if sid != subscriber_id
            ]
    
    def emit(self, event_type, data=None):
        """
        Emit an event.
        
        Args:
            event_type: The type of event to emit
            data: The data to pass to the event handlers
        """
        if data is None:
            data = {}
        
        # If deferring events, add to deferred list
        if self.defer_events:
            self.deferred_events.append((event_type, data))
            return
        
        # Call all subscribers for this event type
        for handler, _ in self.subscribers[event_type]:
            try:
                handler(data)
            except Exception as e:
                print(f"Error in event handler for {event_type}: {e}")
    
    def begin_defer(self):
        """Begin deferring events."""
        self.defer_events = True
    
    def end_defer(self):
        """End deferring events and process all deferred events."""
        self.defer_events = False
        
        # Process all deferred events
        deferred = self.deferred_events
        self.deferred_events = []
        
        for event_type, data in deferred:
            self.emit(event_type, data)
    
    def clear_subscribers(self, event_type=None):
        """
        Clear all subscribers for an event type, or all subscribers if no type is specified.
        
        Args:
            event_type: The type of event to clear subscribers for, or None for all
        """
        if event_type is None:
            self.subscribers.clear()
        elif event_type in self.subscribers:
            self.subscribers[event_type].clear()
    
    def has_subscribers(self, event_type):
        """
        Check if an event type has any subscribers.
        
        Args:
            event_type: The type of event to check
            
        Returns:
            bool: True if the event type has subscribers, False otherwise
        """
        return event_type in self.subscribers and len(self.subscribers[event_type]) > 0