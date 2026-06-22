import tkinter as tk
from tkinter import ttk, messagebox
import time
from astar import Node, astar_search, dijkstra_search, bfs_search, dfs_search
from maze import generate_random_walls, generate_recursive_division

# Visual Theme Colors
BG_MAIN = "#0F172A"       # Slate 900
BG_SIDEBAR = "#1E293B"    # Slate 800
COLOR_TEXT = "#F8FAFC"    # Slate 50
COLOR_MUTED = "#94A3B8"   # Slate 400
COLOR_GRID_LINE = "#334155" # Slate 700

# Cell Colors
COLOR_EMPTY = "#1E293B"
COLOR_WALL = "#020617"
COLOR_START = "#10B981"   # Emerald
COLOR_END = "#EF4444"     # Rose
COLOR_OPEN = "#06B6D4"    # Cyan
COLOR_CLOSED = "#6366F1"  # Indigo
COLOR_PATH = "#F59E0B"    # Amber

class MazeSolverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("A* Maze Pathfinding Visualizer")
        self.root.geometry("960x680")
        self.root.configure(bg=BG_MAIN)
        self.root.resizable(False, False)
        
        # State variables
        self.grid_size = 29  # Default odd size for maze generators
        self.grid = []
        self.start_node = None
        self.end_node = None
        self.rectangles = []  # 2D list of canvas rectangle IDs
        self.text_ids = {}    # Maps (row, col) to canvas text IDs for start/end labels
        
        # Animation & search controls
        self.running = False
        self.paused = False
        self.search_generator = None
        self.search_start_time = 0
        self.nodes_visited_count = 0
        self.path_length = 0
        self.execution_time_ms = 0.0
        
        # Mouse Interaction variables
        self.drag_mode = None  # "START", "END", "WALL", "ERASE"
        
        # Build UI layout
        self.setup_styles()
        self.create_sidebar()
        self.create_canvas()
        
        # Initialize Grid
        self.initialize_grid(self.grid_size)
        
    def setup_styles(self):
        """Set up Tkinter styling for ttk widgets."""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure comboboxes
        self.style.configure("TCombobox", 
                             fieldbackground=BG_SIDEBAR, 
                             background=COLOR_GRID_LINE, 
                             foreground=COLOR_TEXT,
                             arrowcolor=COLOR_TEXT,
                             bordercolor=COLOR_GRID_LINE,
                             lightcolor=COLOR_GRID_LINE,
                             darkcolor=COLOR_GRID_LINE)
        self.style.map("TCombobox", 
                       fieldbackground=[("readonly", BG_SIDEBAR)],
                       foreground=[("readonly", COLOR_TEXT)])
        
    def create_sidebar(self):
        """Creates the settings and telemetry sidebar panel."""
        sidebar = tk.Frame(self.root, bg=BG_SIDEBAR, width=280, padx=15, pady=15)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Title
        title_lbl = tk.Label(sidebar, text="A* PATHFINDER", bg=BG_SIDEBAR, fg=COLOR_TEXT, 
                             font=("Segoe UI", 16, "bold"))
        title_lbl.pack(anchor=tk.W, pady=(0, 15))
        
        # --- Config Section ---
        config_frame = tk.LabelFrame(sidebar, text="Configuration", bg=BG_SIDEBAR, fg=COLOR_MUTED,
                                     font=("Segoe UI", 9, "bold"), bd=1, relief="solid", padx=8, pady=8)
        config_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Grid Size
        tk.Label(config_frame, text="Grid Size:", bg=BG_SIDEBAR, fg=COLOR_MUTED, font=("Segoe UI", 9)).pack(anchor=tk.W)
        self.grid_size_var = tk.StringVar(value="29 x 29")
        size_combo = ttk.Combobox(config_frame, textvariable=self.grid_size_var, 
                                  values=["15 x 15", "21 x 21", "29 x 29", "39 x 39"], state="readonly")
        size_combo.pack(fill=tk.X, pady=(2, 8))
        size_combo.bind("<<ComboboxSelected>>", self.on_grid_size_change)
        
        # Algorithm
        tk.Label(config_frame, text="Algorithm:", bg=BG_SIDEBAR, fg=COLOR_MUTED, font=("Segoe UI", 9)).pack(anchor=tk.W)
        self.algorithm_var = tk.StringVar(value="A* Search")
        self.algorithm_combo = ttk.Combobox(config_frame, textvariable=self.algorithm_var, 
                                            values=["A* Search", "Dijkstra's Algorithm", "BFS (Breadth-First)", "DFS (Depth-First)"], state="readonly")
        self.algorithm_combo.pack(fill=tk.X, pady=(2, 8))
        self.algorithm_combo.bind("<<ComboboxSelected>>", self.on_algorithm_change)
        
        # Heuristic
        tk.Label(config_frame, text="Heuristic:", bg=BG_SIDEBAR, fg=COLOR_MUTED, font=("Segoe UI", 9)).pack(anchor=tk.W)
        self.heuristic_var = tk.StringVar(value="Manhattan")
        self.heuristic_combo = ttk.Combobox(config_frame, textvariable=self.heuristic_var, 
                                            values=["Manhattan", "Euclidean", "Chebyshev"], state="readonly")
        self.heuristic_combo.pack(fill=tk.X, pady=(2, 8))
        
        # Speed
        tk.Label(config_frame, text="Speed:", bg=BG_SIDEBAR, fg=COLOR_MUTED, font=("Segoe UI", 9)).pack(anchor=tk.W)
        self.speed_var = tk.StringVar(value="Fast")
        speed_combo = ttk.Combobox(config_frame, textvariable=self.speed_var, 
                                   values=["Slow", "Medium", "Fast", "Instant"], state="readonly")
        speed_combo.pack(fill=tk.X, pady=(2, 5))

        
        # --- Controls Section ---
        controls_frame = tk.LabelFrame(sidebar, text="Solver Controls", bg=BG_SIDEBAR, fg=COLOR_MUTED,
                                       font=("Segoe UI", 9, "bold"), bd=1, relief="solid", padx=8, pady=8)
        controls_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Start Button
        self.start_btn = tk.Button(controls_frame, text="Visualize A* Search", command=self.toggle_start,
                                   bg=COLOR_START, fg="#ffffff", activebackground="#059669", activeforeground="#ffffff",
                                   font=("Segoe UI", 10, "bold"), relief="flat", bd=0, pady=6, cursor="hand2")
        self.start_btn.pack(fill=tk.X, pady=(0, 6))
        
        # Reset Path Button
        self.clear_path_btn = tk.Button(controls_frame, text="Clear Visuals", command=self.clear_visuals,
                                        bg="#475569", fg=COLOR_TEXT, activebackground="#334155", activeforeground=COLOR_TEXT,
                                        font=("Segoe UI", 9, "bold"), relief="flat", bd=0, pady=4, cursor="hand2")
        self.clear_path_btn.pack(fill=tk.X, pady=(0, 6))
        
        # Clear Grid Button
        self.clear_grid_btn = tk.Button(controls_frame, text="Clear All (Grid)", command=self.clear_all_grid,
                                        bg="#64748B", fg=COLOR_TEXT, activebackground="#475569", activeforeground=COLOR_TEXT,
                                        font=("Segoe UI", 9, "bold"), relief="flat", bd=0, pady=4, cursor="hand2")
        self.clear_grid_btn.pack(fill=tk.X, pady=(0, 6))
        
        # --- Maze Generators ---
        maze_frame = tk.LabelFrame(sidebar, text="Maze Generation", bg=BG_SIDEBAR, fg=COLOR_MUTED,
                                   font=("Segoe UI", 9, "bold"), bd=1, relief="solid", padx=8, pady=8)
        maze_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.maze_var = tk.StringVar(value="Recursive Division")
        maze_combo = ttk.Combobox(maze_frame, textvariable=self.maze_var, 
                                  values=["Recursive Division", "Random Density (30%)"], state="readonly")
        maze_combo.pack(fill=tk.X, pady=(2, 6))
        
        maze_gen_btn = tk.Button(maze_frame, text="Generate Maze", command=self.trigger_maze_generation,
                                 bg="#7C3AED", fg="#ffffff", activebackground="#6D28D9", activeforeground="#ffffff",
                                 font=("Segoe UI", 9, "bold"), relief="flat", bd=0, pady=4, cursor="hand2")
        maze_gen_btn.pack(fill=tk.X)
        
        # --- Telemetry Dashboard ---
        stats_frame = tk.LabelFrame(sidebar, text="Live Telemetry", bg=BG_SIDEBAR, fg=COLOR_MUTED,
                                    font=("Segoe UI", 9, "bold"), bd=1, relief="solid", padx=8, pady=8)
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_lbl = tk.Label(stats_frame, text="STATUS: IDLE", bg=BG_SIDEBAR, fg=COLOR_TEXT, 
                                   font=("Segoe UI", 10, "bold"), anchor=tk.W)
        self.status_lbl.pack(fill=tk.X, pady=2)
        
        self.visited_lbl = tk.Label(stats_frame, text="Explored Nodes: 0", bg=BG_SIDEBAR, fg=COLOR_MUTED, 
                                    font=("Segoe UI", 9), anchor=tk.W)
        self.visited_lbl.pack(fill=tk.X, pady=1)
        
        self.length_lbl = tk.Label(stats_frame, text="Path Cost: N/A", bg=BG_SIDEBAR, fg=COLOR_MUTED, 
                                   font=("Segoe UI", 9), anchor=tk.W)
        self.length_lbl.pack(fill=tk.X, pady=1)
        
        self.time_lbl = tk.Label(stats_frame, text="Time Elapsed: 0.0 ms", bg=BG_SIDEBAR, fg=COLOR_MUTED, 
                                 font=("Segoe UI", 9), anchor=tk.W)
        self.time_lbl.pack(fill=tk.X, pady=1)

    def create_canvas(self):
        """Creates the main visual grid drawing canvas area."""
        self.canvas_size = 600
        self.canvas_frame = tk.Frame(self.root, bg=BG_MAIN, padx=20, pady=20)
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, width=self.canvas_size, height=self.canvas_size,
                                bg=BG_MAIN, bd=0, highlightthickness=0)
        self.canvas.pack(expand=True)
        
        # Mouse event binds
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
    def initialize_grid(self, size):
        """Clears the visual canvas and creates a new grid structure of `size` x `size`."""
        self.grid_size = size
        self.grid = []
        self.rectangles = []
        self.text_ids = {}
        self.canvas.delete("all")
        
        cell_pixel_size = self.canvas_size / size
        
        # Build node grid objects and draw empty cells
        for r in range(size):
            grid_row = []
            rect_row = []
            for c in range(size):
                node = Node(r, c)
                grid_row.append(node)
                
                # Coordinate boundaries for drawing
                x1, y1 = c * cell_pixel_size, r * cell_pixel_size
                x2, y2 = (c + 1) * cell_pixel_size, (r + 1) * cell_pixel_size
                
                rect_id = self.canvas.create_rectangle(
                    x1, y1, x2, y2, 
                    fill=COLOR_EMPTY, 
                    outline=COLOR_GRID_LINE, 
                    width=1
                )
                rect_row.append(rect_id)
                
            self.grid.append(grid_row)
            self.rectangles.append(rect_row)
            
        # Place Default Start and End node coordinates
        self.start_node = self.grid[size // 2][size // 4]
        self.start_node.is_start = True
        self.end_node = self.grid[size // 2][(size * 3) // 4]
        self.end_node.is_end = True
        
        # Draw start/end nodes
        self.update_node_color(self.start_node)
        self.update_node_color(self.end_node)
        
        # Reset telemetry values
        self.reset_telemetry()
        
    def reset_telemetry(self):
        """Resets variables in the sidebar's statistics view."""
        self.nodes_visited_count = 0
        self.path_length = 0
        self.execution_time_ms = 0.0
        self.visited_lbl.config(text="Explored Nodes: 0")
        self.length_lbl.config(text="Path Cost: N/A")
        self.time_lbl.config(text="Time Elapsed: 0.0 ms")
        self.status_lbl.config(text="STATUS: IDLE", fg=COLOR_TEXT)
        
    def update_node_color(self, node):
        """Updates the fill color and text label of a cell rectangle dynamically on the Canvas."""
        r, c = node.row, node.col
        rect_id = self.rectangles[r][c]
        
        # Determine cell color based on state priority
        if node.is_start:
            color = COLOR_START
        elif node.is_end:
            color = COLOR_END
        elif node.is_wall:
            color = COLOR_WALL
        elif node.parent is not None and not node.is_open and not node.is_visited:
            # Reconstructing/Final path node
            color = COLOR_PATH
        elif node.is_visited:
            color = COLOR_CLOSED
        elif node.is_open:
            color = COLOR_OPEN
        else:
            color = COLOR_EMPTY
            
        self.canvas.itemconfig(rect_id, fill=color)
        
        # Start and End Labels
        label_key = (r, c)
        if node.is_start or node.is_end:
            cell_size = self.canvas_size / self.grid_size
            center_x = (c + 0.5) * cell_size
            center_y = (r + 0.5) * cell_size
            label_text = "S" if node.is_start else "E"
            
            if label_key in self.text_ids:
                # Update label text / color
                self.canvas.itemconfig(self.text_ids[label_key], text=label_text)
            else:
                text_id = self.canvas.create_text(
                    center_x, center_y, 
                    text=label_text, 
                    fill="#ffffff", 
                    font=("Segoe UI", int(cell_size * 0.4), "bold")
                )
                self.text_ids[label_key] = text_id
        else:
            # If a label exists but cell is no longer start/end, remove label text
            if label_key in self.text_ids:
                self.canvas.delete(self.text_ids[label_key])
                del self.text_ids[label_key]

    def on_grid_size_change(self, event=None):
        """Callback when the grid size selection in the combobox is adjusted."""
        if self.running:
            messagebox.showwarning("Warning", "Cannot resize the grid while the visualizer is running.")
            # Reset selection to current grid size
            self.grid_size_var.set(f"{self.grid_size} x {self.grid_size}")
            return
            
        selected = self.grid_size_var.get()
        size = int(selected.split(" ")[0])
        self.initialize_grid(size)

    def on_algorithm_change(self, event=None):
        """Callback when the pathfinding algorithm in the combobox is adjusted."""
        algo = self.algorithm_var.get()
        if algo == "A* Search":
            self.heuristic_combo.config(state="readonly")
        else:
            self.heuristic_combo.config(state="disabled")
        
        # Update start button text if solver is not running
        if not self.running:
            self.start_btn.config(text=f"Visualize {algo}")


    # --- Mouse Event Handlers ---
    def get_cell_coords(self, event):
        """Converts window mouse screen coordinates into grid indices (row, col)."""
        cell_size = self.canvas_size / self.grid_size
        col = int(event.x // cell_size)
        row = int(event.y // cell_size)
        
        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            return row, col
        return None

    def on_canvas_click(self, event):
        """Fires when the left mouse button clicks down inside the Canvas grid."""
        if self.running:
            return
            
        coords = self.get_cell_coords(event)
        if not coords:
            return
            
        row, col = coords
        clicked_node = self.grid[row][col]
        
        if clicked_node.is_start:
            self.drag_mode = "START"
        elif clicked_node.is_end:
            self.drag_mode = "END"
        elif clicked_node.is_wall:
            self.drag_mode = "ERASE"
            clicked_node.is_wall = False
            self.update_node_color(clicked_node)
        else:
            self.drag_mode = "WALL"
            clicked_node.is_wall = True
            self.update_node_color(clicked_node)

    def on_canvas_drag(self, event):
        """Fires repeatedly as the left mouse is dragged inside the Canvas."""
        if self.running or not self.drag_mode:
            return
            
        coords = self.get_cell_coords(event)
        if not coords:
            return
            
        row, col = coords
        target_node = self.grid[row][col]
        
        # Implement dragging states
        if self.drag_mode == "START":
            if not target_node.is_end and not target_node.is_wall:
                # Remove S marker from old location
                old_start = self.start_node
                old_start.is_start = False
                self.update_node_color(old_start)
                
                # Move start node pointer
                self.start_node = target_node
                self.start_node.is_start = True
                self.update_node_color(self.start_node)
                
        elif self.drag_mode == "END":
            if not target_node.is_start and not target_node.is_wall:
                # Remove E marker from old location
                old_end = self.end_node
                old_end.is_end = False
                self.update_node_color(old_end)
                
                # Move end node pointer
                self.end_node = target_node
                self.end_node.is_end = True
                self.update_node_color(self.end_node)
                
        elif self.drag_mode == "WALL":
            if not target_node.is_start and not target_node.is_end:
                target_node.is_wall = True
                self.update_node_color(target_node)
                
        elif self.drag_mode == "ERASE":
            if not target_node.is_start and not target_node.is_end:
                target_node.is_wall = False
                self.update_node_color(target_node)

    def on_canvas_release(self, event):
        """Resets the drawing/drag mode when the left click is released."""
        self.drag_mode = None

    # --- Maze Generation ---
    def trigger_maze_generation(self):
        """Triggers the chosen maze generation routine."""
        if self.running:
            return
            
        maze_type = self.maze_var.get()
        
        # Reset visual state before generating walls
        self.clear_visuals(confirm=False)
        
        if maze_type == "Recursive Division":
            generate_recursive_division(self.grid, self.start_node, self.end_node)
        elif maze_type == "Random Density (30%)":
            generate_random_walls(self.grid, self.start_node, self.end_node, density=0.3)
            
        # Draw the updated wall nodes on the Canvas
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                self.update_node_color(self.grid[r][c])
                
        self.reset_telemetry()
        self.status_lbl.config(text="STATUS: MAZE GENERATED", fg=COLOR_OPEN)

    # --- Search Visualizer Loop ---
    def toggle_start(self):
        """Toggles between Visualizing the algorithm, pausing the search, or resuming it."""
        algo = self.algorithm_var.get()
        if self.running:
            if self.paused:
                # Resume search
                self.paused = False
                self.status_lbl.config(text="STATUS: SEARCHING...", fg=COLOR_OPEN)
                self.start_btn.config(text="Pause Solver", bg="#F59E0B")
                self.run_animation_step()
            else:
                # Pause search
                self.paused = True
                self.status_lbl.config(text="STATUS: PAUSED", fg="#F59E0B")
                self.start_btn.config(text=f"Resume {algo}", bg=COLOR_START)
        else:
            # Start a brand new solver search run
            self.start_solver()

    def start_solver(self):
        """Instantiates the generator-based pathfinding algorithm run loop."""
        # 1. Clear previous paths and analytics
        self.clear_visuals(confirm=False)
        
        # 2. Configure variables
        self.running = True
        self.paused = False
        self.start_btn.config(text="Pause Solver", bg="#F59E0B")
        self.status_lbl.config(text="STATUS: SEARCHING...", fg=COLOR_OPEN)
        
        algorithm = self.algorithm_var.get()
        if algorithm == "A* Search":
            heuristic = self.heuristic_var.get()
            self.search_generator = astar_search(self.grid, self.start_node, self.end_node, heuristic)
        elif algorithm == "Dijkstra's Algorithm":
            self.search_generator = dijkstra_search(self.grid, self.start_node, self.end_node)
        elif algorithm == "BFS (Breadth-First)":
            self.search_generator = bfs_search(self.grid, self.start_node, self.end_node)
        elif algorithm == "DFS (Depth-First)":
            self.search_generator = dfs_search(self.grid, self.start_node, self.end_node)
            
        self.search_start_time = time.perf_counter()
        
        # Check speed type
        speed = self.speed_var.get()
        if speed == "Instant":
            self.solve_instantly()
        else:
            self.run_animation_step()

    def solve_instantly(self):
        """Runs the search algorithm synchronously to completion without delayed rendering."""
        try:
            while True:
                step_type, data = next(self.search_generator)
                
                # Check outcome states to stop loop
                if step_type == "success":
                    self.search_complete(data, success=True)
                    break
                elif step_type == "failure":
                    self.search_complete(None, success=False)
                    break
                    
        except StopIteration:
            pass

    def run_animation_step(self):
        """Processes animation updates step-by-step asynchronously using Tkinter scheduler."""
        if not self.running or self.paused:
            return
            
        speed = self.speed_var.get()
        
        # Calibrate timing intervals and node evaluations per step based on selection
        # (Allows smoother adjustments and visual density)
        if speed == "Slow":
            delay_ms = 150
            steps_per_tick = 1
        elif speed == "Medium":
            delay_ms = 35
            steps_per_tick = 1
        else:  # "Fast"
            delay_ms = 10
            steps_per_tick = 3
            
        try:
            for _ in range(steps_per_tick):
                step_type, data = next(self.search_generator)
                
                if step_type == "open":
                    node = data
                    if node != self.start_node and node != self.end_node:
                        self.update_node_color(node)
                        
                elif step_type == "close":
                    node = data
                    self.nodes_visited_count += 1
                    if node != self.start_node and node != self.end_node:
                        self.update_node_color(node)
                        
                elif step_type == "success":
                    self.search_complete(data, success=True)
                    return
                    
                elif step_type == "failure":
                    self.search_complete(None, success=False)
                    return
                    
            # Track execution time
            self.execution_time_ms = (time.perf_counter() - self.search_start_time) * 1000
            self.visited_lbl.config(text=f"Explored Nodes: {self.nodes_visited_count}")
            self.time_lbl.config(text=f"Time Elapsed: {self.execution_time_ms:.1f} ms")
            
            # Schedule next frame update
            self.root.after(delay_ms, self.run_animation_step)
            
        except StopIteration:
            pass

    def search_complete(self, path, success=True):
        """Fires when search completes. Reconstructs path visuals and prints final statistics."""
        self.running = False
        self.paused = False
        self.search_generator = None
        algo = self.algorithm_var.get()
        self.start_btn.config(text=f"Visualize {algo}", bg=COLOR_START)
        
        # Calculate execution elapsed time
        self.execution_time_ms = (time.perf_counter() - self.search_start_time) * 1000
        self.time_lbl.config(text=f"Time Elapsed: {self.execution_time_ms:.1f} ms")
        
        if success and path:
            self.status_lbl.config(text="STATUS: PATH FOUND! ✔", fg=COLOR_START)
            self.path_length = len(path)
            self.length_lbl.config(text=f"Path Cost: {self.path_length - 1} steps")
            
            # Draw Path step-by-step
            for node in path:
                if node != self.start_node and node != self.end_node:
                    self.update_node_color(node)
                    
            # Recalculate exact total nodes evaluated
            visited_nodes = sum(1 for row in self.grid for node in row if node.is_visited)
            self.visited_lbl.config(text=f"Explored Nodes: {visited_nodes}")
            
        else:
            self.status_lbl.config(text="STATUS: UNREACHABLE! ❌", fg=COLOR_END)
            self.length_lbl.config(text="Path Cost: Infinite")
            
            visited_nodes = sum(1 for row in self.grid for node in row if node.is_visited)
            self.visited_lbl.config(text=f"Explored Nodes: {visited_nodes}")
            
            messagebox.showinfo("Search Result", "Destination is unreachable! The path is completely blocked.")

    # --- State Modification Button Clears ---
    def clear_visuals(self, confirm=True):
        """Clears explored routes, open sets, and paths from the grid, preserving walls."""
        if self.running and confirm:
            if not messagebox.askyesno("Confirm Clear", "Search is currently running. Stop and clear paths?"):
                return
                
        # Halt execution loop
        self.running = False
        self.paused = False
        self.search_generator = None
        algo = self.algorithm_var.get()
        self.start_btn.config(text=f"Visualize {algo}", bg=COLOR_START)
        
        # Reset nodes on grid (keep walls)
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                node = self.grid[r][c]
                node.reset()
                self.update_node_color(node)
                
        self.reset_telemetry()

    def clear_all_grid(self):
        """Resets the entire visual grid workspace, clearing all walls and path visualizers."""
        if self.running:
            if not messagebox.askyesno("Confirm Reset", "Search is currently running. Stop and reset entire grid?"):
                return
                
        # Reinitialize base grid structure
        self.initialize_grid(self.grid_size)

if __name__ == "__main__":
    root = tk.Tk()
    app = MazeSolverApp(root)
    root.mainloop()
