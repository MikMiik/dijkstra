class Node:
    def __init__(self, index, key, name, x, y):
        self.index = index
        self.key = str(key)
        self.name = name
        self.x = x
        self.y = y


class Edge:
    def __init__(self, from_idx, to_idx, weight):
        self.from_node = from_idx
        self.to_node = to_idx
        self.weight = weight


class TDGraph:
    def __init__(self):
        self.nodes = []
        self.adjList = []

    def addNode(self, node):
        self.nodes.append(node)
        self.adjList.append([])

    def addEdge(self, edge):
        self.adjList[edge.from_node].append(edge)

    def getNeighbors(self, vertex_index):
        return self.adjList[vertex_index]
