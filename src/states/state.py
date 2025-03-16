"""
Base state class for game states.
"""

class State:
    """
    Base class for all game states.
    
    Game states represent different modes of the game, such as the main menu,
    gameplay, dialogue, inventory, etc. Only one state is active at a time.
    """
    
    def __init__(self, state_manager):
        """
        Initialize the state.
        
        Args:
            state_manager: The state manager this state belongs to
        """
        self.state_manager = state_manager
        self.is_active = False
        self.is_paused = False
    
    def enter(self):
        """
        Called when the state becomes active.
        
        Override this method to initialize the state.
        """
        self.is_active = True
        self.is_paused = False
    
    def exit(self):
        """
        Called when the state is removed from the stack.
        
        Override this method to clean up the state.
        """
        self.is_active = False
        self.is_paused = False
    
    def pause(self):
        """
        Called when the state is paused (another state is pushed on top).
        
        Override this method to pause the state.
        """
        self.is_paused = True
    
    def resume(self):
        """
        Called when the state is resumed (the state above is popped).
        
        Override this method to resume the state.
        """
        self.is_paused = False
    
    def update(self, dt):
        """
        Update the state.
        
        Args:
            dt: Delta time in seconds
        """
        pass
    
    def render(self, surface):
        """
        Render the state.
        
        Args:
            surface: The surface to render to
        """
        pass
    
    def handle_event(self, event):
        """
        Handle an event.
        
        Args:
            event: The event to handle
        """
        pass
    
    def handle_escape(self):
        """
        Handle the escape key.
        
        By default, pops the state if it's not the only state.
        Override this method to change the behavior.
        """
        if self.state_manager.get_state_count() > 1:
            self.state_manager.pop_state()