"""
Main game class that manages the game loop and state.
"""

import pygame
import time
import sys
<<<<<<< HEAD
from .constants import SCREEN_WIDTH, SCREEN_HEIGHT, TARGET_FPS, WINDOW_TITLE, BACKGROUND_COLOR     
=======
from .constants import SCREEN_WIDTH, SCREEN_HEIGHT, TARGET_FPS, WINDOW_TITLE, BACKGROUND_COLOR
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
from .settings import Settings
from ..ecs.world import World
from ..events.event_manager import EventManager
from ..events.event_types import EventType
from ..states.state_manager import StateManager
from ..states.main_menu_state import MainMenuState

class Game:
    """
    Main game class that initializes systems and runs the game loop.
    """
<<<<<<< HEAD

    def __init__(self):
        # Initialize pygame
        pygame.init()

        # Load settings
        self.settings = Settings()

        # Set up display
        self.resolution = self.settings.get_resolution()
        self.fullscreen = self.settings.is_fullscreen()

        flags = pygame.DOUBLEBUF
        if self.fullscreen:
            flags |= pygame.FULLSCREEN

        self.screen = pygame.display.set_mode(self.resolution, flags)
        pygame.display.set_caption(WINDOW_TITLE)

        # Set up clock
        self.clock = pygame.time.Clock()
        self.running = False

        # Create event manager
        self.event_manager = EventManager()

        # Create world
        self.world = World(self.event_manager)

        # Create state manager
        self.state_manager = StateManager()

        # Set up initial state
        self.state_manager.push_state(MainMenuState(self.state_manager, self))

        # Game time tracking
        self.game_time = 0.0  # In-game time in seconds
        self.time_scale = 1.0  # Time scale factor (1.0 = normal speed)

=======
    
    def __init__(self):
        # Initialize pygame
        pygame.init()
        
        # Load settings
        self.settings = Settings()
        
        # Set up display
        self.resolution = self.settings.get_resolution()
        self.fullscreen = self.settings.is_fullscreen()
        
        flags = pygame.DOUBLEBUF
        if self.fullscreen:
            flags |= pygame.FULLSCREEN
        
        self.screen = pygame.display.set_mode(self.resolution, flags)
        pygame.display.set_caption(WINDOW_TITLE)
        
        # Set up clock
        self.clock = pygame.time.Clock()
        self.running = False
        
        # Create event manager
        self.event_manager = EventManager()
        
        # Create world
        self.world = World(self.event_manager)
        
        # Create state manager
        self.state_manager = StateManager()
        
        # Set up initial state
        self.state_manager.push_state(MainMenuState(self.state_manager, self))
        
        # Game time tracking
        self.game_time = 0.0  # In-game time in seconds
        self.time_scale = 1.0  # Time scale factor (1.0 = normal speed)
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        # Performance tracking
        self.fps_timer = 0
        self.fps_count = 0
        self.current_fps = 0
<<<<<<< HEAD

=======
    
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
    def run(self):
        """Run the main game loop."""
        self.running = True
        last_time = time.time()
<<<<<<< HEAD

        # Emit game started event
        self.event_manager.emit(EventType.GAME_STARTED, {})

        while self.running:
            # Calculate delta time
            current_time = time.time()
            dt = min(current_time - last_time, 0.05)  # Cap at 50ms to prevent physics issues      
            last_time = current_time

            # Update game time
            self.game_time += dt * self.time_scale

            # Process input
            self._handle_events()

            # Update current game state
            if self.state_manager.current_state:
                self.state_manager.current_state.update(dt)

            # Update all active systems
            self.world.update(dt)

            # Render
            self._render()

            # Frame rate control
            self.clock.tick(TARGET_FPS)

            # Update FPS counter
            self._update_fps(dt)

