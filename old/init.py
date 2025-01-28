class Item:
    def __init__(self, value: int, weight: int):
        self.value = value
        self.weight = weight
        self.ratio = value / weight
        
class Node:
    def __init__(self, level: int, profit: int, weight: int, bound: float):
        self.level = level
        self.profit = profit
        self.weight = weight
        self.bound = bound
        self.solution = None
        
    def __lt__(self, other):
        return self.bound > other.bound