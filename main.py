# main.py

from bbmulti import Item, KnapsackSolver, KnapsackSolverMultiprocess
from data_generator import generate_knapsack_data, create_items_table

def main():
    weights, profits, capacity = generate_knapsack_data(100, 100, 50, 1000)  # num_items, max_value, max_weight, capacity
    n = 100
    W = 1000
    items = [Item(i, profits[i-1], weights[i-1]) for i in range(1, n+1)]

    num_threads = 1  # Number of threads/processes
    
    # Display Items Table
    print("\nITEMS")
    item_table = create_items_table(weights, profits)
    # print(item_table)
    

    # Using Multithreading
    print("Running Multithreaded Branch and Bound Solver")
    solver = KnapsackSolver(items, W, num_threads=num_threads)
    solver.parallel_branch_and_bound()
    print(f"Max Profit: {solver.max_profit}")
    print(f"Best Items: {sorted(solver.best_items)}")
    print(f"Nodes Generated: {solver.nodes_generated}")

    # Using Multiprocessing
    print("\nRunning Multiprocessing Branch and Bound Solver")
    solver_mp = KnapsackSolverMultiprocess(items, W, num_processes=num_threads)
    solver_mp.parallel_branch_and_bound()
    print(f"Max Profit: {solver_mp.max_profit.value}")
    print(f"Best Items: {sorted(list(solver_mp.best_items))}")
    print(f"Nodes Generated: {solver_mp.nodes_generated.value}")


    print("\nPARAMS:")
    print(f"Number of items = {n}")
    print(f"Capacity = {W}")

if __name__ == "__main__":
    main()
