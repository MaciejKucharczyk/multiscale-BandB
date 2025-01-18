from typing import TypedDict
import heapq
from get_data import read_knapsack, read_optimal_solution
from branchandbound import bound, branch_and_bound
from data_generator import generate_knapsack_data

DIR = "w10c165"
OPTIMAL_FILE = "optimal.txt"
PROFITS_FILE = "profits.txt"
WEIGHTS_FILE = "weights.txt"
SIZE_FILE = "size.txt"


def bandb():
    weights, profits, capacity = read_knapsack(WEIGHTS_FILE, PROFITS_FILE, SIZE_FILE, DIR)

    print(f"Weights: {weights} \n profits: {profits} \n capacity: {capacity}")

    solution, max_profit = branch_and_bound(capacity, weights, profits)
    print(f"Max profit: {max_profit} \n Solution: \n {solution}")
    
import itertools

def knapsack_brute_force(weights, values, capacity):
    num_items = len(weights)
    max_value = 0
    best_combination = []

    # Iterujemy po wszystkich możliwych kombinacjach przedmiotów
    for combination in itertools.product([0, 1], repeat=num_items):
        total_weight = sum(weights[i] * combination[i] for i in range(num_items))
        total_value = sum(values[i] * combination[i] for i in range(num_items))

        # Sprawdzamy, czy waga nie przekracza pojemności plecaka
        if total_weight <= capacity and total_value > max_value:
            max_value = total_value
            best_combination = combination

    return max_value, best_combination

