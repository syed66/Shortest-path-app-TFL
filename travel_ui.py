from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import *
import dijkstra


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
        if current_line in lines[dijkstra.stations[node][0]]:
            path_lines.append(current_line)
        else:
            path_lines.append(dijkstra.stations[node][1])
            current_line = dijkstra.stations[node][1]
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
            current = path[idx]
        if idx == len(path) - 1:
            summary += f"{path_lines[idx]}: from {current} to {path[idx]}"
    dlg.summary.setText(summary)
    dlg.summary.adjustSize()


# Run dijkstra's algorithm on the given inputs
def run_dijkstra(graph, lines):
    source = str(dlg.travel_from.currentText())
    destination = str(dlg.travel_to.currentText())
    first_line = str(dlg.source_line.currentText())
    last_line = str(dlg.destination_line.currentText())
    path, dist = dijkstra.dijkstra(graph, dijkstra.stations[source][0], dijkstra.stations[destination][0])
    print("The shortest path is", path)
    for i in range(len(path) - 1):
        print(f"{i + 1}: from {path[i]} to {path[i + 1]}. time: {graph.get_node_by_name(dijkstra.stations[path[i]][0], path[i + 1])[1]}")
    print(f"The total trip time from {source} to {destination} is {dist[dijkstra.stations[destination][0]] + len(path) - 1}")

    clear_table()
    path_lines, changes = get_journey_lines(lines, path, first_line, last_line)

    total = 0
    for i in range(len(path)):
        if i == len(path) - 1:
            time = ""
        else:
            time = graph.get_node_by_name(dijkstra.stations[path[i]][0], path[i + 1])[1]
        add_row([path[i], path_lines[i], time, total])
        time = 0 if time == "" else time
        total = total + time + 1

    adjust_sizes()

    write_summary(path, path_lines, changes)
    dlg.total_time.adjustSize()
    dlg.total_time.setText(f"The total trip time from {source} to {destination} is {dist[dijkstra.stations[destination][0]] + len(path) - 1}")
    dlg.total_time.adjustSize()


# Clear the contents of the table
def clear_table():
    for i in range(dlg.table.rowCount()):
        dlg.table.removeRow(dlg.table.rowCount()-1)


# Add a row to the table
def add_row(lst):
    rowPosition = dlg.table.rowCount()
    dlg.table.insertRow(rowPosition)
    for i in range(4):
        dlg.table.setItem(rowPosition, i, QTableWidgetItem(str(lst[i])))


# Loading the data
def load_stations():
    graph, lines = dijkstra.load_data()
    for station in sorted(dijkstra.stations):
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


# main function
def main():
    graph, lines = load_stations()
    dlg.button.clicked.connect(lambda: run_dijkstra(graph, lines))


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    dlg = uic.loadUi("gui.ui")
    for i in range(5):
        rowPosition = dlg.table.rowCount()
        dlg.table.insertRow(rowPosition)
    clear_table()
    main()
    dlg.show()
    app.exec()
