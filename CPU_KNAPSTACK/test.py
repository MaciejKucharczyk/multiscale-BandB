import pandas as pd
import time
import csv

from bb_multi import Item, KnapsackSolver, KnapsackSolverMultiprocess

num_items = 20000  # Liczba przedmiotów

# Wczytaj dane z pliku CSV
csv_file_path = f'33_dane_{num_items}_male.csv'  # Zmień na właściwą ścieżkę do pliku
df = pd.read_csv(csv_file_path)

# Doczytaj zmienną capacity z pierwszego wiersza
capacity = int(df.iloc[0]['Capacity'])

# Utwórz listy weights i profits
weights = df['Weights'].astype(int).tolist()
profits = df['Profits'].astype(int).tolist()

items = [Item(i, profits[i-1], weights[i-1]) for i in range(1, num_items+1)]

num_threads = 1  # Number of threads/processes

csv_file_test = f'test_threads_33_1_items_{num_items}_.csv'
with open(csv_file_test, mode='w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    # Zapisz nagłówki kolumn
    csv_writer.writerow(['Num_threads', 'time_threads', 'time_process'])

while num_threads = 1:

    """
    Threads
    """
    # Zacznij pomiar czasu
    start_time = time.perf_counter_ns()
    
    solver = KnapsackSolver(items, capacity, num_threads=num_threads)
    solver.parallel_branch_and_bound()

    # Zakończ pomiar czasu
    end_time = time.perf_counter_ns()

    # Oblicz czas wykonania w nanosekundach
    elapsed_time_th = end_time - start_time

    """
    Processes
    """
    # Zacznij pomiar czasu
    start_time = time.perf_counter_ns()

    solver_mp = KnapsackSolverMultiprocess(items, capacity, num_processes=num_threads)
    solver_mp.parallel_branch_and_bound()

    # Zakończ pomiar czasu
    end_time = time.perf_counter_ns()

    # Oblicz czas wykonania w nanosekundach
    elapsed_time_pr = end_time - start_time
    
    with open(csv_file_test, mode='a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([num_threads, elapsed_time_th, elapsed_time_pr])
        
    num_threads -= 1
    print(f"Wykonano dla {num_threads} ")