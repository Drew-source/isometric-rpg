"""
State manager for game states.
"""

class StateManager:
    """
    Manages a stack of game states.
    
    The StateManager maintains a stack of game states, where only the top
    state is active at any given time. This allows for nested states like
    menus, dialogues, etc.
    """
    
    def __init__(self):
        """Initialize the state manager."""
        self.states = []  # Stack of states
        self.current_state = None  # Reference to the current active state
    
    def push_state(self, state):
        """
        Add a state to the top of the stack and initialize it.
        
        Args:
            state: The state to push
        """
        # Pause the current state if there is one
        if self.current_state:
            self.current_state.pause()
        
        # Add the new state to the stack
        self.states.append(state)
        self.current_state = state
        
        # Enter the new state
        state.enter()
    
    def pop_state(self):
        """
        Remove the top state from the stack.
        
        Returns:
            The popped state, or None if the stack is empty
        """
        if not self.states:
            return None
        
        # Exit the current state
        state = self.states.pop()
        state.exit()
        
        # Update the current state reference
        self.current_state = self.states[-1] if self.states else None
        
        # Resume the new current state if there is one
        if self.current_state:
            self.current_state.resume()
        
        return state
    
    def switch_state(self, state):
        """
        Replace the top state with a new state.
        
        Args:
            state: The state to switch to
        """
        # Pop the current state if there is one
        if self.states:
            self.pop_state()
        
        # Push the new state
        self.push_state(state)
    
    def clear_states(self):
        """Clear all states from the stack."""
        while self.states:
            self.pop_state()
    
    def get_state_count(self):
        """
        Get the number of states in the stack.
        
        Returns:
            int: The number of states
        """
        return len(self.states) 