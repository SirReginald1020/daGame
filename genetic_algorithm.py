# genetic_algorithm.py

import random

class GABrain:
    def __init__(self, population_size, mutation_rate, crossover_rate, sequence_length, goal_x):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.sequence_length = sequence_length
        self.goal_x = goal_x  # X-coordinate of the level goal
        self.population = self.initialize_population()
        
    def initialize_population(self):
        # Generate a population of random chromosomes (action sequences)
        population = []
        for _ in range(self.population_size):
            chromosome = [random.choice(['jump', 'move_left', 'move_right', 'idle']) for _ in range(self.sequence_length)]
            population.append(chromosome)
        return population

    def calculate_fitness(self, agent):
        # Example fitness: distance traveled towards the goal
        distance_traveled = agent.rect.x
        fitness = distance_traveled / self.goal_x  # Normalize by the goal position
        return fitness

    def selection(self):
        # Tournament selection: pick two random agents and select the one with higher fitness
        candidates = random.sample(self.population, 2)
        return max(candidates, key=lambda agent: self.calculate_fitness(agent))

    def crossover(self, parent1, parent2):
        # Single-point crossover
        if random.random() < self.crossover_rate:
            crossover_point = random.randint(0, self.sequence_length - 1)
            child1 = parent1[:crossover_point] + parent2[crossover_point:]
            child2 = parent2[:crossover_point] + parent1[crossover_point:]
        else:
            child1, child2 = parent1[:], parent2[:]
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
            parent1 = self.selection()
            parent2 = self.selection()
            child1, child2 = self.crossover(parent1, parent2)
            new_population.append(self.mutate(child1))
            new_population.append(self.mutate(child2))
        self.population = new_population
