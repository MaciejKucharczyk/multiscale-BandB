from concurrent.futures import ThreadPoolExecutor
from init import Node, Item
from data_generator import generate_knapsack_data, visualize_knapsack_data, create_items_table
from branchandbound import bound

from concurrent.futures import ThreadPoolExecutor
import threading

from concurrent.futures import ThreadPoolExecutor, as_completed
import heapq
import threading

max_workers = 10000
concurrent_threads = 16

def process_node(node, n, capacity, items, max_profit, lock, best_solution):
    level = node.level + 1
    results = []
    
    if level < n:
        # Węzeł lewy (dodanie elementu)
        new_weight = node.weight + items[level].weight
        new_profit = node.profit + items[level].value
        new_solution = node.solution[:]
        new_solution[level] = 1
        
        if new_weight <= capacity:
            with lock:
                if new_profit > max_profit[0]:  # Zabezpieczenie zmiennej współdzielonej
                    max_profit[0] = new_profit
                    best_solution[:] = new_solution
            
            left_child = Node(level, new_profit, new_weight, 0)
            left_child.bound = bound(left_child, n, capacity, items)
            left_child.solution = new_solution
            results.append(left_child)

        # Węzeł prawy (pominięcie elementu)
        right_child = Node(level, node.profit, node.weight, 0)
        right_child.bound = bound(right_child, n, capacity, items)
        right_child.solution = node.solution[:]
        results.append(right_child)
    
    return results

def branch_and_bound_multithreaded(capacity, weights, values):
    items = [Item(value, weight) for value, weight in zip(values, weights)]
    items.sort(key=lambda x: x.ratio, reverse=True)
    n = len(items)
    
    root = Node(-1, 0, 0, 0)
    root.bound = bound(root, n, capacity, items)
    root.solution = [0] * n
    
    queue = [(-root.bound, root)]  # Kolejka priorytetowa z negatywnymi bound dla max-heap
    max_profit = [0]  # Używamy listy, aby zmienna była mutowalna w wątkach
    best_solution = [0] * n
    lock = threading.Lock()  # Blokada do synchronizacji

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        while queue:
            futures = []
            next_queue = []
            
            # Uruchamiamy wątki dla wybranych węzłów
            for _ in range(min(len(queue), concurrent_threads)):  # concurrent_threads - maksymalna liczba watkow jednoczesnie
                _, node = heapq.heappop(queue)
                futures.append(executor.submit(process_node, node, n, capacity, items, max_profit, lock, best_solution))
            
            # Zbieramy wyniki i dodajemy nowe węzły do kolejki
            for future in as_completed(futures):
                results = future.result()
                for child in results:
                    if child.bound > max_profit[0]:
                        heapq.heappush(next_queue, (-child.bound, child))
            
            queue = next_queue  # Aktualizacja kolejki

    return best_solution, max_profit[0]


weights, profits, capacity = generate_knapsack_data(100, 100, 50, 1000)


# Tworzenie tabeli
items_table = create_items_table(weights, profits)
sorted_table = items_table.sort_values(by="Value/Weight Ratio", ascending=False)
# Wyświetlenie tabeli
print(sorted_table)
visualize_knapsack_data(weights, profits)

solution, max_profit = branch_and_bound_multithreaded(capacity, weights, profits)
print("============= B AND B")
print(f"Max profit: {max_profit}")
print(f"Solution: {solution}")


