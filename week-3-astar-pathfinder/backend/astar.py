def astar(graph, coords, start, goal):
    """
    A* pathfinder using Chebyshev distance heuristic.

    Args:
        graph  : dict  { node_id: [(neighbor_id, weight), ...] }
        coords : dict  { node_id: (x, y) }
        start  : str   start node id
        goal   : str   goal node id

    Returns a dict with keys:
        path        - list of node ids from start to goal
        cost        - numeric total cost
        total_cost  - same as cost (alias for frontend)
        steps       - list of structured step dicts
    """

    def h(node_id, goal_id):
        nx, ny = coords[node_id]
        gx, gy = coords[goal_id]
        return max(abs(nx - gx), abs(ny - gy))

    # open list entries: [node_id, g, h_val, f]
    start_h = h(start, goal)
    open_list = [[start, 0, start_h, start_h]]

    closed_set = set()
    parent = {}
    g_score = {start: 0}
    steps = []

    while open_list:
        # pick node with lowest f = g + h
        open_list.sort(key=lambda n: n[1] + n[2])
        current = open_list.pop(0)
        cur_id, cur_g, cur_h, cur_f = current

        if cur_id in closed_set:
            continue

        closed_set.add(cur_id)

        goal_reached = cur_id == goal

        steps.append({
            "current_node": cur_id,
            "g": round(cur_g, 4),
            "h": round(cur_h, 4),
            "f": round(cur_f, 4),
            "open_set": [n[0] for n in open_list if n[0] not in closed_set],
            "closed_set": list(closed_set),
            "f_scores": {n[0]: round(n[1] + n[2], 4) for n in open_list if n[0] not in closed_set},
            "goal_reached": goal_reached,
        })

        if goal_reached:
            break

        for neighbor_id, weight in graph.get(cur_id, []):
            if neighbor_id in closed_set:
                continue
            new_g = cur_g + weight
            if new_g < g_score.get(neighbor_id, float("inf")):
                g_score[neighbor_id] = new_g
                new_h = h(neighbor_id, goal)
                new_f = new_g + new_h
                open_list.append([neighbor_id, new_g, new_h, new_f])
                parent[neighbor_id] = cur_id

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

    total_cost = g_score.get(goal, len(path) - 1)

    return {
        "path": path,
        "cost": total_cost,
        "total_cost": total_cost,
        "steps": steps,
    }