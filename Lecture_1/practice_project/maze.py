import sys


# Node class to represent each state in the maze.
class Node:
    def __init__(self, state, parent, action):
        """
        Initialize a Node.

        Parameters:
            state (tuple): The (row, column) coordinates in the maze.
            parent (Node): The node from which this node was reached.
            action (str): The move taken to get from the parent to this node.
        """
        self.state = state  # (row, col) coordinates
        self.parent = parent  # Parent node that generated this node
        self.action = action  # Action taken from the parent node


# Frontier class using a stack (LIFO) for Depth-First Search
class StackFrontier:
    def __init__(self):
        # Initialize an empty list to store frontier nodes
        self.frontier = []

    def add(self, node):
        """
        Add a node to the frontier.

        Parameters:
            node (Node): The node to be added.
        """
        self.frontier.append(node)  # Add node at the end (top of stack)

    def contains_state(self, state):
        """
        Check if the frontier contains a node with the given state.

        Parameters:
            state (tuple): The state to check.

        Returns:
            bool: True if a node with the state is in the frontier, else False.
        """
        return any(node.state == state for node in self.frontier)

    def empty(self):
        """
        Check if the frontier is empty.

        Returns:
            bool: True if frontier is empty, else False.
        """
        return len(self.frontier) == 0

    def remove(self):
        """
        Remove and return the last node added to the frontier (LIFO behavior).

        Returns:
            Node: The node removed from the frontier.

        Raises:
            Exception: If the frontier is empty.
        """
        if self.empty():  # Check if there are nodes left to explore
            raise Exception("empty frontier")
        else:
            # Remove and return the last node (LIFO)
            node = self.frontier.pop()
            return node


# Frontier class using a queue (FIFO) for Breadth-First Search, inherits from StackFrontier
class QueueFrontier(StackFrontier):
    def remove(self):
        """
        Remove and return the first node added to the frontier (FIFO behavior).

        Returns:
            Node: The node removed from the frontier.

        Raises:
            Exception: If the frontier is empty.
        """
        if self.empty():
            raise Exception("empty frontier")
        else:
            # Remove and return the first element in the list (FIFO)
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node


# Maze class to represent and solve the maze
class Maze:
    def __init__(self, filename):
        """
        Initialize the maze by reading from a file, setting up walls, and defining the start and goal positions.

        Parameters:
            filename (str): The file containing the maze layout.

        Attributes:
            height (int): Number of rows in the maze.
            width (int): Number of columns in the maze.
            walls (list[list[bool]]): 2D grid indicating walls (True) and open spaces (False).
            start (tuple): Coordinates for the starting point (marked as "A").
            goal (tuple): Coordinates for the goal point (marked as "B").
            solution (tuple or None): The solution as a tuple (actions, cells) if solved; otherwise None.

        Raises:
            Exception: If the maze does not contain exactly one start ("A") or one goal ("B").
        """
        # Read the entire file content
        with open(filename) as f:
            contents = f.read()

        # Validate that there is exactly one start point "A" and one goal point "B"
        if contents.count("A") != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")

        # Split the file content into lines to create the maze grid
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = len(contents[0])

        # Initialize walls and set start and goal positions
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)  # Not a wall
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)  # Not a wall
                    elif contents[i][j] == " ":
                        row.append(False)  # Open space
                    else:
                        row.append(True)  # Wall for any other character
                except IndexError:
                    # If we go out-of-bounds for a row, treat as open space
                    row.append(False)
            self.walls.append(row)

        # Initialize solution placeholder
        self.solution = None

    def print(self):
        """
        Print a visual representation of the maze to the console.

        Symbols used:
            '█' - Wall
            'A' - Start position
            'B' - Goal position
            '*' - Path in the solution (if exists)
            ' ' - Open space
        """
        # Get the solution path if available (skip the start cell)
        solution = self.solution[1] if self.solution is not None else None

        # Print a blank line for spacing
        print()

        # Loop through each row and cell of the maze grid
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")  # Print wall
                elif (i, j) == self.start:
                    print("A", end="")  # Print start
                elif (i, j) == self.goal:
                    print("B", end="")  # Print goal
                elif solution is not None and (i, j) in solution:
                    print("*", end="")  # Print cell in the solution path
                else:
                    print(" ", end="")  # Print open space
            print()  # Newline after each row

        # Print a blank line after the maze for spacing
        print()

    def neighbors(self, state):
        """
        Get valid neighboring cells (actions) for a given state.

        Parameters:
            state (tuple): The (row, col) coordinates of the current state.

        Returns:
            list: List of tuples, each containing an action string and the resulting state.
        """
        row, col = state
        # Define possible moves with their direction names and new coordinates
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
            ]

        result = []
        # Check each candidate move for validity (within bounds and not a wall)
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result

    def solve(self):
        """
        Solve the maze using Depth-First Search (DFS).

        This method tracks the number of states explored and builds a solution path if one exists.
        If no solution exists, an exception is raised.
        """
        # Initialize the counter for states explored
        self.num_explored = 0

        # Create the starting node and initialize the frontier with it
        start = Node(state=self.start, parent=None, action=None)
        frontier = StackFrontier()
        frontier.add(start)

        # Set to keep track of visited states
        self.explored = set()

        # Continue searching until the goal is found or frontier is empty
        while True:
            # If the frontier is empty, no solution exists
            if frontier.empty():
                raise Exception("no solution")

            # Remove a node from the frontier (DFS: last-in, first-out)
            node = frontier.remove()
            self.num_explored += 1

            # Check if the current node is the goal
            if node.state == self.goal:
                actions = []
                cells = []
                # Trace back the path from the goal to the start
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                # Reverse the path to get the correct order from start to goal
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            # Mark the current state as explored
            self.explored.add(node.state)

            # Iterate over valid neighbors and add new nodes to the frontier
            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)

    def output_image(self, filename, show_solution=True, show_explored=False):
        """
        Generate an image of the maze with options to display the solution and explored cells.

        Parameters:
            filename (str): The output file name for the generated image.
            show_solution (bool): If True, the solution path is highlighted.
            show_explored (bool): If True, the cells explored during the search are highlighted.
        """
        from PIL import Image, ImageDraw
        cell_size = 50  # Size of each maze cell in pixels
        cell_border = 2  # Border size within each cell

        # Create a blank image with a black background
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
            )
        draw = ImageDraw.Draw(img)

        # Get the solution path if one exists
        solution = self.solution[1] if self.solution is not None else None

        # Iterate over each cell in the maze grid
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                # Determine the fill color based on the cell type
                if col:  # Wall cell
                    fill = (40, 40, 40)
                elif (i, j) == self.start:  # Start cell
                    fill = (255, 0, 0)
                elif (i, j) == self.goal:  # Goal cell
                    fill = (0, 171, 28)
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)
                else:  # Open cell
                    fill = (237, 240, 252)

                # Draw the cell as a rectangle
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                    )

        # Save the generated image to the specified file
        img.save(filename)


# If this script is executed directly (not imported), then run the following:
if len(sys.argv) != 2:
    sys.exit("Usage: python maze.py maze.txt")

# Create a Maze instance with the maze file provided as a command line argument
m = Maze(sys.argv[1])
print("Maze:")
m.print()  # Print the initial maze

print("Solving...")
m.solve()  # Solve the maze

# Output the number of states explored during the search
print("States Explored:", m.num_explored)
print("Solution:")
m.print()  # Print the maze again, now with the solution path (if found)
m.output_image("maze.png", show_explored=True)  # Generate and save an image of the maze
