<<<<<<< HEAD
# Baldur's Gate-Style Isometric RPG

A Python-based isometric RPG game inspired by Baldur's Gate 2, featuring:
- Real-time with pause combat system (RTwP)
- D&D-inspired character mechanics
- Isometric world exploration with pathfinding
- Branching dialogue and quest system
- Party management with up to 6 characters

## Setup and Installation

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run the game:
   ```
   python src/main.py
   ```

## Project Structure

- `assets/` - Game assets (images, data, audio, fonts)
- `src/` - Source code
  - `core/` - Core game architecture
  - `ecs/` - Entity Component System
  - `events/` - Event-driven architecture
  - `components/` - ECS components
  - `systems/` - ECS systems
  - `engine/` - Rendering and physics
  - `ui/` - User interface
  - `world/` - World representation
  - `states/` - Game states
  - `data/` - Data management

## Development

This project follows the Entity Component System (ECS) architecture pattern combined with an Event-Driven design for flexibility and maintainability.

### Implementation Order

1. Core Architecture Foundation
2. World Representation
3. Movement and Pathfinding
4. Character Systems
5. User Interface Framework
6. Game Logic Systems
7. Data Management and Persistence
=======
# Isometric RPG Engine

An isometric role-playing game engine built with Python. This project implements a comprehensive Entity Component System (ECS) architecture that provides a solid foundation for building isometric RPGs with rich gameplay mechanics.

## Features

### Core Systems
- **Entity Component System (ECS)**: Flexible architecture for game entities and systems
- **Event System**: Comprehensive event handling for game state changes
- **Spatial Grid**: Efficient spatial partitioning for entity queries and collision detection
- **Map System**: Powerful map creation, serialization, and loading capabilities

### Character Systems
- **Transform Component**: Handles entity positioning, rotation, and scale
- **Character Stats Component**: Manages character attributes, health, mana, and status effects
- **AI Component**: Controls NPC behavior with personality-driven decision making
- **Combat Component**: Manages combat states, stances, targeting, and combat statistics

### World Representation
- **Tile-based Maps**: Create and manipulate game maps with different tile types
- **Collision Detection**: Handle collisions between entities and the environment
- **Pathfinding**: A* algorithm for finding paths through the game world
- **Line of Sight**: Raytracing for visibility checks

## Getting Started

### Prerequisites
- Python 3.6 or higher

### Installation
1. Clone this repository
2. Navigate to the project directory
3. Run the example scripts in the `examples/` directory

```bash
python examples/spatial_example.py
python examples/map_example.py
python examples/ai_example.py
python examples/combat_example.py
```

## Project Structure

- `src/`: Source code for the engine
  - `ecs/`: Entity Component System core
  - `events/`: Event management system
  - `components/`: Game components (Transform, AI, Combat, etc.)
  - `systems/`: Game systems that process components
  - `spatial/`: Spatial partitioning and queries
  - `map/`: Map representation and management
- `examples/`: Example scripts demonstrating different features

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by classic isometric RPGs like Baldur's Gate, Fallout 1-2, and Diablo 
>>>>>>> 48f82ac (Initial commit with isometric RPG engine)
