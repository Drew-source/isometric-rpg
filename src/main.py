"""
Main entry point for the game.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.game import Game
from core.utils import debug_print

def main():
    """Main function that initializes and runs the game."""
    debug_print("Starting game", "MAIN")
    
    # Create and run the game
    game = Game()
    game.run()
    
    debug_print("Game ended", "MAIN")

if __name__ == "__main__":
    main()