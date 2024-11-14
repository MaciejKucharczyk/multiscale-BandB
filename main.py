from typing import TypedDict
import heapq
from get_data import read_knapsack, read_optimal_solution

DIR = "w10c165"
OPTIMAL_FILE = "optimal.txt"
PROFITS_FILE = "profits.txt"
WEIGHTS_FILE = "weights.txt"
SIZE_FILE = "size.txt"


class Item:
    def __init__(self, value: int, weight: int):
        self.value = value
        self.weight = weight
        self.ratio = value / weight
        
class Node:
    def __init__(self, level: int, profit: int, weight: int, bound: float):
        self.level = level
        self.profit = profit
        self.weight = weight
        self.bound = bound
        self.solution = None
        
    def __lt__(self, other):
        return self.bound > other.bound
    
    
def bound(node, n, capacity, items):
    if node.weight >= capacity:
        return 0
    
    profit_bound = node.profit
    j = node.level + 1
    total_weight = node.weight
    
    # dodajemy przedmioty az skonczy sie miejsce w plecaku
    while j < n and total_weight + items[j].weight <= capacity:
        total_weight += items[j].weight
        profit_bound += items[j].value
        j += 1
        
    # dodajemy czesc wartosci nastepnego przedmiotu 
    if j < n:
        profit_bound += (capacity - total_weight)* items[j].ratio
        
    return profit_bound

def branch_and_bound(capacity, weights, values):
    items = [Item(value, weight) for value, weight in zip(values, weights)]
    items.sort(key=lambda x: x.ratio, reverse=True)
    n = len(items)
    
    queue = []
    
    solution = [0]*len(items)
    root = Node(-1, 0, 0, 0)
    root.solution = solution
    heapq.heappush(queue, root)
    
    max_profit = -1
    
    
    while queue:
        node = heapq.heappop(queue)
        # przetwarzamy wezel, jesli jego zysk jest mniejszy niz ograniczenie
        if node.bound > max_profit:
            level = node.level + 1
            # tworzymy wezel
            if level < n:
                new_weight = node.weight + items[level].weight
                new_profit = node.profit + items[level].value
                 
                if new_weight <= capacity and new_profit > max_profit:
                    print(f"Poka max_profita: {max_profit}")
                    print(f"Na poziome: {level}")
                    max_profit = new_profit
                    solution[level] = 1
                    
                # obliczamy granice dla nowego wezla czyli podwezla dla node
                left_child = Node(level, new_profit, new_weight, 0)
                left_child.bound = bound(left_child, n, capacity, items)
                
                # jezeli ograniczenie jest wieksze od max profitu, tworzymy wezel
                if left_child.bound > max_profit:
                    heapq.heappush(queue, left_child)
                    
                # tworzymy wezel bez dodawania przedmiotu na tym poziomie
                right_child = Node(level, node.profit, node.weight, 0)
                right_child.bound = bound(right_child, n, capacity, items)
                
                # jezeli jego ograniczenie jest wiesze od max profitu, tworzymy wezel
                if right_child.bound > max_profit:
                    heapq.heappush(queue, right_child)
                    
    return [solution, max_profit]

weights, profits, capacity = read_knapsack(WEIGHTS_FILE, PROFITS_FILE, SIZE_FILE, DIR)

print(f"Weights: {weights} \n profits: {profits} \n capacity: {capacity}")

solution, max_profit = branch_and_bound(capacity, weights, profits)
print(f"Max profit: {max_profit} \n Solution: \n {solution}")