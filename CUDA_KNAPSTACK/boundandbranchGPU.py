from numba import cuda, int32
import cupy as cp
from data_generator import generate_knapsack_data
import numpy as np

# ✅ Maksymalna liczba wątków na blok
TPB = 256  

# ✅ Maksymalna liczba przedmiotów
MAX_ITEMS = 500  

@cuda.jit(device=True)
def bound(node_level, node_profit, node_weight, n, capacity, weights, values):
    """
    Oblicza ograniczenie górne dla danego węzła w pamięci współdzielonej.
    """
    if node_weight >= capacity:
        return 0  # Odcinamy gałąź, jeśli przekracza pojemność plecaka

    profit_bound = node_profit
    total_weight = node_weight
    i = node_level + 1

    while i < n and total_weight + weights[i] <= capacity:
        total_weight += weights[i]
        profit_bound += values[i]
        i += 1

    # Przybliżona wartość, jeśli zostało miejsce w plecaku
    if i < n and weights[i] > 0:
        profit_bound += (capacity - total_weight) * (values[i] / weights[i])

    return profit_bound

@cuda.jit
def process_nodes_gpu(nodes, weights, values, n, capacity, max_profit, best_solution):
    """
    Kernel CUDA do równoległego przetwarzania węzłów.
    """
    idx = cuda.grid(1)  # Pobranie unikalnego indeksu wątku

    # ✅ Pamięć współdzielona dla weights i values (dla wątków w bloku)
    shared_weights = cuda.shared.array(shape=(MAX_ITEMS,), dtype=int32)
    shared_values = cuda.shared.array(shape=(MAX_ITEMS,), dtype=int32)

    # ✅ Inicjalizacja pamięci współdzielonej (kopiujemy tylko tyle, ile trzeba)
    tx = cuda.threadIdx.x
    if tx < n:
        shared_weights[tx] = weights[tx]
        shared_values[tx] = values[tx]
    cuda.syncthreads()

    if idx < nodes.shape[0]:
        level = int(nodes[idx, 0] + 1)  
        profit = nodes[idx, 1]
        weight = nodes[idx, 2]

        if level < n:
            new_weight = weight + shared_weights[level]
            new_profit = profit + shared_values[level]

            if new_weight <= capacity:
                cuda.atomic.max(max_profit, 0, new_profit)  

                bound_value = bound(level, new_profit, new_weight, n, capacity, shared_weights, shared_values)
                
                if bound_value > max_profit[0]:  
                    best_solution[level] = 1  # Aktualizacja najlepszego rozwiązania

                    cuda.syncthreads()

                    # ✅ Dynamiczne dodawanie nowych węzłów
                    if idx + 1 < nodes.shape[0]:  
                        nodes[idx + 1, 0] = level
                        nodes[idx + 1, 1] = new_profit
                        nodes[idx + 1, 2] = new_weight
                        nodes[idx + 1, 3] = bound_value  

                    cuda.syncthreads()

def branch_and_bound_cuda(capacity, weights, values):
    """
    Implementacja Branch and Bound w CUDA z użyciem CuPy.
    """
    n = len(weights)

    if n > MAX_ITEMS:
        raise ValueError(f"Zbyt duża liczba przedmiotów: {n}, max: {MAX_ITEMS}")

    # ✅ Przekazanie danych do pamięci GPU
    d_weights = cuda.to_device(np.array(weights, dtype=np.int32))
    d_values = cuda.to_device(np.array(values, dtype=np.int32))

    # ✅ Dynamiczna alokacja węzłów
    max_nodes = n * 10
    nodes = cp.zeros((max_nodes, 4), dtype=cp.float32)
    nodes[0] = cp.array([0, 0, 0, 0], dtype=cp.float32)  # Korzeń drzewa

    max_profit = cp.array([0], dtype=cp.int32)
    best_solution = cp.zeros(n, dtype=cp.int32)

    # ✅ Przekazanie danych do GPU
    d_nodes = nodes
    d_max_profit = max_profit
    d_best_solution = best_solution

    # ✅ Uruchomienie kernela CUDA
    threads_per_block = TPB
    blocks_per_grid = (max_nodes + TPB - 1) // TPB  

    process_nodes_gpu[blocks_per_grid, threads_per_block](
        d_nodes, d_weights, d_values, n, capacity, d_max_profit, d_best_solution
    )

    # ✅ Pobranie wyników
    best_solution = d_best_solution.get()
    max_profit = d_max_profit.get()[0]

    return best_solution, max_profit

# ✅ Generowanie danych (z `data_generator.py`)
weights, profits, capacity = generate_knapsack_data(500, 100, 50, 1000)  # Większe instancje dla GPU

# ✅ Uruchomienie CUDA
solution, max_profit = branch_and_bound_cuda(capacity, weights, profits)

print("============= B AND B CUDA =============")
print(f"Max profit: {max_profit}")
print(f"Solution: {solution}")