=======
        
        # Emit game started event
        self.event_manager.emit(EventType.GAME_STARTED, {})
        
        while self.running:
            # Calculate delta time
            current_time = time.time()
            dt = min(current_time - last_time, 0.05)  # Cap at 50ms to prevent physics issues
            last_time = current_time
            
            # Update game time
            self.game_time += dt * self.time_scale
            
            # Process input
            self._handle_events()
            
            # Update current game state
            if self.state_manager.current_state:
                self.state_manager.current_state.update(dt)
            
            # Update all active systems
            self.world.update(dt)
            
            # Render
            self._render()
            
            # Frame rate control
            self.clock.tick(TARGET_FPS)
            
            # Update FPS counter
            self._update_fps(dt)
    
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
    def _handle_events(self):
        """Process pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Handle escape key (context-dependent)
                    if self.state_manager.current_state:
                        self.state_manager.current_state.handle_escape()
                elif event.key == pygame.K_F5:
                    # Quick save
                    self._quick_save()
                elif event.key == pygame.K_F9:
                    # Quick load
                    self._quick_load()
<<<<<<< HEAD

            # Pass event to current state
            if self.state_manager.current_state:
                self.state_manager.current_state.handle_event(event)

=======
            
            # Pass event to current state
            if self.state_manager.current_state:
                self.state_manager.current_state.handle_event(event)
    
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
    def _render(self):
        """Render the current frame."""
        # Clear screen
        self.screen.fill(BACKGROUND_COLOR)
<<<<<<< HEAD

        # Render current state
        if self.state_manager.current_state:
            self.state_manager.current_state.render(self.screen)

        # Draw FPS counter if enabled
        if self.settings.settings.get("show_fps", False):
            self._render_fps()

        # Update display
        pygame.display.flip()

=======
        
        # Render current state
        if self.state_manager.current_state:
            self.state_manager.current_state.render(self.screen)
        
        # Draw FPS counter if enabled
        if self.settings.settings.get("show_fps", False):
            self._render_fps()
        
        # Update display
        pygame.display.flip()
    
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
    def _update_fps(self, dt):
        """Update FPS counter."""
        self.fps_count += 1
        self.fps_timer += dt
<<<<<<< HEAD

=======
        
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
        if self.fps_timer >= 1.0:
            self.current_fps = self.fps_count
            self.fps_count = 0
            self.fps_timer = 0
<<<<<<< HEAD

=======
    
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
    def _render_fps(self):
        """Render FPS counter on screen."""
        font = pygame.font.SysFont("monospace", 16)
        fps_text = font.render(f"FPS: {self.current_fps}", True, (255, 255, 0))
        self.screen.blit(fps_text, (10, 10))
<<<<<<< HEAD

=======
    
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
    def _quick_save(self):
        """Perform a quick save."""
        # TODO: Implement save system integration
        print("Quick save not implemented yet")
<<<<<<< HEAD

=======
    
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
    def _quick_load(self):
        """Perform a quick load."""
        # TODO: Implement save system integration
        print("Quick load not implemented yet")
<<<<<<< HEAD

=======
    
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
    def quit(self):
        """Quit the game."""
        self.running = False
        pygame.quit()
        sys.exit()
<<<<<<< HEAD

=======
    
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        self.fullscreen = not self.fullscreen
        self.settings.set_fullscreen(self.fullscreen)
<<<<<<< HEAD

        flags = pygame.DOUBLEBUF
        if self.fullscreen:
            flags |= pygame.FULLSCREEN

        self.screen = pygame.display.set_mode(self.resolution, flags)

=======
        
        flags = pygame.DOUBLEBUF
        if self.fullscreen:
            flags |= pygame.FULLSCREEN
        
        self.screen = pygame.display.set_mode(self.resolution, flags)
    
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
    def set_resolution(self, width, height):
        """Set the game resolution."""
        self.resolution = (width, height)
        self.settings.set_resolution(width, height)
<<<<<<< HEAD

        flags = pygame.DOUBLEBUF
        if self.fullscreen:
            flags |= pygame.FULLSCREEN

        self.screen = pygame.display.set_mode(self.resolution, flags)

    def set_time_scale(self, scale):
        """Set the game time scale."""
        self.time_scale = max(0.0, min(4.0, scale))  # Clamp between 0 and 4
=======
        
        flags = pygame.DOUBLEBUF
        if self.fullscreen:
            flags |= pygame.FULLSCREEN
        
        self.screen = pygame.display.set_mode(self.resolution, flags)
    
    def set_time_scale(self, scale):
        """Set the game time scale."""
        self.time_scale = max(0.0, min(4.0, scale))  # Clamp between 0 and 4 
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
