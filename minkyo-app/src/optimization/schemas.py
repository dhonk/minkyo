from typing import Callable
from math import inf

'''
Defining globally used things here


'''

type Uid = str

# nodes for creating ride assignments
class Node():
    def __init__(self, uid: Uid):
        self.id = uid

class Car(Node):
    def __init__(self, uid: Uid, cap: int, passengers: list[Node]=[]):
        super.__init__(uid)
        self.cap = cap
        self.passengers = passengers.copy()

class Graph():
    def __init__(self, nodes: list[Uid], dist: Callable[[Uid, Uid], float]):
        self.adj = {x: {} for x in nodes}
        self.nodes = nodes.copy()
        self.dist = dist

        for i in self.nodes:
            for j in self.nodes:
                self.adj[i][j] = inf if i == j else self.dist(i, j)
