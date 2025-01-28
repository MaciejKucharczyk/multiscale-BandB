# -*- coding: utf-8 -*-

import threading
from queue import PriorityQueue, Empty
from data_generator import generate_knapsack_data, create_items_table

"""
Przykładowa wersja wielowątkowa algorytmu 0-1 Knapsack
z wykorzystaniem podejścia best-first branch and bound.
"""

# ----- GENEROWANIE LUB WSTAWIENIE DANYCH -----
weights, profits, capacity = generate_knapsack_data(100, 100, 50, 1000)
n = 100
W = capacity
p = [0] + profits
w = [0] + weights
p_per_weight = [0] + [p[i] / w[i] for i in range(1, n+1)]


# ----- STRUKTURY DANYCH -----
class Node:
    """
    Węzeł drzewa przeszukiwania.
    """
    def __init__(self, level, profit, weight):
        self.level = level
        self.profit = profit
        self.weight = weight
        self.items = []
        self.bound = 0.0  # bound będzie ustalany przez get_bound

    def __lt__(self, other):
        """
        Metoda __lt__ potrzebna przy używaniu PriorityQueue,
        bo klasa Node musi być porównywalna. 
        Chcemy *max-heap*, a Pythonowa PriorityQueue to *min-heap*:
        możemy przechowywać ujemną wartość bound, żeby dostać max-heap.
        """
        return self.bound > other.bound  # to jest odwrotne, jeśli bound > => "mniejszy" w sensie kolejki


def get_bound(node: Node):
    """
    Obliczanie górnej granicy (bound) dla danego węzła.
    """
    if node.weight >= W:
        return 0
    else:
        result = node.profit
        j = node.level + 1
        totweight = node.weight
        while j <= n and totweight + w[j] <= W:
            totweight += w[j]
            result += p[j]
            j += 1
        if j <= n:
            # cząstkowa część kolejnego przedmiotu (frakcja),
            # w B&B 0-1 teoretycznie się nie pakuje frakcji, 
            # ale do obliczenia bounda można użyć tej heurystyki
            result += (W - totweight) * p_per_weight[j]
        return result


# ----- ZMIENNE GLOBALNE -----
# Kolejka priorytetowa (działa jak min-heap, ale "odwrócimy" warunek w Node.__lt__ lub chowając ujemny bound).
pq = PriorityQueue()

# Globalne najlepsze rozwiązanie
maxprofit = 0
bestitems = []
total_weight = 0

# Lock do synchronizacji aktualizacji powyższych zmiennych
best_lock = threading.Lock()


def branch_and_bound_worker():
    global maxprofit, bestitems, total_weight

    while True:
        try:
            # Pobieramy węzeł z kolejki (blokująco z domyślnym timeout=nieograniczonym).
            # Możesz wstawić mały timeout, aby wątki kończyły się, gdy kolejka jest pusta:
            # node = pq.get(timeout=0.5) 
            node = pq.get(block=True)
        except Empty:
            # Kolejka pusta, kończymy wątek
            print("Pusta kolejka, watek zakonczony")
            break

        # Sprawdzamy, czy ten węzeł w ogóle może poprawić maxprofit
        if node.bound > maxprofit:
            # Rozwijamy węzeł:

            # 1) Węzeł "z przedmiotem" (jeśli jest sens wziąć kolejny item)
            u_in = Node(node.level + 1,
                        node.profit,
                        node.weight)
            u_in.items = node.items.copy()

            if u_in.level <= n:
                u_in.profit += p[u_in.level]
                u_in.weight += w[u_in.level]
                u_in.items.append(u_in.level)

                # Jeśli waga nie przekracza W, to sprawdzamy aktualizację maxprofit
                if u_in.weight <= W:
                    with best_lock:
                        if u_in.profit > maxprofit:
                            maxprofit = u_in.profit
                            bestitems = u_in.items[:]
                            total_weight = u_in.weight

                # Oblicz górną granicę i jeśli wciąż obiecująca -> wrzucamy do pq
                u_in.bound = get_bound(u_in)
                if u_in.bound > maxprofit:
                    pq.put(u_in)

            # 2) Węzeł "bez przedmiotu"
            u_out = Node(node.level + 1,
                         node.profit,
                         node.weight)
            u_out.items = node.items.copy()
            
            if u_out.level <= n:
                u_out.bound = get_bound(u_out)
                if u_out.bound > maxprofit:
                    pq.put(u_out)

        # Sygnalizujemy kolejce, że wykonaliśmy zadanie 
        pq.task_done()


def main():
    global maxprofit, bestitems, total_weight

    # Inicjalizacja drzewa (węzeł "root")
    root = Node(level=0, profit=0, weight=0)
    root.bound = get_bound(root)
    pq.put(root)

    # Uruchamiamy np. 4 wątki workerów
    NUM_THREADS = 4
    threads = []
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=branch_and_bound_worker)
        t.start()
        threads.append(t)
        
    print(f"Zainicjowano {NUM_THREADS} workerow")

    # Czekamy aż kolejka opróżni się całkowicie
    pq.join()

    # Kończymy wątki
    for t in threads:
        t.join()

    # Wyniki
    print("ITEMS")
    item_table = create_items_table(w, p)
    print(item_table)

    print("PARAMS:")
    print(f"num of items = {n}")
    print(f"capacity = {W}")

    print("\nEND maxprofit = ", maxprofit)
    print("bestitems = ", bestitems)
    print("total_weight = ", total_weight)

if __name__ == "__main__":
    main()
