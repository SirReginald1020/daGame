# genetic_algorithm.py

import random
import pygame
import json


class Agent(pygame.sprite.Sprite):
    def __init__(self, chromosome, start_x=100, start_y=300):
        super().__init__()
        self.chromosome = chromosome
        self.current_action_index = 0
        self.rect = pygame.Rect(start_x, start_y, 34, 57)  # Starting position and size
        self.vel_y = 0
        self.speed = 4.5
        self.jumping = False

    def perform_action(self, action):
        if action == 'move_left':
            self.rect.x -= self.speed  # Adjust movement speed as necessary
        elif action == 'move_right':
            self.rect.x += self.speed
        elif action == 'jump':
            self.rect.y -= 11  # Example jump; implement gravity as needed
            self.jumping = True
        elif action == 'idle':
            pass  # No movement for idle

    def apply_gravity(self):
        self.vel_y += 0.35  # Gravity
        self.rect.y += self.vel_y

    def update(self, platforms):
        # Perform action and apply gravity
        self.perform_action()
        self.apply_gravity()

        # Handle collisions
        self.horizontal_collisions(platforms)
        self.vertical_collisions(platforms)

    def horizontal_collisions(self, platforms):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        for hit in hits:
            if self.rect.right > hit.rect.left > self.rect.left:  # Moving right
                self.rect.right = hit.rect.left
            elif self.rect.left < hit.rect.right < self.rect.right:  # Moving left
                self.rect.left = hit.rect.right

    def vertical_collisions(self, platforms):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits:
            if self.vel_y > 0:  # Falling down
                self.rect.bottom = hits[0].rect.top
                self.vel_y = 0
                self.jumping = False
            elif self.vel_y < 0:  # Jumping up
                self.rect.top = hits[0].rect.bottom
                self.vel_y = 0

    def draw(self, screen, camera):
        # Draw in relation to the camera
        offset_position = camera.apply(self)
        pygame.draw.rect(screen, (255, 0, 0), offset_position)  # Draw agent as a red rectangle


class GABrain:
    def __init__(self, population_size, mutation_rate, crossover_rate, sequence_length, goal_x):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.sequence_length = sequence_length
        self.goal_x = goal_x  # X-coordinate of the level goal
        self.population = self.initialize_population()
        
    def initialize_population(self):
        # Generate a population of agents with random chromosomes (action sequences)
        population = []
        for _ in range(self.population_size):
            chromosome = [random.choice(['jump', 'move_left', 'move_right', 'idle']) for _ in range(self.sequence_length)]
            agent = Agent(chromosome)
            population.append(agent)
        return population

    def calculate_fitness(self, agent):
        # Fitness is based on distance traveled towards the goal
        distance_traveled = agent.rect.x
        fitness = distance_traveled / self.goal_x  # Normalize by the goal position
        return fitness

    def selection(self):
        # Calculate fitness for all agents and sort by fitness
        sorted_population = sorted(self.population, key=lambda agent: self.calculate_fitness(agent), reverse=True)
        
        # Select from the top half of the population for higher fitness
        top_half = sorted_population[:len(sorted_population) // 2]
        
        # Randomly pick two parents from the top half
        parent1 = random.choice(top_half)
        parent2 = random.choice(top_half)
        return parent1, parent2

    def crossover(self, parent1, parent2):
        # Single-point crossover on chromosomes
        if random.random() < self.crossover_rate:
            crossover_point = random.randint(0, self.sequence_length - 1)
            child1_chromosome = parent1.chromosome[:crossover_point] + parent2.chromosome[crossover_point:]
            child2_chromosome = parent2.chromosome[:crossover_point] + parent1.chromosome[crossover_point:]
        else:
            child1_chromosome, child2_chromosome = parent1.chromosome[:], parent2.chromosome[:]
        
        # Create new Agent objects for children
        child1 = Agent(child1_chromosome)
        child2 = Agent(child2_chromosome)
        return child1, child2

    def mutate(self, chromosome):
        # Mutate chromosome actions based on mutation rate
        for i in range(len(chromosome)):
            if random.random() < self.mutation_rate:
                chromosome[i] = random.choice(['jump', 'move_left', 'move_right', 'idle'])
        return chromosome

    def evolve(self):
        # Create a new generation using selection, crossover, and mutation
        new_population = []
        for _ in range(self.population_size // 2):
            parent1, parent2 = self.selection()
            child1, child2 = self.crossover(parent1, parent2)
            child1.chromosome = self.mutate(child1.chromosome)
            child2.chromosome = self.mutate(child2.chromosome)
            new_population.extend([child1, child2])
        self.population = new_population

    def save_population(self, filename="population.json"):
        # Save current population to a JSON file
        population_data = [
            {
                "chromosome": agent.chromosome,
                "position": {"x": agent.rect.x, "y": agent.rect.y}
            }
            for agent in self.population
        ]
        with open(filename, "a") as file:
            json.dump(population_data, file, indent=4)
        print("Population saved successfully to", filename)
