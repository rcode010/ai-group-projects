def astar(graph, coords, start, goal):

    def h(node, goalNode):
        return max(abs(node[1] - goalNode[1]), abs(node[0] - goalNode[0]))

    open_list = []
    closed_list = []
    parent = {}
    steps = []

    # store as [name, g, h, f]
    start_h = h(coords[start], coords[goal])
    open_list.append([start, 0, start_h, start_h])

    while open_list:
        lowest = float("inf")
        current = None
        for node in open_list:
            f = node[1] + node[2]
            if f < lowest:
                lowest = f
                current = node

        if current is None:
            break

        if current[0] == goal:
            steps.append(f"Exploring {current[0]} | g={current[1]}, h={current[2]}, f={current[3]} | Goal Reached!")
            break

        steps.append(f"Exploring {current[0]} | g={current[1]}, h={current[2]}, f={current[3]} | Open: {[n[0] for n in open_list]}")

        open_list.pop(open_list.index(current))
        closed_list.append(current)

        for neighbor in graph[current[0]]:
            if neighbor in [n[0] for n in closed_list]:
                continue
            new_g = current[1] + 1
            new_h = h(coords[neighbor], coords[goal])
            new_f = new_g + new_h
            open_list.append([neighbor, new_g, new_h, new_f])
            parent[neighbor] = current[0]

    # trace path
    if goal not in parent and start != goal:
        return None

    path = []
    current = goal
    while current != start:
        path.append(current)
        current = parent[current]
    path.append(start)
    path.reverse()

    return {
        "path": path,
        "cost": len(path) - 1,
        "steps": steps
    }