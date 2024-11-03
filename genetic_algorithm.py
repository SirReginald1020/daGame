# genetic_algorithm.py

import random
import math
import pygame
import json
import torch
import torch.nn as nn
import torch.optim as optim


class Agent(pygame.sprite.Sprite):
    def __init__(self, network, platforms_data, goal_x=3900, start_x=80, start_y=1000):
        super().__init__()
        self.network = network  # The agent's neural network
        self.platforms_data = platforms_data  # Static platform data for context
        self.rect = pygame.Rect(start_x, start_y, 34, 57)  # Starting position and size
        self.vel_y = 0
        self.air_time = 0  # To penalize air time and discourage unnecessary jumping
        self.speed = 4.5
        self.jumping = False
        self.goal_x = goal_x
        self.totalDistanceTraveled = 0  # Reward them for minimizing this while reaching the goal

    def perform_action(self):
        # Process the inputs to the network (use distances to platforms and goal)
        inputs = self.calculate_inputs()
        inputs_tensor = torch.tensor(inputs, dtype=torch.float32).unsqueeze(0)  # Single batch

        # Predict action probabilities
        with torch.no_grad():
            output = self.network(inputs_tensor)
        action = torch.argmax(output).item()  # Get the action with the highest score

        # Map neural network output to actions
        if action == 0:  # Move left
            self.rect.x -= self.speed
        elif action == 1:  # Move right
            self.rect.x += self.speed
        elif action == 2 and not self.jumping:  # Jump
            self.vel_y = -11  # Jump strength
            self.jumping = True
        if self.jumping:
            self.air_time += 1  # Increment air_time when off the ground

    def calculate_inputs(self):
        # Encode the agent's state, platform information, and goal distance
        closest_platform = self.get_nearest_platform_below()
        goal_distance = self.goal_x - self.rect.x

        # Inputs could include (as an example):
        # [agent x, agent y, closest platform x, closest platform y, distance to goal]
        inputs = [
            self.rect.x / 1000,  # Normalize to smaller range
            self.rect.y / 1000,
            closest_platform["x"] / 1000,
            closest_platform["y"] / 1000,
            goal_distance / 1000
        ]
        return inputs

    def get_nearest_platform_below(self):
        # Calculate and return the nearest platform below or near the agent's x position
        platforms_below = [p for p in self.platforms_data if p["x"] <= self.rect.x <= p["x"] + p["width"]]
        if platforms_below:
            return min(platforms_below, key=lambda p: abs(p["y"] - self.rect.y))
        return {"x": 0, "y": 1100}  # Default to a platform at the bottom if none found

    def apply_gravity(self):
        # Apply gravity to vertical velocity and update position
        self.vel_y += 0.35  # Gravity strength
        self.rect.y += self.vel_y

    def update(self, platforms):
        # Perform action, apply gravity, and check for collisions
        self.perform_action()  # Call without an argument
        self.apply_gravity()
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
                self.jumping = False  # Can jump again
                self.air_time = 0  # Reset air_time when back on the ground
            elif self.vel_y < 0:  # Jumping up
                self.rect.top = hits[0].rect.bottom
                self.vel_y = 0
        else:
            if not self.jumping:
                self.jumping = True
                self.air_time += 1  # Increment when jumping starts

    def draw(self, screen, camera):
        # Draw the agent on screen adjusted by camera position
        offset_position = camera.apply(self)
        pygame.draw.rect(screen, (255, 0, 0), offset_position)  # Draw agent as a red rectangle


class AgentNetwork(nn.Module):
    def __init__(self):
        super(AgentNetwork, self).__init__()
        self.fc1 = nn.Linear(5, 64)  # Adjust input size based on number of input features
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 3)  # Output size 3 for left, right, and jump

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)  # Raw logits (softmax can be applied later for probabilities)


class GABrain:
    def __init__(self, population_size, mutation_rate, crossover_rate, goal_x,
                 platforms_file="Levels/Mario.json"):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        # Load and parse platform data
        with open(platforms_file, "r") as file:
            self.platforms_data = json.load(file)
        self.goal_x = goal_x
        self.generation = 0
        self.population = self.initialize_population()
        
    def initialize_population(self):
        # Initialize a population of agents with random neural networks
        population = []
        for _ in range(self.population_size):
            network = AgentNetwork()  # Each agent gets a unique network
            agent = Agent(network=network, platforms_data=self.platforms_data, goal_x=self.goal_x)
            population.append(agent)
        return population

    def calculate_fitness(self, agent):
        # Fitness is based on distance to the goal, penalized by total travel distance
        distance_to_goal = abs(self.goal_x - agent.rect.x)
        fitness = (1 / (distance_to_goal + 1)) * 10 - 0.01 * agent.totalDistanceTraveled
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
        # Create two children with new networks
        child1, child2 = AgentNetwork(), AgentNetwork()

        # Loop over each parameter in both parent networks
        for p1, p2, c1, c2 in zip(parent1.parameters(), parent2.parameters(), child1.parameters(), child2.parameters()):
            # Blend the parameters of the parents to create children
            c1.data.copy_(0.5 * p1.data + 0.5 * p2.data)
            c2.data.copy_(0.5 * p1.data + 0.5 * p2.data)

        return child1, child2

    def mutate(self, network):
        for param in network.parameters():
            if random.random() < self.mutation_rate:  # Use dynamic rate
                param.data += torch.randn_like(param) * 0.1  # Small random mutation

    def evolve(self):
        # Exponential decay: adjust the decay rate as needed
        decay_rate = 0.005
        # Uncomment out the line below to have gradual mutation rate decay
        # self.mutation_rate = self.mutation_rate * math.exp(-decay_rate * self.generation)
        self.generation += 1

        # Selection and mutation logic remains the same
        sorted_population = sorted(self.population, key=lambda agent: self.calculate_fitness(agent), reverse=True)
        top_half = sorted_population[:self.population_size // 2]

        new_population = []
        for _ in range(self.population_size // 2):
            parent1, parent2 = random.choice(top_half), random.choice(top_half)
            child1, child2 = self.crossover(parent1.network, parent2.network)
            self.mutate(child1)  # Use updated mutation rate
            self.mutate(child2)
            new_population.extend([Agent(child1, self.platforms_data), Agent(child2, self.platforms_data)])

        self.population = new_population

    def save_population(self, filename="population.json"):
        """Save the neural network weights of the population."""
        population_data = []
        for agent in self.population:
            state_dict = agent.network.state_dict()  # Extract network weights
            # Convert tensor values to lists for JSON compatibility
            network_data = {k: v.tolist() for k, v in state_dict.items()}
            population_data.append(network_data)

        with open(filename, "w") as file:
            json.dump(population_data, file, indent=4)
        print("Population saved successfully to", filename)

    def load_population(self, filename="population.json"):
        """Load the neural network weights to create a new generation."""
        try:
            with open(filename, "r") as file:
                population_data = json.load(file)
                loaded_population = []
                for network_data in population_data:
                    network = AgentNetwork()  # Create a new network instance
                    # Convert list back to tensors and load into network
                    state_dict = {k: torch.tensor(v) for k, v in network_data.items()}
                    network.load_state_dict(state_dict)

                    # Initialize a new agent with this loaded network
                    agent = Agent(network, self.platforms_data)
                    loaded_population.append(agent)
                self.population = loaded_population
            print("Population loaded successfully from", filename)
        except FileNotFoundError:
            print("Error: Population file not found.")

