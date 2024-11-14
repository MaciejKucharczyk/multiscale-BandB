""" Odczyt danych z trzech plikow tekstowych """
def read_knapsack(filename1, filename2, filename3, dir):
    weights = []
    profits = []
    capacity = 0
    weights_file = open(f"./data/{dir}/{filename1}", "r")
    for line in weights_file:
        weights.append(int(line))
    
    weights_file.close()
    
    try:
        profits_file = open(f"./data/{dir}/{filename2}", "r")
        for line in profits_file:
            profits.append(int(line))
            
        profits_file.close()
    except FileNotFoundError:
        print("File with Profits not found...")
        
    
    try:
        size_file = open(f"./data/{dir}/{filename3}", "r")
        capacity = int(size_file.readline())
        size_file.close()
    except FileNotFoundError:
        print("File with Size not found...")
    
    return [weights, profits, capacity]

""" Odczyt optymalnego rozwiązania """
def read_optimal_solution(filename, dir):
    optimal_solution = []
    try:
        optimal_file = open(f"./data/{dir}/{filename}", "r")
        optimal_solution = [int(line.strip()) for line in optimal_file]
        optimal_file.close()
    except FileNotFoundError:
        print("File with Optimal Solution not found...")
    return optimal_solution