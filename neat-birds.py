import pygame
from pygame.locals import *
import random
import neat
import os
import sys
import matplotlib.pyplot as plt  # For plotting fitness

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 554
screen_height = 600

# Set up the display with double buffering
screen = pygame.display.set_mode((screen_width, screen_height), pygame.DOUBLEBUF)
pygame.display.set_caption('Flappy Bird with NEAT')

# Clock and FPS
clock = pygame.time.Clock()
fps = 60

# Fonts & Colors
font = pygame.font.SysFont('Bauhaus 93', 40)
white = (255, 255, 255)
flash_color = (255, 255, 0)  # Yellow color for flashing effect

# Load images
background = pygame.image.load("background.png")
ground = pygame.image.load("ground.png")

# Game variables
ground_y = screen_height - 65
pipe_gap = 350
pipe_frequency = 1500  # milliseconds
movespeed = 4

# Fitness tracking lists
max_fitness_per_gen = []  # Track max fitness per generation
avg_fitness_per_gen = []  # Track average fitness per generation

def draw_text(text, font, text_col, x, y):
    """Draw text at a specific position."""
    img = font.render(text, True, text_col)
    screen.blit(img, (x - img.get_width(), y))  # Align text to the right

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = [pygame.image.load(f'Bird{num}.png') for num in range(1, 4)]
        self.index = 0
        self.counter = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = 0  

    def update(self):
        self.vel = min(self.vel + 0.5, 8)
        if self.rect.bottom < ground_y:
            self.rect.y += int(self.vel)
        self.counter += 1
        if self.counter > 5:
            self.counter = 0
            self.index = (self.index + 1) % len(self.images)
        self.image = pygame.transform.rotate(self.images[self.index], self.vel * -1)

    def jump(self):
        self.vel = -10

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('pipe.png')
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = (x, y - pipe_gap // 2)
        else:
            self.rect.topleft = (x, y)
        self.flash_timer = 0  # Timer for flash effect
        self.flash_duration = 10  # Duration of flash effect in frames

    def update(self):
        self.rect.x -= movespeed
        if self.rect.right < 0:
            self.kill()

        # Update flash effect
        if self.flash_timer > 0:
            self.flash_timer -= 1
            if self.flash_timer % 2 == 0:  # Alternate colors for flashing effect
                self.image.fill(flash_color, special_flags=pygame.BLEND_RGB_ADD)
            else:
                self.image = pygame.image.load('pipe.png')
                if self.rect.bottomleft[1] < screen_height // 2:  # Restore flipped state for top pipe
                    self.image = pygame.transform.flip(self.image, False, True)

    def flash(self):
        """Trigger the flash effect."""
        self.flash_timer = self.flash_duration

# NEAT Integration
def eval_genomes(genomes, config, generation):
    birds = []
    nets = []
    ge = []
    
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(50, screen_height // 2))
        genome.fitness = 0
        ge.append(genome)

    pipe_group = pygame.sprite.Group()
    last_pipe = pygame.time.get_ticks() - pipe_frequency
    groundmove = 0
    run = True
    max_frames = 10000
    frame_count = 0
    max_fitness = 0  # Track maximum fitness in the current generation
    total_fitness = 0  # For calculating average fitness
    score = 0  # Number of pipes passed
    pipe_passed = False  # Track if birds have passed a pipe

    while run and len(birds) > 0 and frame_count < max_frames:
        frame_count += 1
        clock.tick(fps)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

        screen.blit(background, (0, 0))
        
        for i, bird in enumerate(birds):
            ge[i].fitness += 0.1
            total_fitness += ge[i].fitness
            if pipe_group:
                pipe = pipe_group.sprites()[0]
                output = nets[i].activate((
                    bird.rect.y,  # Vertical position of the bird
                    abs(bird.rect.y - pipe.rect.top),  # Distance to the top of the pipe
                    abs(bird.rect.y - pipe.rect.bottom),  # Distance to the bottom of the pipe
                    bird.vel,  # Vertical velocity of the bird
                    pipe.rect.x - bird.rect.x,  # Horizontal distance to the pipe
                    movespeed,  # Speed of the pipes
                    pipe.rect.height  # Height of the pipe gap
                ))
                if output[0] > 0.5:
                    bird.jump()

            # Update max fitness
            if ge[i].fitness > max_fitness:
                max_fitness = ge[i].fitness

        bird_group = pygame.sprite.Group(*birds)
        bird_group.update()
        bird_group.draw(screen)
        pipe_group.update()
        pipe_group.draw(screen)
        
        screen.blit(ground, (groundmove, ground_y))
        screen.blit(ground, (groundmove + 554, ground_y))

        for i, bird in enumerate(birds):
            if pygame.sprite.spritecollide(bird, pipe_group, False) or bird.rect.top < 0 or bird.rect.bottom >= ground_y:
                ge[i].fitness -= 5
                birds.pop(i)
                nets.pop(i)
                ge.pop(i)

        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            pipe_group.add(Pipe(screen_width, screen_height // 2 + pipe_height, -1))
            pipe_group.add(Pipe(screen_width, screen_height // 2 + pipe_height, 1))
            last_pipe = time_now
            pipe_passed = False  # Reset flag for new pipes
        
        # Check if birds passed the first pipe in the group
        if pipe_group:
            first_pipe = pipe_group.sprites()[0]
            if first_pipe.rect.right < 50 and not pipe_passed:
                score += 1  # Increase score when the first pipe is passed
                for g in ge:
                    g.fitness += 2  # Reward for passing a pipe
                pipe_passed = True  # Prevent multiple score increments for one pipe
                # Trigger flash effect for all pipes in the group
                for pipe in pipe_group:
                    pipe.flash()

        groundmove -= movespeed
        if groundmove <= -554:
            groundmove = 0
        
        # Display all stats in the top-right corner
        text_x = screen_width - 20  # Right side padding
        text_y = 20  # Start from the top

        draw_text(f"Gen: {generation}", font, white, text_x, text_y)
        draw_text(f"Birds: {len(birds)}", font, white, text_x, text_y + 40)
        draw_text(f"Max Fit: {int(max_fitness)}", font, white, text_x, text_y + 80)
        draw_text(f"Score: {score}", font, white, text_x, text_y + 120)

        pygame.display.update()

    # Calculate average fitness for the generation
    avg_fitness = total_fitness / len(ge) if ge else 0
    max_fitness_per_gen.append(max_fitness)
    avg_fitness_per_gen.append(avg_fitness)

def plot_fitness():
    """Plot the maximum and average fitness over generations."""
    plt.plot(max_fitness_per_gen, label="Max Fitness")
    # plt.plot(avg_fitness_per_gen, label="Avg Fitness")
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.title("Fitness Over Generations")
    plt.legend()
    plt.show()

# NEAT Setup
def run_neat(config_path):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())
    
    # Run NEAT for 10 generations
    winner = population.run(lambda genomes, config: eval_genomes(genomes, config, population.generation), 30)
    print(winner)
    # Plot fitness after NEAT completes
    plot_fitness()

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    run_neat(config_path)

pygame.quit()