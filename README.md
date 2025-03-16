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