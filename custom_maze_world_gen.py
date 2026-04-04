import random

# --- CONFIGURATION ---
WIDTH = 15          # Number of cells wide (X)
HEIGHT = 15         # Number of cells high (Y)
CELL_SIZE = 1.2     # Size of each cell in meters (Turtlebot3 is ~0.2m wide)
WALL_THICKNESS = 0.15
WALL_HEIGHT = 1.0
ISLAND_FACTOR = 0.15  # 15% chance to remove a wall to create islands/variable spacing

class MazeGenerator:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        # True means wall exists. Setup grid of walls.
        self.h_walls = [[True for _ in range(w)] for _ in range(h + 1)]
        self.v_walls = [[True for _ in range(w + 1)] for _ in range(h)]
        self.visited = [[False for _ in range(w)] for _ in range(h)]

    def generate(self):
        # 1. Depth-First Search for a "Perfect" Maze
        def carve_passages(cx, cy):
            self.visited[cy][cx] = True
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(directions)

            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.w and 0 <= ny < self.h and not self.visited[ny][nx]:
                    # Knock down the wall between current and next
                    if dx == 1: self.v_walls[cy][cx + 1] = False
                    elif dx == -1: self.v_walls[cy][cx] = False
                    elif dy == 1: self.h_walls[cy + 1][cx] = False
                    elif dy == -1: self.h_walls[cy][cx] = False
                    carve_passages(nx, ny)

        # Start carving from the center (where robot spawns)
        start_x, start_y = self.w // 2, self.h // 2
        carve_passages(start_x, start_y)

        # 2. Knock down extra walls to create ISLANDS and VARIABLE SPACING
        for y in range(self.h):
            for x in range(self.w):
                if x > 0 and random.random() < ISLAND_FACTOR:
                    self.v_walls[y][x] = False
                if y > 0 and random.random() < ISLAND_FACTOR:
                    self.h_walls[y][x] = False

        # 3. Ensure the outer bounding box is solid, but make ONE exit (Finish)
        for x in range(self.w):
            self.h_walls[0][x] = True
            self.h_walls[self.h][x] = True
        for y in range(self.h):
            self.v_walls[y][0] = True
            self.v_walls[y][self.w] = True
            
        # Clear a 2x2 area in the center for the robot to spawn cleanly
        self.v_walls[start_y][start_x] = False
        self.v_walls[start_y][start_x+1] = False
        self.h_walls[start_y][start_x] = False
        self.h_walls[start_y+1][start_x] = False

        # Create the Finish Line (Exit gap at the top middle)
        self.h_walls[self.h][self.w // 2] = False

    def to_sdf(self):
        # We put everything in ONE link for massive Gazebo performance gains
        sdf = "<link name='maze_link'>\n"
        
        # Offsets to center the maze exactly at (0,0) in Gazebo
        offset_x = (self.w * CELL_SIZE) / 2.0
        offset_y = (self.h * CELL_SIZE) / 2.0
        
        wall_id = 0
        mat = "<material><ambient>0.6 0.6 0.6 1</ambient></material>"

        # Generate Horizontal Walls
        for y in range(self.h + 1):
            for x in range(self.w):
                if self.h_walls[y][x]:
                    px = (x * CELL_SIZE) + (CELL_SIZE / 2.0) - offset_x
                    py = (y * CELL_SIZE) - offset_y
                    sdf += f"""
        <collision name='c_{wall_id}'><pose>{px} {py} {WALL_HEIGHT/2} 0 0 0</pose><geometry><box><size>{CELL_SIZE+WALL_THICKNESS} {WALL_THICKNESS} {WALL_HEIGHT}</size></box></geometry></collision>
        <visual name='v_{wall_id}'><pose>{px} {py} {WALL_HEIGHT/2} 0 0 0</pose><geometry><box><size>{CELL_SIZE+WALL_THICKNESS} {WALL_THICKNESS} {WALL_HEIGHT}</size></box></geometry>{mat}</visual>"""
                    wall_id += 1

        # Generate Vertical Walls
        for y in range(self.h):
            for x in range(self.w + 1):
                if self.v_walls[y][x]:
                    px = (x * CELL_SIZE) - offset_x
                    py = (y * CELL_SIZE) + (CELL_SIZE / 2.0) - offset_y
                    sdf += f"""
        <collision name='c_{wall_id}'><pose>{px} {py} {WALL_HEIGHT/2} 0 0 0</pose><geometry><box><size>{WALL_THICKNESS} {CELL_SIZE+WALL_THICKNESS} {WALL_HEIGHT}</size></box></geometry></collision>
        <visual name='v_{wall_id}'><pose>{px} {py} {WALL_HEIGHT/2} 0 0 0</pose><geometry><box><size>{WALL_THICKNESS} {CELL_SIZE+WALL_THICKNESS} {WALL_HEIGHT}</size></box></geometry>{mat}</visual>"""
                    wall_id += 1

        sdf += "\n      </link>"
        return sdf

maze = MazeGenerator(WIDTH, HEIGHT)
maze.generate()

sdf_content = f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="optimized_maze_world">
    <include><uri>model://sun</uri></include>
    <include><uri>model://ground_plane</uri></include>
    <model name="pledge_maze">
      <static>true</static>
      {maze.to_sdf()}
    </model>
  </world>
</sdf>
"""

with open("maze_3.world", "w") as f:
    f.write(sdf_content)

print("Maze generated successfully as maze_3.world")