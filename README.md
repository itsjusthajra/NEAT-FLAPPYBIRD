# NEAT-FLAPPYBIRD

## Overview
This project implements a Flappy Bird game where AI agents, powered by the NEAT (NeuroEvolution of Augmenting Topologies) algorithm, learn to navigate through pipes. The birds evolve over generations, improving their ability to avoid obstacles and maximize fitness.
Features

- **Game Mechanics**: Classic Flappy Bird gameplay with birds, pipes, and a scrolling ground.
- **NEAT Integration**: Uses the NEAT library to evolve neural networks that control bird jumps.
- **Visual Feedback**: Displays generation, number of birds, maximum fitness, and score in real-time.
- **Pipe Flash Effect**: Pipes flash yellow when birds pass them, indicating a score increase.
- **Fitness Tracking**: Records max and average fitness per generation, plotted at the end.

## Requirements

- Python 3.x
- Pygame
- NEAT-Python
Matplotlib (for fitness plotting)
**Image assets**:
- background.png (background)
- ground.png (scrolling ground)
- pipe.png (pipe sprite)
- Bird1.png, Bird2.png, Bird3.png (bird animation frames)



## Installation

**Clone this repository**:
git clone <repository-url>


**Install dependencies**:
```bash pip install pygame neat-python matplotlib```


**Ensure the following files are in the project directory**:

- neat-birds.py
- config.txt (NEAT configuration file)
- Image assets: background.png, ground.png, pipe.png, Bird1.png, Bird2.png, Bird3.png



## Usage

Place the script (neat-birds.py) and assets in the same directory.

Configure NEAT parameters in config.txt (e.g., population size, mutation rates).

**Run the scrip**t:
```bash python neat-birds.py```


- Watch the birds evolve over 30 generations, with fitness and score displayed on-screen.

- After completion, a Matplotlib plot shows maximum fitness per generation.


## How It Works

- **Bird**s: Controlled by neural networks, birds jump based on inputs like position, pipe distances, velocity, and pipe speed.
- **Fitness**: Birds gain 0.1 fitness per frame, 2 for passing pipes, and lose 5 for collisions or boundary hits.
- **Pipes**: Spawn every 1.5 seconds with a random height offset, flashing when passed.
- **Display**: Shows generation, bird count, max fitness, and score in the top-right corner.
- **Plot**: Tracks and visualizes maximum fitness across generations.

## Configuration
**Edit config.txt to tweak NEAT settings**:

- Population size
- Mutation and crossover rates
- Neural network architecture (inputs, outputs, hidden nodes)

## Game Controls

- No manual controls; the NEAT algorithm fully controls the birds.
- Close the window to exit.

## Notes

- Ensure image assets match the expected dimensions for proper rendering.
- The game runs at 60 FPS with a maximum of 10,000 frames per generation.
- Adjust pipe_gap, movespeed, and pipe_frequency in the code to change difficulty.

## Future Improvements

- Add sound effects for jumps and pipe passes.
- Save and load the best genome for continued training.
- Enhance visuals with more animations or backgrounds.
