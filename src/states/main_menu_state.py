"""
Main menu state for the game.
"""

import pygame
from .state import State
from ..core.constants import UI_BACKGROUND_COLOR, UI_TEXT_COLOR, UI_HIGHLIGHT_COLOR

class MainMenuState(State):
    """
    Main menu state that displays the game's main menu.
    
    This state is the first one shown when the game starts and provides
    options to start a new game, load a saved game, adjust settings, or quit.
    """
    
    def __init__(self, state_manager, game):
        """
        Initialize the main menu state.
        
        Args:
            state_manager: The state manager this state belongs to
            game: The game instance
        """
        super().__init__(state_manager)
        self.game = game
        
        # Menu options
        self.options = [
            "New Game",
            "Load Game",
            "Settings",
            "Quit"
        ]
        
        self.selected_option = 0
        
        # UI elements
        self.title_font = None
        self.option_font = None
        self.title_text = None
        self.option_texts = []
        self.background = None
    
    def enter(self):
        """Set up the main menu when entering the state."""
        super().enter()
        
        # Load fonts
        self.title_font = pygame.font.SysFont("arial", 64, bold=True)
        self.option_font = pygame.font.SysFont("arial", 32)
        
        # Render title
        self.title_text = self.title_font.render("Baldur's Gate-Style RPG", True, UI_TEXT_COLOR)
        
        # Render options
        self._update_option_texts()
        
        # Create background
        self.background = pygame.Surface(self.game.resolution)
        self.background.fill(UI_BACKGROUND_COLOR)
        
        # TODO: Load and display a background image
    
    def exit(self):
        """Clean up when exiting the state."""
        super().exit()
        
        # Clear references to resources
        self.title_font = None
        self.option_font = None
        self.title_text = None
        self.option_texts = []
        self.background = None
    
    def update(self, dt):
        """
        Update the main menu.
        
        Args:
            dt: Delta time in seconds
        """
        pass  # No updates needed for a static menu
    
    def render(self, surface):
        """
        Render the main menu.
        
        Args:
            surface: The surface to render to
        """
        # Draw background
        surface.blit(self.background, (0, 0))
        
        # Draw title
        title_x = (surface.get_width() - self.title_text.get_width()) // 2
        title_y = surface.get_height() // 4
        surface.blit(self.title_text, (title_x, title_y))
        
        # Draw options
        option_y = title_y + self.title_text.get_height() + 50
        option_spacing = 50
        
        for i, option_text in enumerate(self.option_texts):
            option_x = (surface.get_width() - option_text.get_width()) // 2
            surface.blit(option_text, (option_x, option_y + i * option_spacing))
    
    def handle_event(self, event):
        """
        Handle events for the main menu.
        
        Args:
            event: The event to handle
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self._select_previous_option()
            elif event.key == pygame.K_DOWN:
                self._select_next_option()
            elif event.key == pygame.K_RETURN:
                self._activate_selected_option()
    
    def _select_next_option(self):
        """Select the next menu option."""
        self.selected_option = (self.selected_option + 1) % len(self.options)
        self._update_option_texts()
    
    def _select_previous_option(self):
        """Select the previous menu option."""
        self.selected_option = (self.selected_option - 1) % len(self.options)
        self._update_option_texts()
    
    def _update_option_texts(self):
        """Update the rendered option texts based on the selected option."""
        self.option_texts = []
        
        for i, option in enumerate(self.options):
            color = UI_HIGHLIGHT_COLOR if i == self.selected_option else UI_TEXT_COLOR
            text = self.option_font.render(option, True, color)
            self.option_texts.append(text)
    
    def _activate_selected_option(self):
        """Activate the currently selected menu option."""
        if self.selected_option == 0:  # New Game
            # TODO: Start a new game
            print("New Game selected")
        elif self.selected_option == 1:  # Load Game
            # TODO: Show load game screen
            print("Load Game selected")
        elif self.selected_option == 2:  # Settings
            # TODO: Show settings screen
            print("Settings selected")
        elif self.selected_option == 3:  # Quit
            self.game.quit() 