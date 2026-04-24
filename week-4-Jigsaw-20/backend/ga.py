"""
Genetic Algorithm module for Jigsaw Puzzle Solver.
Implements chromosome representation, fitness function, selection, crossover, mutation, and elitism.
"""

import random
from typing import List, Tuple
from dataclasses import dataclass
import numpy as np

from puzzle import PuzzlePiece


@dataclass
class Individual:
    """Represents a single candidate solution (chromosome)."""
    chromosome: List[int]  # List of piece IDs
    fitness: float = 0.0


class GeneticAlgorithm:
    """
    Genetic Algorithm solver for the Jigsaw Puzzle problem.
    """

    def __init__(
        self,
        pieces: List[PuzzlePiece],
        grid_size: int = 20,
        population_size: int = 100,
        elitism_count: int = 5,
        mutation_rate: float = 0.02,
        tournament_size: int = 5
    ):
        self.pieces = pieces
        self.grid_size = grid_size
        self.total_pieces = grid_size * grid_size
        self.population_size = population_size
        self.elitism_count = elitism_count
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size

        # Build piece lookup for fitness calculation
        self.piece_map = {p.piece_id: p for p in pieces}

        # Edge weight factors (higher = more importance)
        self.horizontal_weight = 1.0  # Left-right edge matching
        self.vertical_weight = 1.0    # Top-bottom edge matching

        self.population: List[Individual] = []
        self.generation = 0
        self.best_individual: Individual = None
        # generation_history: list of dicts with keys generation, fitness, chromosome
        self.generation_history: List[dict] = []

    def create_initial_population(self) -> None:
        """Create initial population with random chromosomes."""
        self.population = []
        for _ in range(self.population_size):
            chromosome = list(range(self.total_pieces))
            random.shuffle(chromosome)
            self.population.append(Individual(chromosome=chromosome))
        self.generation = 0
        self.best_individual = None
        self.generation_history = []

    def calculate_fitness(self, chromosome: List[int]) -> float:
        """
        Calculate fitness score for a chromosome.
        Fitness is based on edge matching between adjacent pieces.
        Higher score = better matching = closer to solved puzzle.
        """
        fitness = 0.0
        max_possible = 0.0

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                pos = row * self.grid_size + col
                piece_id = chromosome[pos]
                piece = self.piece_map[piece_id]

                # Check right neighbor (horizontal matching)
                if col < self.grid_size - 1:
                    right_pos = row * self.grid_size + (col + 1)
                    right_piece_id = chromosome[right_pos]
                    right_piece = self.piece_map[right_piece_id]

                    # Compare right edge of current piece with left edge of right piece
                    edge_similarity = self._edge_similarity(piece.right_edge, right_piece.left_edge)
                    fitness += edge_similarity * self.horizontal_weight
                    max_possible += self.horizontal_weight

                # Check bottom neighbor (vertical matching)
                if row < self.grid_size - 1:
                    bottom_pos = (row + 1) * self.grid_size + col
                    bottom_piece_id = chromosome[bottom_pos]
                    bottom_piece = self.piece_map[bottom_piece_id]

                    # Compare bottom edge of current piece with top edge of bottom piece
                    edge_similarity = self._edge_similarity(piece.bottom_edge, bottom_piece.top_edge)
                    fitness += edge_similarity * self.vertical_weight
                    max_possible += self.vertical_weight

        # Normalize to 0-100 scale
        return (fitness / max_possible) * 100 if max_possible > 0 else 0

    def _edge_similarity(self, edge1: np.ndarray, edge2: np.ndarray) -> float:
        """
        Calculate similarity between two edges.
        Returns 1.0 for perfect match, 0.0 for completely different.
        Uses MSE (Mean Squared Error) converted to similarity.
        """
        mse = np.mean((edge1 - edge2) ** 2)
        # Convert MSE to similarity (max RGB difference is 255)
        max_mse = 255 ** 2
        similarity = 1.0 - (mse / max_mse)
        return max(0.0, min(1.0, similarity))

    def tournament_selection(self) -> Individual:
        """Select a parent using tournament selection."""
        tournament = random.sample(self.population, self.tournament_size)
        return max(tournament, key=lambda ind: ind.fitness)

    def order_based_crossover(self, parent1: Individual, parent2: Individual) -> Individual:
        """
        Order-based crossover (OX) for permutation chromosomes.
        Preserves the constraint that each piece appears exactly once.
        """
        size = len(parent1.chromosome)

        # Pick two crossover points
        start = random.randint(0, size - 1)
        end = random.randint(start, size - 1)

        # Create child with segment from parent1
        child_chromosome = [None] * size
        child_chromosome[start:end + 1] = parent1.chromosome[start:end + 1]

        # Fill remaining positions with pieces from parent2 in order
        parent2_pieces = [p for p in parent2.chromosome if p not in child_chromosome[start:end + 1]]

        child_idx = 0
        parent2_idx = 0
        while child_idx < size:
            if child_chromosome[child_idx] is None:
                child_chromosome[child_idx] = parent2_pieces[parent2_idx]
                parent2_idx += 1
            child_idx += 1

        return Individual(chromosome=child_chromosome)

    def mutate(self, individual: Individual) -> Individual:
        """
        Mutate an individual by swapping two random positions.
        Applied with probability mutation_rate.
        """
        if random.random() < self.mutation_rate:
            chromosome = individual.chromosome.copy()
            idx1, idx2 = random.sample(range(len(chromosome)), 2)
            chromosome[idx1], chromosome[idx2] = chromosome[idx2], chromosome[idx1]
            return Individual(chromosome=chromosome)
        return Individual(chromosome=individual.chromosome.copy())

    def evaluate_population(self) -> None:
        """Calculate fitness for all individuals in the population."""
        for individual in self.population:
            individual.fitness = self.calculate_fitness(individual.chromosome)

        # Track best individual
        current_best = max(self.population, key=lambda ind: ind.fitness)
        if self.best_individual is None or current_best.fitness > self.best_individual.fitness:
            self.best_individual = Individual(
                chromosome=current_best.chromosome.copy(),
                fitness=current_best.fitness
            )

        self.generation_history.append({
            "generation": self.generation if self.generation > 0 else 1,
            "fitness": self.best_individual.fitness,
            "chromosome": self.best_individual.chromosome.copy()
        })

    def create_next_generation(self) -> None:
        """Create the next generation using elitism, selection, crossover, and mutation."""
        # Sort population by fitness (descending)
        self.population.sort(key=lambda ind: ind.fitness, reverse=True)

        # Elitism: keep top individuals unchanged
        new_population = [
            Individual(chromosome=ind.chromosome.copy(), fitness=ind.fitness)
            for ind in self.population[:self.elitism_count]
        ]

        # Fill rest of population with offspring
        while len(new_population) < self.population_size:
            # Selection
            parent1 = self.tournament_selection()
            parent2 = self.tournament_selection()

            # Crossover
            child = self.order_based_crossover(parent1, parent2)

            # Mutation
            child = self.mutate(child)

            new_population.append(child)

        self.population = new_population
        self.generation += 1

    def run_generation(self) -> Tuple[int, float, List[int]]:
        """
        Run one generation of the genetic algorithm.
        Returns: (generation_number, best_fitness, best_chromosome)
        """
        if self.generation == 0:
            # First call: evaluate the initial random population
            self.evaluate_population()
            self.generation = 1  # Mark that generation 1 is done
        else:
            # Subsequent calls: evolve + evaluate
            self.create_next_generation()
            self.evaluate_population()

        return (
            self.generation,
            self.best_individual.fitness,
            self.best_individual.chromosome.copy()
        )

    def get_best_chromosome(self) -> List[int]:
        """Return the best chromosome found so far."""
        return self.best_individual.chromosome.copy() if self.best_individual else []

    def get_best_fitness(self) -> float:
        """Return the best fitness score found so far."""
        return self.best_individual.fitness if self.best_individual else 0.0
