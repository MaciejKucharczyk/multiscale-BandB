from numba import cuda, jit
import cupy as cp  # ✅ Zamiana NumPy na CuPy

# Maksymalna liczba wątków na blok
TPB = 256  

@cuda.jit(device=True)
def bound(node_level, node_profit, node_weight, n, capacity, weights, values):
    """
    Oblicza ograniczenie górne dla danego węzła.
    """
    if node_weight >= capacity:
        return 0  # Jeśli przekracza pojemność, odcinamy gałąź

    profit_bound = node_profit
    total_weight = node_weight
    i = node_level + 1

    while i < n and total_weight + weights[i] <= capacity:
        total_weight += weights[i]
        profit_bound += values[i]
        i += 1

    # Przybliżona wartość, jeśli zostało miejsce w plecaku
    if i < n:
        profit_bound += (capacity - total_weight) * (values[i] / weights[i])

    return profit_bound

@cuda.jit
def process_nodes_gpu(nodes, weights, values, n, capacity, max_profit, best_solution):
    """
    Kernel CUDA do równoległego przetwarzania węzłów.
    """
    idx = cuda.grid(1)  # Unikalny indeks wątku

    if idx < nodes.shape[0]:
        level = int(nodes[idx, 0] + 1)  # Rzutowanie na int32
        profit = nodes[idx, 1]
        weight = nodes[idx, 2]

        if level < n:
            new_weight = weight + int(weights[level])  # Zapewnienie poprawnego typu
            new_profit = profit + int(values[level])

            if new_weight <= capacity:
                cuda.atomic.max(max_profit, 0, new_profit)  

                bound_value = bound(level, new_profit, new_weight, n, capacity, weights, values)
                
                if bound_value > max_profit[0]:  
                    best_solution[level] = 1  # Aktualizacja rozwiązania

                    # Dodajemy nowy węzeł do `nodes`
                    if idx + 1 < nodes.shape[0]:  
                        nodes[idx + 1, 0] = level
                        nodes[idx + 1, 1] = new_profit
                        nodes[idx + 1, 2] = new_weight
                        nodes[idx + 1, 3] = bound_value  # Zapisujemy ograniczenie górne

def branch_and_bound_cuda(capacity, weights, values):
    """
    Implementacja Branch and Bound w CUDA z użyciem CuPy.
    """
    n = len(weights)

    # ✅ Zamiana NumPy na CuPy
    nodes = cp.zeros((n * 10, 4), dtype=cp.float32)
    nodes[0] = cp.array([0, 0, 0, 0], dtype=cp.float32)  # Korzeń drzewa

    max_profit = cp.array([0], dtype=cp.int32)
    best_solution = cp.zeros(n, dtype=cp.int32)

    # ✅ Przekazanie danych do GPU (CuPy obsługuje to automatycznie)
    d_nodes = nodes
    d_weights = cp.array(weights, dtype=cp.int32)
    d_values = cp.array(values, dtype=cp.int32)
    d_max_profit = max_profit
    d_best_solution = best_solution

    # Uruchomienie kernela CUDA
    threads_per_block = TPB
    blocks_per_grid = (n * 10 + TPB - 1) // TPB  

    process_nodes_gpu[blocks_per_grid, threads_per_block](
        d_nodes, d_weights, d_values, n, capacity, d_max_profit, d_best_solution
    )

    # ✅ Pobranie wyników
    best_solution = d_best_solution.get()
    max_profit = d_max_profit.get()[0]

    return best_solution, max_profit

# Generowanie danych
capacity = 1000

weights = [
    50, 16, 36, 36, 50, 41, 45, 28, 47, 12, 19, 46, 29, 33, 19, 30, 39, 22, 41, 12,
    28, 44, 23, 44, 18, 31, 44, 50, 24, 21, 35, 22, 46, 45, 12, 50, 32, 43, 13, 19,
    35, 31, 27, 15, 27, 48, 17, 17, 43, 16, 46, 20, 20, 42, 47, 22, 28, 45, 50, 39,
    25, 46, 24, 31, 37, 35, 40, 45, 40, 19, 27, 26, 16, 33, 13, 49, 47, 26, 49, 26,
    12, 16, 15, 26, 16, 14, 33, 16, 44, 27, 29, 43, 25, 46, 20, 48, 48, 42, 27, 42
]

profits = [
    47, 36, 68, 64, 61, 50, 46, 44, 87, 37, 36, 44, 60, 62, 97, 36, 58, 86, 61, 90,
    68, 33, 53, 87, 76, 68, 52, 60, 76, 46, 44, 81, 45, 78, 77, 66, 38, 91, 48, 81,
    43, 70, 79, 57, 41, 38, 62, 70, 43, 62, 45, 81, 68, 91, 79, 53, 80, 78, 59, 67,
    42, 54, 64, 53, 92, 81, 67, 61, 74, 40, 62, 37, 73, 84, 67, 41, 60, 73, 60, 96,
    83, 91, 51, 66, 50, 64, 66, 87, 84, 79, 61, 50, 98, 96, 44, 39, 47, 52, 53, 87
]


solution, max_profit = branch_and_bound_cuda(capacity, weights, profits)

print("============= B AND B CUDA")
print(f"Max profit: {max_profit}")
print(f"Solution: {solution}")
