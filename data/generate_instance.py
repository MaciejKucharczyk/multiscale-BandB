from data_generator import generate_knapsack_data, create_items_table
import csv

csv_file_path = 'dane.csv'

weights, profits, capacity = generate_knapsack_data(100, 100, 50, 1000)  # Example parameters
    
    
with open(csv_file_path, mode='w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    # Zapisz nagłówki kolumn
    csv_writer.writerow(['Weights', 'Profits', 'Capacity'])

for weight, profit in zip(weights, profits):
    with open(csv_file_path, mode='a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([weight, profit, capacity])