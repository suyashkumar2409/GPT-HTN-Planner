import heapq

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.g_cost = float('inf')  # Cost from start node
        self.h_cost = 0             # Heuristic cost (estimated cost to goal)
        self.parent = None

    def __lt__(self, other):
        # Comparison method for the priority queue
        return (self.g_cost + self.h_cost) < (other.g_cost + other.h_cost)

def euclidean_distance(node1, node2):
    # Euclidean distance heuristic between two nodes
    return ((node1.x - node2.x) ** 2 + (node1.y - node2.y) ** 2) ** 0.5

def a_star_search(start, goal, grid):
    open_set = []  # Priority queue for nodes to be evaluated
    closed_set = set()  # Set of nodes already evaluated

    start.g_cost = 0
    start.h_cost = euclidean_distance(start, goal)
    heapq.heappush(open_set, start)

    while open_set:
        current_node = heapq.heappop(open_set)

        if current_node == goal:
            # Reconstruct the path from goal to start
            path = []
            while current_node:
                path.append((current_node.x, current_node.y))
                current_node = current_node.parent
            return path[::-1]  # Reverse the path to start -> goal

        closed_set.add(current_node)

        # Generate neighbor nodes
        neighbors = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_x, new_y = current_node.x + dx, current_node.y + dy
            if 0 <= new_x < len(grid) and 0 <= new_y < len(grid[0]) and grid[new_x][new_y] == 0:
                neighbors.append(Node(new_x, new_y))

        for neighbor in neighbors:
            if neighbor in closed_set:
                continue

            tentative_g_cost = current_node.g_cost + euclidean_distance(current_node, neighbor)

            if tentative_g_cost < neighbor.g_cost or neighbor not in open_set:
                neighbor.parent = current_node
                neighbor.g_cost = tentative_g_cost
                neighbor.h_cost = euclidean_distance(neighbor, goal)
                if neighbor not in open_set:
                    heapq.heappush(open_set, neighbor)

    return None  # No path found

# Example grid (0 represents a free space, 1 represents an obstacle)
grid = [
    [0, 0, 0, 0, 0],
    [0, 1, 0, 1, 0],
    [0, 0, 0, 0, 0],
    [0, 1, 0, 1, 0],
    [0, 0, 0, 0, 0]
]

start_node = Node(0, 0)
goal_node = Node(4, 4)

path = a_star_search(start_node, goal_node, grid)

if path:
    print("Path found:")
    for x, y in path:
        print(f"({x}, {y})")
else:
    print("No path found")
