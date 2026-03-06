import time
import pytest
import json

from src.optimization.schemas import *

def test_node_create():
    n = Node('hi')
    assert n.id == 'hi'

tiny_entries: dict[Uid, Uid] = {
    'a': (0,0),
    'b': (0, 1),
    'c': (1, 0),
    'd': (1, 1),
}

def tiny_dist(a: Node, b: Node) -> float:
    x_a, y_a = tiny_entries[a]
    x_b, y_b = tiny_entries[b]
    return ((x_a - x_b) ** 2 + (y_a - y_b) ** 2) ** 0.5

def test_graph_create():
    g = Graph(['a', 'b', 'c', 'd'], tiny_dist)
    assert g != None

    print(json.dumps(g.adj, indent=4))
