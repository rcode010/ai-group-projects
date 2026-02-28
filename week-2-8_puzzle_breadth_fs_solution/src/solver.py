"""
BFS algorithm for solving 8-puzzle
"""
# Goal

from collections import deque

solved = (1, 2, 3, 4, 5, 6, 7, 8, 0)
initial_state = (1,2,3,
                 4,0,6,
                 7,5,8)


class Node:
    def __init__(self, state: tuple, parent: "Node" = None, move: str = None, cost: int = 0):
        self.state = state  # Current puzzle state
        self.parent = parent  # Previous state
        self.move = move  # Move that got here ("UP", "DOWN", etc.)
        self.cost = cost  # Depth / path cost


def bfs_solve(initial_state):
    if is_goal(initial_state):
        return []

    queue = deque()
    visited = set()

    # Create starting node
    start_node = Node(state=initial_state, parent=None, move=None, cost=0)

    queue.append(start_node)
    visited.add(initial_state)

    while queue:
        current_node = queue.popleft()
        target, neighbor_indices = get_neighbors(list(current_node.state))

        # 3. For each neighbor
        for neighbor_index in neighbor_indices:
            # Create new state
            new_state = swap_board(list(current_node.state), target, neighbor_index)
            new_state_tuple = tuple(new_state)

            # Skip if already visited
            if new_state_tuple in visited:
                continue

            move = get_move_direction(target, neighbor_index)

            # Create new node
            new_node = Node(
                state=new_state_tuple,
                parent=current_node,
                move=move,
                cost=current_node.cost + 1
            )
            # Check if goal
            if is_goal(new_state_tuple):
                # FOUND SOLUTION! Reconstruct path
                return reconstruct_path(new_node)
            queue.append(new_node)
            visited.add(new_state_tuple)
    return None


def get_move_direction(empty_pos, new_pos):

    diff = new_pos - empty_pos

    if diff == -3:
        return "UP"
    elif diff == 3:
        return "DOWN"
    elif diff == -1:
        return "LEFT"
    elif diff == 1:
        return "RIGHT"

def swap_board(board,target,neighbor):
    new_board = board[:]
    temp = new_board[neighbor]
    new_board[neighbor] = new_board[target]
    new_board[target] = temp

    return new_board


def reconstruct_path(goal_node):

    path = []
    current = goal_node

    # Go backwards through parents
    while current.parent is not None:
        path.append(current.move)
        current = current.parent

    # Reverse to get start → goal
    path.reverse()

    return path

def get_neighbors(state):
    neighbors = []
    target = 0

    # Generate valid moves
    for x in range(len(state)):

        if state[x] == 0:
            target = x

            index = x
            row = index // 3
            col = index % 3

            if row != 0:
                neighbors.append(x - 3)  # top

            if col != 2:
                neighbors.append(x + 1)  # right

            if row != 2:
                neighbors.append(x + 3)  # bottom

            if col != 0:
                neighbors.append(x - 1)  # left

    return target, neighbors


def is_goal(initial_state):
    # Check if puzzle solved
    if initial_state == solved:
        return True
    else:
        return False


x = bfs_solve(initial_state)
print(x)