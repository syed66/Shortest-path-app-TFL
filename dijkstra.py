import pandas as pd
import math
import sys

stations = {}


# graph node
class Node:
    def __init__(self, value):
        self.value = value
        self.next = None
        self.prev = None


# doubly linked list data structure to store the connections between the nodes
class Doubly_linked_list:
    def __init__(self):
        self.head = None

    # appending a node to the list
    def append(self, value):
        new_node = Node(value)
        new_node.next = None
        if self.head is None:
            new_node.prev = None
            self.head = new_node
            return
        current = self.head
        while current.next is not None:
            current = current.next
        current.next = new_node
        new_node.prev = current
        return

    # get the value of the node at index (idx)
    def get_node(self, idx):
        cnt = 0
        current = self.head
        while current is not None:
            if cnt == idx:
                return current.value
            current = current.next
            cnt += 1
        return None

    # get the value of the node(station) that have the name (node)
    def get_node_by_name(self, node):
        current = self.head
        while current is not None:
            if get_station_name(current.value[0]) == node:
                return current.value
            current = current.next
        return None

    # get the size of the list
    def get_size(self):
        size = 0
        current = self.head
        while current is not None:
            current = current.next
            size += 1
        return size

    # print the elements of the list
    def print_list(self):
        current = self.head
        while current is not None:
            print(current.value, end=' ==> ')
            current = current.next


# graph representation adjacency list
class Graph:
    def __init__(self, num_vertices):
        self.V = num_vertices
        self.graph = [None] * num_vertices
        for i in range(num_vertices):
            self.graph[i] = Doubly_linked_list()

    # adding an edge to the graph that (from source_node --> station of value (value))
    def add_edge(self, source_node, value):
        self.graph[source_node].append(value)

    # get the node(station) that is connected to source_node at index (idx)
    def get_node(self, source_node, idx):
        return self.graph[source_node].get_node(idx)

    # get the node that is connected to source_node and has the name (node)
    def get_node_by_name(self, source_node, node):
        return self.graph[source_node].get_node_by_name(node)

    # get the number of neighbors of a node in the graph
    def get_num_neighbors(self, node):
        return self.graph[node].get_size()

    # print the graph
    def print_graph(self):
        for i in range(self.V):
            print(i, end=" : ")
            self.graph[i].print_list()
            print("\n")


# Get the node with minimum distance from source that is not yet processed
def min_dist_node(dist, vis, num_nodes):
    min_dist = sys.maxsize
    selected_node = None
    for node in range(num_nodes):
        if vis[node] is False and dist[node] < min_dist:
            min_dist = dist[node]
            selected_node = node
    return selected_node


# Get the shortest path from source to destination
def get_path(prev, node, source):
    current = node
    path = [get_station_name(node)]
    while current != source:
        current = prev[current]
        path.append(get_station_name(current))
    return path[::-1]


# Dijkstra algorithm for calculating the shortest path from source to destination in the given graph
def dijkstra(graph, source, destination):

    # initializing
    dist = [sys.maxsize] * graph.V
    dist[source] = 0
    vis = [False] * graph.V
    prev = [None] * graph.V

    # iterating over the nodes
    for i in range(graph.V):
        u = min_dist_node(dist, vis, graph.V)
        vis[u] = True

        # relaxation
        for j in range(graph.get_num_neighbors(u)):
            v = graph.get_node(u, j)
            if not vis[v[0]] and dist[v[0]] > dist[u] + v[1]:
                dist[v[0]] = dist[u] + v[1]
                prev[v[0]] = u

    path = get_path(prev, destination, source)
    return path, dist


# Get a station name depending on its index
def get_station_name(station_num):
    lst = [k for k, v in stations.items() if v[0] == station_num]
    if lst:
        return lst[0]


# Load the data from the data sheet and creating the graph
def load_data():
    graph = Graph(270)
    lines = [None] * graph.V
    for i in range(graph.V):
        lines[i] = []
    cnt = 1
    df = pd.read_excel(r'London Underground data.xlsx')
    stations[df.columns[1].strip()] = (0, df.columns[0].strip())
    lines[0].append(df.columns[0].strip())
    df.columns = range(4)
    for idx, row in df.iterrows():
        row[1] = row[1].strip()
        if idx == 208:
            row[0] = "Circle"
        row[0] = row[0].strip()
        if math.isnan(row[3]):
            if row[1] not in stations:
                stations[row[1]] = (cnt, row[0])
                cnt += 1
            lines[stations[row[1]][0]].append(row[0])
        else:
            row[2] = row[2].strip()
            graph.add_edge(stations[row[1]][0], (stations[row[2]][0], row[3]))
            graph.add_edge(stations[row[2]][0], (stations[row[1]][0], row[3]))
    return graph, lines


# Main function
def main():
    graph, lines = load_data()
    dijkstra(graph, stations["Maida Vale"][0], stations["Westbourne Park"][0])


if __name__ == "__main__":
    main()
