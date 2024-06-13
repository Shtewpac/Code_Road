# Block Puzzle Game with Reinforcement Learning AI Agent

This project implements the classic Block Puzzle game in Python, along with an AI agent that learns to play the game optimally using reinforcement learning. The AI agent uses the Q-learning algorithm to learn the best action to take given any board configuration and the available pieces.

## Overview

The project is organized into several key directories and files:

- `agents/`: Contains the AI agent implementation using the Q-learning algorithm.
  - `__init__.py`: Makes the directory a Python package.
  - `q_learning_agent.py`: Implementation of the Q-learning agent.
- `game/`: Contains the Block Puzzle game implementation.
  - `__init__.py`: Makes the directory a Python package.
  - `board.py`: Implementation of the game board and related functions.
  - `piece.py`: Implementation of the game pieces (blocks) and related functions.
  - `game.py`: Main game logic and game loop.
- `utils/`: Contains utility functions and helper classes.
  - `__init__.py`: Makes the directory a Python package.
  - `helpers.py`: Utility functions and helper classes used throughout the project.

Additional files:

- `main.py`: The main entry point of the program to play the game with the trained AI agent.
- `train_agent.py`: The script to train the AI agent using reinforcement learning.
- `requirements.txt`: Lists the required dependencies for the project.
- `README.md`: This documentation file containing project information.

## Features

- Implements the core mechanics of the Block Puzzle game.
- Includes various block shapes such as tetrominoes, straight blocks, square blocks, and more.
- Provides a simple drag-and-drop interface for placing blocks on the board.
- Automatically clears completed lines and keeps score.
- Trains an AI agent using reinforcement learning to play the game optimally.
- Allows the trained AI agent to play the game autonomously.
- Supports customization of game parameters and AI agent hyperparameters.

## Getting started

### Requirements

- Python 3.6 or higher
- NumPy library
- Pygame library (optional, for future GUI implementation)

### Quickstart

1. Clone the repository:

```bash
git clone https://github.com/yourusername/block-puzzle-rl.git
```

2. Navigate to the project directory:

```bash
cd block-puzzle-rl
```

3. Install the required dependencies:

```bash
pip install numpy
```

To play the Block Puzzle game with the trained AI agent:

```bash
python main.py
```

To train the AI agent:

```bash
python train_agent.py
```

This will train the AI agent for a specified number of episodes (default is 1000) using reinforcement learning. The trained agent's Q-table will be used when playing the game.

### License

The project is proprietary (not open source). Copyright (c) 2024.