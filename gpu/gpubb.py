import numpy as np
from numba import cuda, float32, int32

class Node:
    def __init__(self, level, profit, weight, bound, items):
        self.level = level
        self.profit = profit
        self.weight = weight
        self.bound = bound
        self.items = items

@cuda.jit(device=True)
def calculate_bound_kernel(levels, profits, weights, p_per_weight, n, capacity, bounds):
    idx = cuda.grid(1)
    if idx < len(levels):
        level = levels[idx]
        profit = profits[idx]
        weight = weights[idx]
        
        if weight >= capacity:
            bounds[idx] = 0.0
        else:
            bound = profit
            totweight = weight
            j = level + 1
            while j < n and totweight + weights[j] <= capacity:
                totweight += weights[j]
                bound += profits[j]
                j += 1
            if j < n:
                bound += (capacity - totweight) * p_per_weight[j]
            bounds[idx] = bound
            
def calculate_bounds_gpu(nodes, items, capacity, n):
    num_nodes = len(nodes)

    # Przygotowanie danych
    levels = np.array([node.level for node in nodes], dtype=np.int32)
    profits = np.array([node.profit for node in nodes], dtype=np.float32)
    weights = np.array([node.weight for node in nodes], dtype=np.float32)
    p_per_weight = np.array([item.profit_per_weight for item in items], dtype=np.float32)

    bounds = np.zeros(num_nodes, dtype=np.float32)

    # Kopiowanie danych na GPU
    d_levels = cuda.to_device(levels)
    d_profits = cuda.to_device(profits)
    d_weights = cuda.to_device(weights)
    d_p_per_weight = cuda.to_device(p_per_weight)
    d_bounds = cuda.to_device(bounds)

    # Definicja konfiguracji kernela
    threads_per_block = 256
    blocks_per_grid = (num_nodes + (threads_per_block - 1)) // threads_per_block

    # Wywołanie kernela
    calculate_bound_kernel[blocks_per_grid, threads_per_block](d_levels, d_profits, d_weights, d_p_per_weight, n, capacity, d_bounds)

    # Kopiowanie wyników z powrotem na CPU
    bounds = d_bounds.copy_to_host()

    return bounds

def get_initial_bound(node, capacity, items):
    if node.weight >= capacity:
        return 0
    else:
        bound = node.profit
        total_weight = node.weight
        j = node.level + 1
        while j < len(items) and total_weight + items[j].weight <= capacity:
            total_weight += items[j].weight
            bound += items[j].profit
            j += 1
        if j < len(items):
            bound += (capacity - total_weight) * items[j].profit_per_weight
        return bound

def branch_and_bound_gpu(items, capacity, n):
    max_profit = 0
    best_items = []
    nodes_generated = 0
    
    initial_bound = get_initial_bound(Node(-1, 0, 0, 0.0, []), capacity, items)
    
    # Inicjalizacja korzenia
    root = Node(-1, 0, 0, initial_bound, [])
    queue = [root]
    nodes_generated += 1
    
    while len(queue) > 0:
        # Pobranie węzła z kolejki (najwyższy bound)
        node = queue.pop(0)
        if node.bound > max_profit:
            next_level = node.level + 1
            if next_level >= n:
                continue
            item = items[next_level]
            
            # Włączenie przedmiotu
            u_profit = node.profit + item.profit
            u_weight = node.weight + item.weight
            u_items = node.items.copy()
            u_items.append(next_level)
            if u_weight <= capacity and u_profit > max_profit:
                max_profit = u_profit
                best_items = u_items
            # Tworzenie węzła u
            u = Node(next_level, u_profit, u_weight, 0.0, u_items)
            
            # Wyłączenie przedmiotu
            v = Node(next_level, node.profit, node.weight, 0.0, node.items.copy())
            
            # Dodanie węzłów do listy do przetworzenia
            queue.append(u)
            queue.append(v)
            nodes_generated += 2
            
            # Obliczanie bounds na GPU
            bounds = calculate_bounds_gpu(queue, items, capacity, n)
            for i, bound in enumerate(bounds):
                if bound > max_profit:
                    queue[i].bound = bound
                else:
                    queue[i].bound = 0.0  # Przycinanie
            
            # Filtracja kolejki
            queue = [node for node in queue if node.bound > max_profit]
    
    return max_profit, best_items, nodes_generated

