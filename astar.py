import math
import heapq
from collections import deque

class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.is_wall = False
        self.is_start = False
        self.is_end = False
        
        # A* values
        self.g = float('inf')  # Cost from start to current node
        self.h = 0.0           # Heuristic estimate to end
        self.f = float('inf')  # Total cost (g + h)
        self.parent = None
        
        # State tracking for visualization
        self.is_visited = False
        self.is_open = False
        
    def reset(self):
        """Reset A* specific fields, retaining wall/start/end designations."""
        self.g = float('inf')
        self.h = 0.0
        self.f = float('inf')
        self.parent = None
        self.is_visited = False
        self.is_open = False

    def __lt__(self, other):
        # Tie-breaker: prefer node with lower h (closer to goal) if f-scores are equal
        if self.f == other.f:
            return self.h < other.h
        return self.f < other.f

def manhattan_distance(node1, node2):
    return abs(node1.row - node2.row) + abs(node1.col - node2.col)

def euclidean_distance(node1, node2):
    return math.sqrt((node1.row - node2.row) ** 2 + (node1.col - node2.col) ** 2)

def chebyshev_distance(node1, node2):
    return max(abs(node1.row - node2.row), abs(node1.col - node2.col))

def get_heuristic(name):
    if name == "Manhattan":
        return manhattan_distance
    elif name == "Euclidean":
        return euclidean_distance
    elif name == "Chebyshev":
        return chebyshev_distance
    return manhattan_distance

def reconstruct_path(end_node):
    path = []
    current = end_node
    while current is not None:
        path.append(current)
        current = current.parent
    path.reverse()
    return path

def astar_search(grid, start_node, end_node, heuristic_name="Manhattan"):
    """
    Executes the A* pathfinding algorithm.
    Yields step summaries for animated visualization:
      ("open", node): node added to open set
      ("close", node): node explored and added to closed/visited set
      ("success", path): shortest path found
      ("failure", None): target is unreachable
    """
    heuristic_func = get_heuristic(heuristic_name)
    
    # 1. Reset all nodes on the grid
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    for r in range(rows):
        for c in range(cols):
            grid[r][c].reset()
            
    # 2. Initialize start node
    start_node.g = 0.0
    start_node.h = heuristic_func(start_node, end_node)
    start_node.f = start_node.h
    
    # Open set is a priority queue. Stores tuples: (f_score, node_id_or_node)
    # Since we defined __lt__ on Node, heapq works directly on Node objects.
    # To handle potential heap identity issues we can push: (node.f, node)
    open_heap = []
    heapq.heappush(open_heap, (start_node.f, start_node))
    start_node.is_open = True
    
    yield ("open", start_node)
    
    while open_heap:
        _, current = heapq.heappop(open_heap)
        
        # If node was already processed or removed from open set representation
        if not current.is_open:
            continue
            
        current.is_open = False
        current.is_visited = True
        
        yield ("close", current)
        
        if current == end_node:
            path = reconstruct_path(end_node)
            yield ("success", path)
            return
            
        # Get valid orthogonal neighbors (up, down, left, right)
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = current.row + dr, current.col + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                neighbor = grid[nr][nc]
                if not neighbor.is_wall:
                    neighbors.append(neighbor)
                    
        for neighbor in neighbors:
            if neighbor.is_visited:
                continue
                
            # Cost distance from current node to neighbor is 1.0
            tentative_g = current.g + 1.0
            
            if tentative_g < neighbor.g:
                neighbor.parent = current
                neighbor.g = tentative_g
                neighbor.h = heuristic_func(neighbor, end_node)
                neighbor.f = neighbor.g + neighbor.h
                
                if not neighbor.is_open:
                    neighbor.is_open = True
                    heapq.heappush(open_heap, (neighbor.f, neighbor))
                    yield ("open", neighbor)
                else:
                    # Heap needs to re-sort since value changed.
                    # In python heapq, we can just push it again; since node.g/f is smaller,
                    # the smaller node value will be popped first and duplicate items are ignored 
                    # due to checking is_open or visited flags when popped.
                    heapq.heappush(open_heap, (neighbor.f, neighbor))
                    
    yield ("failure", None)

