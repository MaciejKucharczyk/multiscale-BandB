import random
import matplotlib.pyplot as plt
import pandas as pd


def generate_knapsack_data(num_items, max_value, max_weight, capacity):
    random.seed(42)
    values = [random.randint(int(max_value/3), max_value) for _ in range(num_items)]
    weights = [random.randint(int(max_weight/4), max_weight) for _ in range(num_items)]
    return weights, values, capacity

# Przykład użycia
# weights, profits, capacity = generate_knapsack_data(100, 100, 50, 1000)

# Funkcja tworzenia tabeli z przedmiotami
def create_items_table(weights, values):
    print("DEBUG: weights:", weights)
    print("DEBUG: values:", values)
    
    if not weights or not values:
        raise ValueError("ERROR: weights or values list is empty!")

    if len(weights) != len(values):
        raise ValueError("ERROR: weights and values lists have different lengths!")

    ratios = [v / w if w != 0 else 0 for v, w in zip(values, weights)]
    
    df = pd.DataFrame({
        "Index": range(len(weights)),
        "Weight": weights,
        "Value": values,
        "Value/Weight Ratio": ratios
    })

    print("Columns in DataFrame:", df.columns)  # ✅ Poprawiona linia
    print(df.head())  # Podgląd pierwszych wierszy

    pd.set_option('display.max_rows', None)  
    pd.set_option('display.max_columns', None)

    return df

def visualize_knapsack_data(weights, values):
    ratios = [v / w for v, w in zip(values, weights)]
    
    # Histogram wartości
    # plt.figure()
    # plt.hist(values, bins=10, alpha=0.7, label='Values')
    # plt.hist(weights, bins=10, alpha=0.7, label='Weights')
    # plt.title('Distribution of Values and Weights')
    # plt.xlabel('Value/Weight')
    # plt.ylabel('Frequency')
    # plt.legend()
    # plt.show()
    
    # Scatter plot wartości do wag
    plt.figure()
    plt.scatter(weights, values, alpha=0.7, c=ratios, cmap='viridis')
    plt.colorbar(label='Value-to-Weight Ratio')
    plt.title('Value vs Weight')
    plt.xlabel('Weight')
    plt.ylabel('Value')
    plt.show()
    
    # Histogram stosunku wartości do wagi
    plt.figure()
    plt.hist(ratios, bins=10, alpha=0.7, color='orange')
    plt.title('Distribution of Value-to-Weight Ratios')
    plt.xlabel('Value-to-Weight Ratio')
    plt.ylabel('Frequency')
    plt.show()