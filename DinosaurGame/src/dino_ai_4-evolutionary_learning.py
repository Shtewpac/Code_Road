import random
import numpy as np
import pygame

class Individual:
    def __init__(self, genome):
        self.genome = genome
        self.fitness = 0

class Population:
    def __init__(self, size, genome_size):
        self.individuals = [Individual(np.random.rand(genome_size)) for _ in range(size)]

    def evaluate(self, game):
        fitness_scores = game.play(self.individuals)
        for individual, score in zip(self.individuals, fitness_scores):
            individual.fitness = score

    def select(self):
        self.individuals = [max(random.sample(self.individuals, k=2), key=lambda x: x.fitness) for _ in range(len(self.individuals))]

    def evolve(self):
        offspring = []
        while len(offspring) < len(self.individuals):
            parent1, parent2 = random.sample(self.individuals, k=2)
            child1, child2 = self.crossover(parent1, parent2)
            self.mutate(child1)
            self.mutate(child2)
            offspring.extend([child1, child2])
        self.individuals = offspring

    def crossover(self, parent1, parent2):
        if len(parent1.genome) == 1:
            return Individual(parent1.genome.copy()), Individual(parent2.genome.copy())
        point = random.randint(1, len(parent1.genome) - 1)
        child1_genome = np.concatenate((parent1.genome[:point], parent2.genome[point:]))
        child2_genome = np.concatenate((parent2.genome[:point], parent1.genome[point:]))
        return Individual(child1_genome), Individual(child2_genome)

    def mutate(self, individual, rate=0.1):
        individual.genome += np.random.rand(*individual.genome.shape) < rate

class EvolutionaryLearner:
    def __init__(self, population_size, genome_size, num_generations, game):
        self.population = Population(population_size, genome_size)
        self.num_generations = num_generations
        self.game = game

    def run(self):
        for generation in range(self.num_generations):
            self.population.evaluate(self.game)
            best_fitness = max(individual.fitness for individual in self.population.individuals)
            print(f"Generation {generation+1}: Best Fitness = {best_fitness}")
            self.population.select()
            self.population.evolve()
        return max(self.population.individuals, key=lambda x: x.fitness).genome

class DinosaurGame:
    def __init__(self, population_size):
        pygame.init()
        self.width, self.height = 800, 400
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Dinosaur Game - Evolutionary Learning")

        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.dino_width, self.dino_height = 40, 60
        self.cactus_width, self.cactus_height = 60, 80
        self.dino_jump_speed = -20
        self.dino_gravity = 0.8
        self.cactus_speed = 5

        self.population_size = population_size
        self.colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]  # Add more colors if needed

    def play(self, population):
        game_instances = []
        for i in range(self.population_size):
            dino_x, dino_y = 50, self.height - self.dino_height - 10
            dino_y_velocity = 0
            cactus_x, cactus_y = self.width // self.population_size * (i + 1), self.height - self.cactus_height - 10
            game_instances.append({"dino_x": dino_x, "dino_y": dino_y, "dino_y_velocity": dino_y_velocity,
                                "cactus_x": cactus_x, "cactus_y": cactus_y, "score": 0})

        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return [game_instance["score"] for game_instance in game_instances]

            self.screen.fill(self.WHITE)

            for i, (individual, game_instance) in enumerate(zip(population, game_instances)):
                # Get the input state for the individual
                distance_to_obstacle = (game_instance["cactus_x"] - game_instance["dino_x"]) / (self.width // self.population_size)
                input_state = np.array([distance_to_obstacle, game_instance["dino_y_velocity"]])

                # Decide action based on the individual's genome
                action = np.dot(individual.genome, input_state) > 0.5

                if action and game_instance["dino_y"] == self.height - self.dino_height - 10:  # Jump action
                    game_instance["dino_y_velocity"] = self.dino_jump_speed
                else:  # Wait action
                    if game_instance["dino_y"] < self.height - self.dino_height - 10:
                        game_instance["dino_y_velocity"] += self.dino_gravity
                    else:
                        game_instance["dino_y_velocity"] = 0

                game_instance["dino_y"] += game_instance["dino_y_velocity"]
                game_instance["dino_y"] = min(game_instance["dino_y"], self.height - self.dino_height - 10)

                # Move the cactus
                game_instance["cactus_x"] -= self.cactus_speed
                if game_instance["cactus_x"] < -self.cactus_width:
                    game_instance["cactus_x"] = self.width // self.population_size
                    game_instance["score"] += 1

                # Check for collision
                if game_instance["dino_x"] + self.dino_width > game_instance["cactus_x"] and \
                game_instance["dino_y"] + self.dino_height > game_instance["cactus_y"]:
                    individual.fitness = game_instance["score"]
                    game_instance["dino_y"] = self.height - self.dino_height - 10
                    game_instance["cactus_x"] = self.width // self.population_size
                    game_instance["score"] = 0

                # Draw the dinosaur and cactus for each game instance
                color = self.colors[i % len(self.colors)]
                pygame.draw.rect(self.screen, color, (game_instance["dino_x"], game_instance["dino_y"],
                                                    self.dino_width, self.dino_height))
                pygame.draw.rect(self.screen, color, (game_instance["cactus_x"], game_instance["cactus_y"],
                                                    self.cactus_width, self.cactus_height))

                # Display the score for each game instance
                font = pygame.font.Font(None, 36)
                score_text = font.render(f"Score: {game_instance['score']}", True, color)
                self.screen.blit(score_text, (game_instance["dino_x"], game_instance["dino_y"] - 30))

            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    population_size = 5
    genome_size = 2  # Update to match the input state size
    num_generations = 10

    game = DinosaurGame(population_size)
    learner = EvolutionaryLearner(population_size, genome_size, num_generations, game)
    best_genome = learner.run()

    print("Best Genome:", best_genome)
unknown