# SYNTEXHUB-AI-PROJECTS
A Python-based pathfinding visualizer that demonstrates A*, Dijkstra, BFS, and DFS algorithms with interactive maze creation, multiple heuristics, animated visualization, and live algorithm statistics.
#  A* Maze Pathfinding Visualizer

An interactive Python application built with **Tkinter** that visualizes multiple pathfinding algorithms on a customizable maze. Users can create obstacles, generate mazes, and compare the behavior of different search algorithms through real-time animation.

---

##  Features

- ✅ Interactive grid-based maze editor
- ✅ Drag and drop Start and End nodes
- ✅ Draw and erase walls using the mouse
- ✅ Multiple pathfinding algorithms:
  - A* Search
  - Dijkstra's Algorithm
  - Breadth-First Search (BFS)
  - Depth-First Search (DFS)
- ✅ Three A* heuristics:
  - Manhattan Distance
  - Euclidean Distance
  - Chebyshev Distance
- ✅ Maze generation:
  - Recursive Division
  - Random Wall Generator
- ✅ Adjustable visualization speed
- ✅ Live telemetry dashboard displaying:
  - Explored nodes
  - Path cost
  - Execution time
- ✅ Unit tests included for algorithm validation

---

##  Technologies Used

- Python 3.x
- Tkinter (GUI)
- heapq
- collections
- unittest

---

##  Project Structure

``
├── main.py              # Main GUI application
├── astar.py             # Pathfinding algorithms
├── maze.py              # Maze generation algorithms
├── test_astar.py        # Unit tests
└── README.md
```

---

##  Installation

```
Run the application:

``'bash
python main.py
``
```
Run unit tests:

```bash
``
python test_astar.py
```

```

##  How to Use

1. Launch the application.
2. Choose a grid size.
3. Select a pathfinding algorithm.
4. (Optional) Select a heuristic for A* Search.
5. Draw walls by clicking and dragging on the grid.
6. Drag the Start (S) and End (E) nodes to new positions.
7. Generate a maze if desired.
8. Select animation speed.
9. Click **Visualize** to watch the algorithm find a path.

---

##  Algorithms Implemented

### A* Search
Uses heuristic functions to efficiently find the shortest path while minimizing explored nodes.

### Dijkstra's Algorithm
Guarantees the shortest path by exploring nodes based solely on distance from the start.

### Breadth-First Search (BFS)
Explores nodes level by level and guarantees the shortest path in an unweighted graph.

### Depth-First Search (DFS)
Explores as deep as possible before backtracking. It does not always produce the shortest path but is useful for traversal demonstrations.

---

##  Heuristics

The A* implementation supports three heuristic functions:

- Manhattan Distance
- Euclidean Distance
- Chebyshev Distance

These heuristics can be selected directly from the application interface.

---

##  Maze Generation

### Recursive Division
Creates structured mazes by recursively dividing the grid into chambers.

### Random Density
Generates random obstacles based on a configurable wall density.

---

##  Live Statistics

During execution the application displays:

- Number of explored nodes
- Path length (cost)
- Execution time
- Search status

---

##  Testing

The project includes comprehensive unit tests covering:

- Clear grid pathfinding
- Obstacle navigation
- Unreachable destinations
- Different A* heuristics
- BFS correctness
- DFS correctness
- Dijkstra correctness

Execute tests using:

```bash
``
python test_astar.py
'''

##  Learning Objectives

This project demonstrates:

- Graph traversal algorithms
- Heuristic search
- Priority queues
- GUI development with Tkinter
- Event-driven programming
- Maze generation algorithms
- Algorithm visualization
- Unit testing in Python

---

##  Author

GitHub: https://github.com/omkardesai168-oss
