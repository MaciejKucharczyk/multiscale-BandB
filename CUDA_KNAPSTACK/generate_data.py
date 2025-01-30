from data_generator import generate_knapsack_data
import csv


# num_items = 10**4  # Liczba przedmiotów
max_value = (2**10)*3  # Maksymalna wartość
max_weight = (2**10)*4   # Maksymalna waga

num_items_list = [10**4, 20000, 50000, 10**5]

# for i in range(7):
#     weights, profits, capacity = generate_knapsack_data(num_items, max_value, max_weight, 1000)  # num_items, max_value, max_weight, capacity
#     capacity = sum(weights) // 2  # Pojemność plecaka
#     csv_file_path = f'dane_{num_items}_duze.csv'
#     with open(csv_file_path, mode='w', newline='') as csv_file:
#         csv_writer = csv.writer(csv_file)
#         # Zapisz nagłówki kolumn
#         csv_writer.writerow(['Weights', 'Profits', 'Capacity'])

#     first = True
#     for weight, profit in zip(weights, profits):
#         with open(csv_file_path, mode='a', newline='') as csv_file:
#             csv_writer = csv.writer(csv_file)
#             if first:
#                 first = False
#                 csv_writer.writerow([weight, profit, capacity])
#             else:
#                 csv_writer.writerow([weight, profit])
            
#     print(f"Wygenerowano dane do pliku: {csv_file_path}")
#     num_items *= 5  # Zwiększaj liczbę przedmiotów
    
 
# num_items = 10**6  # Liczba przedmiotów
# max_value = 2**30 - 1  # Maksymalna wartość
# max_weight = 2**30 - 1   # Maksymalna waga
 
   
for num_items in num_items_list:
    weights, profits, capacity = generate_knapsack_data(num_items, max_value, max_weight, 1000)  # num_items, max_value, max_weight, capacity
    capacity = sum(weights) // 2  # Pojemność plecaka
    csv_file_path = f'33_dane_{num_items}_male.csv'
    with open(csv_file_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        # Zapisz nagłówki kolumn
        csv_writer.writerow(['Weights', 'Profits', 'Capacity'])

    first = True
    for weight, profit in zip(weights, profits):
        with open(csv_file_path, mode='a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            if first:
                first = False
                csv_writer.writerow([weight, profit, capacity])
            else:
                csv_writer.writerow([weight, profit])
            
    print(f"Wygenerowano dane do pliku: {csv_file_path}")
    # num_items *= 5  # Zwiększaj liczbę przedmiotów




