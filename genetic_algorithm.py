# genetic_algorithm.py
import json
import random
import pygame
import torch
import torch.nn as nn
import torch.optim as optim

class Agent(pygame.sprite.Sprite):
    def __init__(self, network, platforms_data, goal_x=7960, start_x=80, start_y=1000):
        super().__init__()
        self.start_x = start_x
        self.network = network
        self.platforms_data = platforms_data
        self.rect = pygame.Rect(start_x, start_y, 34, 57)
        self.vel_y = 0
        self.air_time = 0
        self.speed = 4.5
        self.jumping = False
        self.goal_x = goal_x
        self.total_distance_traveled = 0
        self.last_x_position = self.rect.x
        self.stuck_timer = 0  # To detect if an agent is stationary
        self.moved_left = 0

    def perform_action(self):
        if self.jumping:
            self.air_time += 0.1
        # Calculate inputs based on the agent's view of nearby platforms and obstacles
        inputs = self.calculate_inputs()
        inputs_tensor = torch.tensor(inputs, dtype=torch.float32).unsqueeze(0)

        # Predict action probabilities
        with torch.no_grad():
            output = self.network(inputs_tensor)
        action = torch.argmax(output).item()

        # Action mapping
        if action == 0:  # Move left
            self.rect.x -= self.speed
            self.moved_left = True
        elif action == 1:  # Move right
            self.moved_left = False
            self.rect.x += self.speed
        elif action == 2 and not self.jumping:  # Jump only if not already in air
            self.vel_y = -11
            self.jumping = True
            self.stuck_timer = 0  # Reset if a jump is made

        # Check if the agent is stuck (no significant forward progress)
        if abs(self.rect.x - self.last_x_position) < 5:
            self.stuck_timer += 1
        else:
            self.stuck_timer = 0  # Reset if moving forward
        self.last_x_position = self.rect.x

        # Force a jump if stuck too long
        if self.stuck_timer > 60:
            self.jumping = True
            self.vel_y = -11
            self.stuck_timer = 0

    def calculate_inputs(self):
        # Build a "world map" by identifying nearby platforms and obstacles
        nearby_platforms = self.get_nearby_platforms()
        closest_obstacle = self.get_nearest_obstacle_in_front()
        goal_distance = self.goal_x - self.rect.x

        # Include information from multiple nearby platforms and the goal distance
        inputs = [
            self.rect.x / 1000,  # Normalize the agent's position
            self.rect.y / 1000,
            goal_distance / 1000
        ]

        # Add the nearest platforms (up to 3) for better spatial awareness
        for platform in nearby_platforms[:3]:  # Limit to 3 platforms for simplicity
            inputs.extend([platform["x"] / 1000, platform["y"] / 1000])

        # Pad inputs if fewer platforms are detected
        while len(inputs) < 9:
            inputs.extend([0, 0])  # Padding for missing platforms

        # Include obstacle data
        if closest_obstacle:
            inputs.extend([closest_obstacle["x"] / 1000, closest_obstacle["y"] / 1000])
        else:
            inputs.extend([0, 0])  # Padding if no obstacle in range

        return inputs

    def get_nearby_platforms(self, range=300):
        """Get platforms within a specified horizontal range."""
        return [p for p in self.platforms_data if abs(p["x"] - self.rect.x) < range]

    def get_nearest_obstacle_in_front(self, range=200):
        """Find the closest obstacle in front within a set distance."""
        obstacles = [p for p in self.platforms_data if p["x"] > self.rect.x and abs(p["y"] - self.rect.y) < range]
        if obstacles:
            return min(obstacles, key=lambda p: p["x"] - self.rect.x)
        return None

    def apply_gravity(self):
        self.vel_y += 0.35
        self.rect.y += self.vel_y

    def update(self, platforms):
        self.perform_action()
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
            if self.vel_y > 0:  # Falling
                self.rect.bottom = hits[0].rect.top
                self.vel_y = 0
                self.jumping = False  # Reset jump
            elif self.vel_y < 0:  # Jumping
                self.rect.top = hits[0].rect.bottom
                self.vel_y = 0
        else:
            if not self.jumping:
                self.jumping = True

    def draw(self, screen, camera):
        offset_position = camera.apply(self)
        pygame.draw.rect(screen, (255, 0, 0), offset_position)

class AgentNetwork(nn.Module):
    def __init__(self):
        super(AgentNetwork, self).__init__()
        self.fc1 = nn.Linear(11, 64)  # Adjust input size based on the number of input features
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
        # Fitness is based on distance to the goal, penalized by total travel distance and stationary behavior
        distance_to_goal = abs(self.goal_x - agent.rect.x)
        progress_reward = float(agent.rect.x - agent.start_x) / 10  # Reward for moving right
        if agent.rect.x > self.goal_x:
            goal_reward = 2000  # Give them super meth for winning
        else:
            goal_reward = 0
        tax_on_living = 0.1  # Set them on fire so they run faster
        # movement_penalty = abs(agent.rect.x - agent.last_x_position)
        movement_penalty = 5 if agent.moved_left else 0  # Old one above, new one only for when they go the wrong way

        fitness = (
                (1 / (distance_to_goal + 1)) * 10  # Reward for getting closer to the goal
                + progress_reward  # Direct reward for moving right
                - 0.01 * agent.total_distance_traveled  # Penalize total distance (minimize backtracking)
                - (5 if agent.moved_left else 0)  # Penalize moving left
                - tax_on_living  # Living cost
                - movement_penalty
                - agent.air_time * 0.5  # Minor penalty for jumping (discourage unnecessary jumping)
                + goal_reward
        )
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

