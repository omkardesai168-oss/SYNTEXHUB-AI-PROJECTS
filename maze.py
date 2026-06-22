import random

def generate_random_walls(grid, start_node, end_node, density=0.3):
    """Fills the grid with walls randomly based on density (0.0 to 1.0)."""
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    for r in range(rows):
        for c in range(cols):
            node = grid[r][c]
            node.is_wall = False
            node.reset()
            
            # Skip start and end nodes
            if node == start_node or node == end_node:
                continue
                
            if random.random() < density:
                node.is_wall = True

def generate_recursive_division(grid, start_node, end_node):
    """
    Generates a maze using the Recursive Division algorithm.
    This creates clean, solid wall corridors. Works best with odd grid dimensions.
    """
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    # 1. Clear all nodes
    for r in range(rows):
        for c in range(cols):
            grid[r][c].is_wall = False
            grid[r][c].reset()
            
    # 2. Draw border walls
    for r in range(rows):
        grid[r][0].is_wall = True
        grid[r][cols - 1].is_wall = True
    for c in range(cols):
        grid[0][c].is_wall = True
        grid[rows - 1][c].is_wall = True
        
    def choose_orientation(width, height):
        if width < height:
            return "horizontal"
        elif height < width:
            return "vertical"
        else:
            return "horizontal" if random.random() < 0.5 else "vertical"
            
    def divide(r_start, r_end, c_start, c_end, orientation):
        # We need a width and height of at least 2 cells to divide
        if r_end - r_start < 2 or c_end - c_start < 2:
            return
            
        horizontal = (orientation == "horizontal")
        
        # We want to build a wall. To align corridors properly on odd rows/cols:
        # We select even coordinates for walls, and odd coordinates for passages.
        if horizontal:
            # Find possible even rows to place the wall
            possible_rows = [r for r in range(r_start + 1, r_end) if r % 2 == 0]
            if not possible_rows:
                return
            wall_row = random.choice(possible_rows)
            
            # Find possible odd columns to place the passage (hole)
            possible_passages = [c for c in range(c_start, c_end + 1) if c % 2 != 0]
            if not possible_passages:
                passage_col = random.randint(c_start, c_end)
            else:
                passage_col = random.choice(possible_passages)
                
            # Place the horizontal wall
            for c in range(c_start, c_end + 1):
                if c != passage_col:
                    grid[wall_row][c].is_wall = True
                    
            # Recursively divide sub-chambers
            # Top sub-chamber
            h_height = (wall_row - 1) - r_start
            h_width = c_end - c_start
            divide(r_start, wall_row - 1, c_start, c_end, choose_orientation(h_width, h_height))
            
            # Bottom sub-chamber
            v_height = r_end - (wall_row + 1)
            v_width = c_end - c_start
            divide(wall_row + 1, r_end, c_start, c_end, choose_orientation(v_width, v_height))
            
        else:
            # Find possible even columns to place the wall
            possible_cols = [c for c in range(c_start + 1, c_end) if c % 2 == 0]
            if not possible_cols:
                return
            wall_col = random.choice(possible_cols)
            
            # Find possible odd rows to place the passage (hole)
            possible_passages = [r for r in range(r_start, r_end + 1) if r % 2 != 0]
            if not possible_passages:
                passage_row = random.randint(r_start, r_end)
            else:
                passage_row = random.choice(possible_passages)
                
            # Place the vertical wall
            for r in range(r_start, r_end + 1):
                if r != passage_row:
                    grid[r][wall_col].is_wall = True
                    
            # Recursively divide sub-chambers
            # Left sub-chamber
            l_height = r_end - r_start
            l_width = (wall_col - 1) - c_start
            divide(r_start, r_end, c_start, wall_col - 1, choose_orientation(l_width, l_height))
            
            # Right sub-chamber
            r_height = r_end - r_start
            r_width = c_end - (wall_col + 1)
            divide(r_start, r_end, wall_col + 1, c_end, choose_orientation(r_width, r_height))
            
    # Divide starting from inside the borders
    divide(1, rows - 2, 1, cols - 2, choose_orientation(cols - 2, rows - 2))
    
    # Ensure start and end nodes are NOT walls and reset
    start_node.is_wall = False
    start_node.reset()
    end_node.is_wall = False
    end_node.reset()
