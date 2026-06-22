import unittest
from astar import Node, astar_search, dijkstra_search, bfs_search, dfs_search, reconstruct_path

class TestAStarSearch(unittest.TestCase):
    def setUp(self):
        # Set up a small 5x5 grid for testing
        self.rows = 5
        self.cols = 5
        self.grid = [[Node(r, c) for c in range(self.cols)] for r in range(self.rows)]
        self.start = self.grid[0][0]
        self.start.is_start = True
        self.end = self.grid[4][4]
        self.end.is_end = True

    def test_clear_grid_path(self):
        """Test A* on a completely clear grid. Shortest path cost should be 8 steps."""
        generator = astar_search(self.grid, self.start, self.end, "Manhattan")
        path = None
        
        # Consume generator
        for step_type, data in generator:
            if step_type == "success":
                path = data
                
        self.assertIsNotNone(path)
        # Cost is number of nodes in path - 1 (reconstructed path includes start and end)
        self.assertEqual(len(path) - 1, 8)
        self.assertEqual(path[0], self.start)
        self.assertEqual(path[-1], self.end)

    def test_simple_wall_obstacle(self):
        """
        Test A* navigating around a simple wall obstacle:
        S . . . .
        # # # # .
        . . . . .
        . . . . .
        . . . . G
        """
        # Place a horizontal wall block on row 1
        for c in range(4):
            self.grid[1][c].is_wall = True
            
        generator = astar_search(self.grid, self.start, self.end, "Manhattan")
        path = None
        for step_type, data in generator:
            if step_type == "success":
                path = data
                
        self.assertIsNotNone(path)
        # S -> (0,4) -> (4,4) is the path. 
        # Path details: (0,0)->(0,1)->(0,2)->(0,3)->(0,4)->(1,4)->(2,4)->(3,4)->(4,4)
        # Total steps: 8
        self.assertEqual(len(path) - 1, 8)
        # None of the nodes in path should be walls
        for node in path:
            self.assertFalse(node.is_wall)

    def test_unreachable_target(self):
        """
        Test that A* correctly reports failure when the goal is completely blocked.
        S | G (blocked by walls)
        """
        # Block the end node completely (row 4, col 4)
        self.grid[3][4].is_wall = True
        self.grid[4][3].is_wall = True
        
        generator = astar_search(self.grid, self.start, self.end, "Manhattan")
        path_found = False
        failed = False
        
        for step_type, data in generator:
            if step_type == "success":
                path_found = True
            elif step_type == "failure":
                failed = True
                
        self.assertFalse(path_found)
        self.assertTrue(failed)

    def test_different_heuristics(self):
        """Verify that Manhattan and Euclidean distance heuristics find valid paths."""
        for heuristic in ["Manhattan", "Euclidean", "Chebyshev"]:
            # Recreate grid
            grid = [[Node(r, c) for c in range(self.cols)] for r in range(self.rows)]
            start = grid[0][0]
            start.is_start = True
            end = grid[4][4]
            end.is_end = True
            
            # Place obstacle
            grid[2][1].is_wall = True
            grid[2][2].is_wall = True
            grid[2][3].is_wall = True
            
            generator = astar_search(grid, start, end, heuristic)
            path = None
            for step_type, data in generator:
                if step_type == "success":
                    path = data
            
            self.assertIsNotNone(path, f"Path should be found using {heuristic}")
            self.assertEqual(path[0], start)
            self.assertEqual(path[-1], end)

    def test_dijkstra_clear_grid(self):
        """Test Dijkstra on a completely clear grid. Shortest path cost should be 8 steps."""
        generator = dijkstra_search(self.grid, self.start, self.end)
        path = None
        for step_type, data in generator:
            if step_type == "success":
                path = data
        self.assertIsNotNone(path)
        self.assertEqual(len(path) - 1, 8)

    def test_dijkstra_obstacle(self):
        """Test Dijkstra navigating around a simple wall obstacle."""
        for c in range(4):
            self.grid[1][c].is_wall = True
        generator = dijkstra_search(self.grid, self.start, self.end)
        path = None
        for step_type, data in generator:
            if step_type == "success":
                path = data
        self.assertIsNotNone(path)
        self.assertEqual(len(path) - 1, 8)
        for node in path:
            self.assertFalse(node.is_wall)

    def test_dijkstra_unreachable(self):
        """Test Dijkstra handles unreachable target correctly."""
        self.grid[3][4].is_wall = True
        self.grid[4][3].is_wall = True
        generator = dijkstra_search(self.grid, self.start, self.end)
        path_found = False
        failed = False
        for step_type, data in generator:
            if step_type == "success":
                path_found = True
            elif step_type == "failure":
                failed = True
        self.assertFalse(path_found)
        self.assertTrue(failed)

    def test_bfs_clear_grid(self):
        """Test BFS on a completely clear grid. Shortest path cost should be 8 steps."""
        generator = bfs_search(self.grid, self.start, self.end)
        path = None
        for step_type, data in generator:
            if step_type == "success":
                path = data
        self.assertIsNotNone(path)
        self.assertEqual(len(path) - 1, 8)

    def test_bfs_obstacle(self):
        """Test BFS navigating around a simple wall obstacle."""
        for c in range(4):
            self.grid[1][c].is_wall = True
        generator = bfs_search(self.grid, self.start, self.end)
        path = None
        for step_type, data in generator:
            if step_type == "success":
                path = data
        self.assertIsNotNone(path)
        self.assertEqual(len(path) - 1, 8)
        for node in path:
            self.assertFalse(node.is_wall)

    def test_bfs_unreachable(self):
        """Test BFS handles unreachable target correctly."""
        self.grid[3][4].is_wall = True
        self.grid[4][3].is_wall = True
        generator = bfs_search(self.grid, self.start, self.end)
        path_found = False
        failed = False
        for step_type, data in generator:
            if step_type == "success":
                path_found = True
            elif step_type == "failure":
                failed = True
        self.assertFalse(path_found)
        self.assertTrue(failed)

    def test_dfs_clear_grid(self):
        """Test DFS on a completely clear grid. DFS might not find the absolute shortest path but must find a path."""
        generator = dfs_search(self.grid, self.start, self.end)
        path = None
        for step_type, data in generator:
            if step_type == "success":
                path = data
        self.assertIsNotNone(path)
        self.assertEqual(path[0], self.start)
        self.assertEqual(path[-1], self.end)

    def test_dfs_unreachable(self):
        """Test DFS handles unreachable target correctly."""
        self.grid[3][4].is_wall = True
        self.grid[4][3].is_wall = True
        generator = dfs_search(self.grid, self.start, self.end)
        path_found = False
        failed = False
        for step_type, data in generator:
            if step_type == "success":
                path_found = True
            elif step_type == "failure":
                failed = True
        self.assertFalse(path_found)
        self.assertTrue(failed)

if __name__ == "__main__":
    unittest.main()

