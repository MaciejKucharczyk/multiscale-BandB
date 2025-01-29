import sys
import os

# Dodaje katalog główny do sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gpubb import branch_and_bound_gpu
from data.data_generator import generate_knapsack_data, create_items_table

class Item:
    def __init__(self, index, profit, weight):
        self.index = index
        self.profit = profit
        self.weight = weight
        self.profit_per_weight = 0.0


def main_gpu():
    weights, profits, capacity = generate_knapsack_data(100, 100, 50, 1000)  # num_items, max_value, max_weight, capacity
    n = 100
    W = 1000
    items = [Item(i, profits[i-1], weights[i-1]) for i in range(1, n+1)]
    for item in items:
        item.profit_per_weight = item.profit / item.weight if item.weight != 0 else 0.0
        items.sort(key=lambda x: x.profit_per_weight, reverse=True)
    
    max_profit, best_items, nodes_generated = branch_and_bound_gpu(items, W, n)
    
    print("ITEMS")
    item_table = create_items_table(weights, profits)
    print(item_table)
    
    print("PARAMS:")
    print(f"num of items = {n}")
    print(f"capacity = {W}")
    
    print("\nEND maxprofit = ", max_profit, "nodes generated = ", nodes_generated)
    print("bestitems = ", best_items)
    total_weight = sum([items[i].weight for i in best_items])
    print("total_weight = ", total_weight)

if __name__ == "__main__":
    main_gpu()
