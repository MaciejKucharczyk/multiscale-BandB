import heapq
from get_data import read_knapsack, read_optimal_solution
from init import Node, Item
from data_generator import generate_knapsack_data, visualize_knapsack_data, create_items_table

DIR = "w10c165"
OPTIMAL_FILE = "optimal.txt"
PROFITS_FILE = "profits.txt"
WEIGHTS_FILE = "weights.txt"
SIZE_FILE = "size.txt"


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
        # profit_bound += (capacity - total_weight)* items[j].ratio
        remaining_capacity = capacity - total_weight
        profit_bound += remaining_capacity * items[j].ratio
        
    # Debugowanie: wyświetlanie bound
    print(f"Node Level: {node.level}, Profit: {node.profit}, Bound: {profit_bound}")
    return profit_bound

def branch_and_bound(capacity, weights, values):
    items = [Item(value, weight) for value, weight in zip(values, weights)]
    items.sort(key=lambda x: x.ratio, reverse=True)
    n = len(items)
    
    queue = []
    
    best_solution = [0]*len(items)
    
    root = Node(-1, 0, 0, 0)
    root.bound = bound(root, n, capacity, items)

    root.solution = best_solution
    heapq.heappush(queue, (-root.bound, root))
    
    max_profit = 0
    
    
    while queue:
        _, node = heapq.heappop(queue)
        # przetwarzamy wezel, jesli jego zysk jest mniejszy niz ograniczenie
        if node.bound > max_profit:
            level = node.level + 1

            # tworzymy wezel z dodaniem elementu
            if level < n:
                new_weight = node.weight + items[level].weight
                new_profit = node.profit + items[level].value
                 
                if new_weight <= capacity:
                    # update best solution if profit is better
                    if new_profit > max_profit:
                        # print(f"Current max_profit: {max_profit}    level: {level}")
                        max_profit = new_profit
                        best_solution = node.solution.copy()
                        best_solution[level] = 1
                    # max_profit = new_profit
                    # best_solution[level] = 1
                    
                    # obliczamy granice dla nowego wezla czyli podwezla dla node
                    left_child = Node(level, new_profit, new_weight, 0)
                    left_child.bound = bound(left_child, n, capacity, items)
                    
                    
                
                    # jezeli ograniczenie jest wieksze od max profitu, tworzymy wezel
                    if left_child.bound > max_profit:
                        left_child.solution = node.solution.copy()
                        left_child.solution[level] = 1
                        heapq.heappush(queue, (-left_child.bound, left_child))
                    # else:
                        # print(f"Skipping left_child creation at level {level} due to weight {new_weight}")
                    
                # tworzymy wezel bez dodawania przedmiotu na tym poziomie
                right_child = Node(level, node.profit, node.weight, 0)
                right_child.bound = bound(right_child, n, capacity, items)
                right_child.solution = node.solution.copy()
                right_child.solution[level] = 0  # Exclude the item at this level

                
                # jezeli jego ograniczenie jest wiesze od max profitu, tworzymy wezel
                if right_child.bound > max_profit:
                    heapq.heappush(queue, (-right_child.bound, right_child))
                
                    
    return [best_solution, max_profit]

weights, profits, capacity = generate_knapsack_data(100, 100, 50, 1000) # num_items, max_value, max_weight, capacity
# weights, profits, capacity = read_knapsack(WEIGHTS_FILE, PROFITS_FILE, SIZE_FILE, DIR)

# Tworzenie tabeli
items_table = create_items_table(weights, profits)
sorted_table = items_table.sort_values(by="Value/Weight Ratio", ascending=False)
# Wyświetlenie tabeli
print(sorted_table)
print("ITEMS:")
visualize_knapsack_data(weights, profits)

solution, max_profit = branch_and_bound(capacity, weights, profits)
print(f"Max profit: {max_profit}")
print(f"Solution: {solution}")

selected_items = [i for i in range(len(solution)) if solution[i] == 1]
total_weight = sum(weights[i] for i in selected_items)
total_value = sum(profits[i] for i in selected_items)
print(f"Total weight of selected items: {total_weight}")
print(f"Total value of selected items: {total_value}")
print(f"Knapsack capacity: {capacity}")
print(f"Max profit reported: {max_profit}")
