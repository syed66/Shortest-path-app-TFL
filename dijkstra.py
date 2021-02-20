import pandas as pd
import math
import sys
import time
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import *
import matplotlib.pyplot as plt
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

    # get the value of the node
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


# returns the shortest path from source to destination
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
    dist = [sys.maxsize] * graph.V #assigning each node to infinity
    dist[source] = 0 #the source distance intialised as 0
    vis = [False] * graph.V#intialisting a visited list
    prev = [None] * graph.V

    # iterating over the nodes
    for i in range(graph.V):
        u = min_dist_node(dist, vis, graph.V)
        vis[u] = True

        # relaxation
        for j in range(graph.get_num_neighbors(u)):
            v = graph.get_node(u, j)
            if not vis[v[0]] and dist[v[0]] > dist[u] + v[1]:#if the distance of the node is greater than the distance between the 2 nodes plus the distance to the source node
                dist[v[0]] = dist[u] + v[1]
                prev[v[0]] = u  #for each node we store the previous node, so we can go backwards also, so we use it to get the path

    path = get_path(prev, destination, source)
    # returns the path, and the dist (time taken) for the journey
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
        if math.isnan(row[3]):#checks for duplicate stations and wether the third column is empty
            if row[1] not in stations:
                stations[row[1]] = (cnt, row[0])
                cnt += 1
            lines[stations[row[1]][0]].append(row[0])
        else: #If there is something in the 3rd column you add edge
            row[2] = row[2].strip()#stripping of whitespace
            # Adding the connection to the graph
            graph.add_edge(stations[row[1]][0], (stations[row[2]][0], row[3]))
            graph.add_edge(stations[row[2]][0], (stations[row[1]][0], row[3]))

    return graph, lines



#############################################GUI#################################
# Get the correct lines along the shortest path
def get_journey_lines(lines, path, first_line, last_line):
    path_lines = []
    changes = []
    current_line = first_line
    change_idx = 0
    for idx in range(len(path)):
        node = path[idx]
        if idx == len(path) - 1:
            if current_line != last_line:
                for i in range(change_idx, len(path) - 1):
                    path_lines[i] = last_line
                path_lines.append(last_line)
                break
        if current_line in lines[stations[node][0]]:
            path_lines.append(current_line)
        else:
            path_lines.append(stations[node][1])
            current_line = stations[node][1]
            change_idx = idx
            changes.append(change_idx)
    return path_lines, changes


# Write the journey summary
def write_summary(path, path_lines, changes):
    dlg.summary.setText("")
    current = path[0]
    summary = "Journey summary:\n"
    for idx in range(len(path)):
        if idx in changes:
            summary += f"{path_lines[idx-1]}: from {current} to {path[idx-1]}\n"
            summary += f"change\n"
            current = path[idx-1]
        if idx == len(path) - 1:
            summary += f"{path_lines[idx]}: from {current} to {path[idx]}"
    dlg.summary.setText(summary)
    dlg.summary.adjustSize()


# Run dijkstra's algorithm on the given inputs
def run_dijkstra(graph, lines):
    # getting text input from user
    source = str(dlg.travel_from.currentText())
    destination = str(dlg.travel_to.currentText())
    first_line = str(dlg.source_line.currentText())
    last_line = str(dlg.destination_line.currentText())
    path, dist = dijkstra(graph, stations[source][0], stations[destination][0])
    print("The shortest path is", path)
    for i in range(len(path) - 1):
        print(f"{i + 1}: from {path[i]} to {path[i + 1]}. time: {graph.get_node_by_name(stations[path[i]][0], path[i + 1])[1]}")
    print(f"The total trip time from {source} to {destination} is {dist[stations[destination][0]] + len(path) - 1} Minutes")

    clear_table()
    path_lines, changes = get_journey_lines(lines, path, first_line, last_line)

    total = 0
    for i in range(len(path)):
        if i == len(path) - 1:
            time = ""
        else:
            time = graph.get_node_by_name(stations[path[i]][0], path[i + 1])[1]
        add_row([path[i], path_lines[i], time, total])
        time = 0 if time == "" else time
        total = total + time + 1

    adjust_sizes()

    write_summary(path, path_lines, changes)
    dlg.total_time.adjustSize()
    dlg.total_time.setText(f"The total trip time from {source} to {destination} is {dist[stations[destination][0]] + len(path) - 1} Minutes")
    dlg.total_time.adjustSize()


# Clear the contents of the table after query
def clear_table():
    for i in range(dlg.table.rowCount()):
        dlg.table.removeRow(dlg.table.rowCount()-1)


# Add a row to the table to present the path
def add_row(lst):
    rowPosition = dlg.table.rowCount()
    dlg.table.insertRow(rowPosition)
    for i in range(4):
        dlg.table.setItem(rowPosition, i, QTableWidgetItem(str(lst[i])))


# Loading the data and stations to the input fields
def load_stations():
    graph, lines = load_data()
    for station in sorted(stations):
        dlg.travel_from.addItem(station)
        dlg.travel_to.addItem(station)
    lst = []
    for item in lines:
        for line in item:
            lst.append(line)
    for i in sorted(list(set(lst))):
        dlg.source_line.addItem(i)
        dlg.destination_line.addItem(i)
    dlg.travel_from.adjustSize()
    dlg.travel_to.adjustSize()
    dlg.destination_line.adjustSize()
    dlg.source_line.adjustSize()
    return graph, lines


# Adjusting the sizes of the elements to fit data
def adjust_sizes():
    dlg.label.adjustSize()
    dlg.label_3.adjustSize()
    dlg.label_2.adjustSize()
    dlg.label_4.adjustSize()
    header = dlg.table.horizontalHeader()
    header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
    header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
    dlg.table.adjustSize()


# main function to run
def main():
    # to print doubly linked list used in graph
    plt.ion()
    graph, lines = load_data()
    #graph.print_graph()
    timeList=[]
    x=[x for x in range(100)]
    for i in range(100):
        t1= time.time()
        dijkstra(graph,stations['Maida Vale'][0], stations['Westbourne Park'][0])
        t2=time.time()
        timeList.append(t2-t1)
    print(timeList)
    fig=plt.figure()
    #ax=fig.add_axes([0,0,1,1])
    plt.plot(x,timeList,lw=3,marker='o')
    import numpy as np
    y_ticks=np.arange(0,0.4,0.05)
    plt.yticks(y_ticks)
    plt.show(block=True)
    # graph, lines = load_stations()
    # dlg.button.clicked.connect(lambda: run_dijkstra(graph, lines))
    # print(stations)

if __name__ == '__main__':
    # if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    #     QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    #
    # if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    #     QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    # app = QtWidgets.QApplication([])
    # dlg = uic.loadUi("gui.ui")
    # for i in range(5):
    #     rowPosition = dlg.table.rowCount()
    #     dlg.table.insertRow(rowPosition)
    #
    # clear_table()
    main()
    # dlg.show()
    # app.exec()

