# knapsack.py
""" 
DZIALA
wielowatkowa i wieloprocesowa wersja algorytmu branch and bound
"""

from data.data_generator import generate_knapsack_data, create_items_table
from threading import Thread, Lock
import heapq

class Item:
    def __init__(self, index, profit, weight):
        self.index = index
        self.profit = profit
        self.weight = weight
        self.profit_per_weight = profit / weight if weight != 0 else 0

class Node:
    def __init__(self, level, profit, weight, bound, items):
        self.level = level
        self.profit = profit
        self.weight = weight
        self.bound = bound
        self.items = items

    def __lt__(self, other):
        # For max-heap based on bound
        return self.bound > other.bound

class KnapsackSolver:
    def __init__(self, items, capacity, num_threads=4):
        self.items = sorted(items, key=lambda x: x.profit_per_weight, reverse=True)
        self.capacity = capacity
        self.num_threads = num_threads
        self.max_profit = 0
        self.best_items = []
        self.lock = Lock()
        self.nodes_generated = 0

    def get_bound(self, node):
        if node.weight >= self.capacity:
            return 0
        else:
            bound = node.profit
            total_weight = node.weight
            j = node.level + 1
            while j < len(self.items) and total_weight + self.items[j].weight <= self.capacity:
                total_weight += self.items[j].weight
                bound += self.items[j].profit
                j += 1
            if j < len(self.items):
                bound += (self.capacity - total_weight) * self.items[j].profit_per_weight
            return bound

    def branch_and_bound(self):
        initial_bound = self.get_bound(Node(-1, 0, 0, 0, []))
        root = Node(-1, 0, 0, initial_bound, [])
        priority_queue = []
        heapq.heappush(priority_queue, root)
        self.nodes_generated += 1

        while priority_queue:
            node = heapq.heappop(priority_queue)
            if node.bound > self.max_profit:
                # Explore child including the next item
                next_level = node.level + 1
                if next_level >= len(self.items):
                    continue
                item = self.items[next_level]
                
                # Include the item
                u = Node(
                    next_level,
                    node.profit + item.profit,
                    node.weight + item.weight,
                    0,
                    node.items + [item.index]
                )
                if u.weight <= self.capacity and u.profit > self.max_profit:
                    with self.lock:
                        if u.profit > self.max_profit:
                            self.max_profit = u.profit
                            self.best_items = u.items
                u.bound = self.get_bound(u)
                if u.bound > self.max_profit:
                    heapq.heappush(priority_queue, u)
                    self.nodes_generated += 1

                # Exclude the item
                v = Node(
                    next_level,
                    node.profit,
                    node.weight,
                    0,
                    node.items.copy()
                )
                v.bound = self.get_bound(v)
                if v.bound > self.max_profit:
                    heapq.heappush(priority_queue, v)
                    self.nodes_generated += 1

    # Additional methods for multithreading will be added here
    def branch_and_bound_thread(self, node):
        local_max_profit = 0
        local_best_items = []
        local_nodes_generated = 0
        priority_queue = []
        heapq.heappush(priority_queue, node)
        local_nodes_generated += 1

        while priority_queue:
            current_node = heapq.heappop(priority_queue)
            if current_node.bound > local_max_profit:
                next_level = current_node.level + 1
                if next_level >= len(self.items):
                    continue
                item = self.items[next_level]
                
                # Include the item
                u = Node(
                    next_level,
                    current_node.profit + item.profit,
                    current_node.weight + item.weight,
                    0,
                    current_node.items + [item.index]
                )
                if u.weight <= self.capacity and u.profit > local_max_profit:
                    local_max_profit = u.profit
                    local_best_items = u.items
                u.bound = self.get_bound(u)
                if u.bound > local_max_profit:
                    heapq.heappush(priority_queue, u)
                    local_nodes_generated += 1

                # Exclude the item
                v = Node(
                    next_level,
                    current_node.profit,
                    current_node.weight,
                    0,
                    current_node.items.copy()
                )
                v.bound = self.get_bound(v)
                if v.bound > local_max_profit:
                    heapq.heappush(priority_queue, v)
                    local_nodes_generated += 1

        # Update the global best profit and items
        with self.lock:
            if local_max_profit > self.max_profit:
                self.max_profit = local_max_profit
                self.best_items = local_best_items
            self.nodes_generated += local_nodes_generated
            
    
    # Continue within the KnapsackSolver class

    def parallel_branch_and_bound(self):
        initial_bound = self.get_bound(Node(-1, 0, 0, 0, []))
        root = Node(-1, 0, 0, initial_bound, [])
        initial_children = []

        # Generate initial children up to the first level
        next_level = root.level + 1
        for i in range(2):  # Adjust the depth as needed
            if next_level >= len(self.items):
                break
            item = self.items[next_level]
            
            # Include the item
            u = Node(
                next_level,
                root.profit + item.profit,
                root.weight + item.weight,
                0,
                root.items + [item.index]
            )
            if u.weight <= self.capacity:
                u.bound = self.get_bound(u)
                if u.bound > self.max_profit:
                    initial_children.append(u)
                    self.nodes_generated += 1

            # Exclude the item
            v = Node(
                next_level,
                root.profit,
                root.weight,
                0,
                root.items.copy()
            )
            v.bound = self.get_bound(v)
            if v.bound > self.max_profit:
                initial_children.append(v)
                self.nodes_generated += 1

        # Limit the number of initial children to the number of threads
        initial_children = initial_children[:self.num_threads]

        threads = []
        for child in initial_children:
            thread = Thread(target=self.branch_and_bound_thread, args=(child,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()


import multiprocessing
from multiprocessing import Process, Manager

class KnapsackSolverMultiprocess:
    def __init__(self, items, capacity, num_processes=4):
        self.items = sorted(items, key=lambda x: x.profit_per_weight, reverse=True)
        self.capacity = capacity
        self.num_processes = num_processes
        self.manager = Manager()
        self.max_profit = self.manager.Value('i', 0)
        self.best_items = self.manager.list()
        self.nodes_generated = self.manager.Value('i', 0)

    def get_bound(self, node):
        if node.weight >= self.capacity:
            return 0
        else:
            bound = node.profit
            total_weight = node.weight
            j = node.level + 1
            while j < len(self.items) and total_weight + self.items[j].weight <= self.capacity:
                total_weight += self.items[j].weight
                bound += self.items[j].profit
                j += 1
            if j < len(self.items):
                bound += (self.capacity - total_weight) * self.items[j].profit_per_weight
            return bound

    def branch_and_bound_process(self, node):
        local_max_profit = 0
        local_best_items = []
        local_nodes_generated = 0
        priority_queue = []
        heapq.heappush(priority_queue, node)
        local_nodes_generated += 1

        while priority_queue:
            current_node = heapq.heappop(priority_queue)
            if current_node.bound > local_max_profit:
                next_level = current_node.level + 1
                if next_level >= len(self.items):
                    continue
                item = self.items[next_level]
                
                # Include the item
                u = Node(
                    next_level,
                    current_node.profit + item.profit,
                    current_node.weight + item.weight,
                    0,
                    current_node.items + [item.index]
                )
                if u.weight <= self.capacity and u.profit > local_max_profit:
                    local_max_profit = u.profit
                    local_best_items = u.items
                u.bound = self.get_bound(u)
                if u.bound > local_max_profit:
                    heapq.heappush(priority_queue, u)
                    local_nodes_generated += 1

                # Exclude the item
                v = Node(
                    next_level,
                    current_node.profit,
                    current_node.weight,
                    0,
                    current_node.items.copy()
                )
                v.bound = self.get_bound(v)
                if v.bound > local_max_profit:
                    heapq.heappush(priority_queue, v)
                    local_nodes_generated += 1

        # Update the global best profit and items
        with self.manager.Lock():
            if local_max_profit > self.max_profit.value:
                self.max_profit.value = local_max_profit
                self.best_items[:] = local_best_items
            self.nodes_generated.value += local_nodes_generated

    def parallel_branch_and_bound(self):
        initial_bound = self.get_bound(Node(-1, 0, 0, 0, []))
        root = Node(-1, 0, 0, initial_bound, [])
        initial_children = []

        # Generate initial children up to the first level
        next_level = root.level + 1
        for i in range(2):  # Adjust the depth as needed
            if next_level >= len(self.items):
                break
            item = self.items[next_level]
            
            # Include the item
            u = Node(
                next_level,
                root.profit + item.profit,
                root.weight + item.weight,
                0,
                root.items + [item.index]
            )
            if u.weight <= self.capacity:
                u.bound = self.get_bound(u)
                if u.bound > self.max_profit.value:
                    initial_children.append(u)

            # Exclude the item
            v = Node(
                next_level,
                root.profit,
                root.weight,
                0,
                root.items.copy()
            )
            v.bound = self.get_bound(v)
            if v.bound > self.max_profit.value:
                initial_children.append(v)

        # Limit the number of initial children to the number of processes
        initial_children = initial_children[:self.num_processes]

        processes = []
        for child in initial_children:
            process = Process(target=self.branch_and_bound_process, args=(child,))
            processes.append(process)
            process.start()

        # Wait for all processes to complete
        for process in processes:
            process.join()