def dijkstra_search(grid, start_node, end_node):
    """
    Executes Dijkstra's pathfinding algorithm.
    Yields step summaries for animated visualization.
    """
    # 1. Reset all nodes on the grid
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    for r in range(rows):
        for c in range(cols):
            grid[r][c].reset()
            
    # 2. Initialize start node
    start_node.g = 0.0
    
    # Priority queue: (g_score, node)
    open_heap = []
    heapq.heappush(open_heap, (start_node.g, start_node))
    start_node.is_open = True
    
    yield ("open", start_node)
    
    while open_heap:
        _, current = heapq.heappop(open_heap)
        
        # If node was already processed
        if not current.is_open:
            continue
            
        current.is_open = False
        current.is_visited = True
        
        yield ("close", current)
        
        if current == end_node:
            path = reconstruct_path(end_node)
            yield ("success", path)
            return
            
        # Get valid orthogonal neighbors (up, down, left, right)
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = current.row + dr, current.col + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                neighbor = grid[nr][nc]
                if not neighbor.is_wall:
                    neighbors.append(neighbor)
                    
        for neighbor in neighbors:
            if neighbor.is_visited:
                continue
                
            # Cost distance from current node to neighbor is 1.0
            tentative_g = current.g + 1.0
            
            if tentative_g < neighbor.g:
                neighbor.parent = current
                neighbor.g = tentative_g
                
                if not neighbor.is_open:
                    neighbor.is_open = True
                    heapq.heappush(open_heap, (neighbor.g, neighbor))
                    yield ("open", neighbor)
                else:
                    heapq.heappush(open_heap, (neighbor.g, neighbor))
                    
    yield ("failure", None)

def bfs_search(grid, start_node, end_node):
    """
    Executes Breadth-First Search (BFS) pathfinding algorithm.
    Yields step summaries for animated visualization.
    """
    # 1. Reset all nodes on the grid
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    for r in range(rows):
        for c in range(cols):
            grid[r][c].reset()
            
    # FIFO queue
    queue = deque([start_node])
    start_node.is_open = True
    
    yield ("open", start_node)
    
    while queue:
        current = queue.popleft()
        
        current.is_open = False
        current.is_visited = True
        
        yield ("close", current)
        
        if current == end_node:
            path = reconstruct_path(end_node)
            yield ("success", path)
            return
            
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = current.row + dr, current.col + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                neighbor = grid[nr][nc]
                if not neighbor.is_wall and not neighbor.is_visited and not neighbor.is_open:
                    neighbor.parent = current
                    neighbor.is_open = True
                    queue.append(neighbor)
                    yield ("open", neighbor)
                    
    yield ("failure", None)

def dfs_search(grid, start_node, end_node):
    """
    Executes Depth-First Search (DFS) pathfinding algorithm.
    Yields step summaries for animated visualization.
    """
    # 1. Reset all nodes on the grid
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    for r in range(rows):
        for c in range(cols):
            grid[r][c].reset()
            
    # LIFO stack containing (node, parent)
    stack = [(start_node, None)]
    
    while stack:
        current, parent = stack.pop()
        
        if current.is_visited:
            continue
            
        current.parent = parent
        current.is_visited = True
        
        yield ("close", current)
        
        if current == end_node:
            path = reconstruct_path(end_node)
            yield ("success", path)
            return
            
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        # Reverse directions to explore in standard order (up, down, left, right)
        for dr, dc in reversed(directions):
            nr, nc = current.row + dr, current.col + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                neighbor = grid[nr][nc]
                if not neighbor.is_wall and not neighbor.is_visited:
                    neighbor.is_open = True
                    stack.append((neighbor, current))
                    yield ("open", neighbor)
                    
    yield ("failure", None)

