def astar(graph, coords, start, goal, node_weights=None):
    """
    A* pathfinder using Chebyshev distance heuristic.

    Args:
        graph        : dict  { node_id: [(neighbor_id, edge_weight), ...] }
        coords       : dict  { node_id: (x, y) }
        start        : str   start node id
        goal         : str   goal node id
        node_weights : dict  { node_id: weight }  — each node's own cost

    g(n) = sum of ALL edge weights along the path from start to n
           + weight of CURRENT node only (not parent nodes)

    Returns a dict with keys:
        path        - list of node ids from start to goal
        cost        - numeric total cost
        total_cost  - same as cost (alias for frontend)
        steps       - list of structured step dicts
    """

    if node_weights is None:
        node_weights = {nid: 0 for nid in graph}

    def h(node_id, goal_id):
        """Chebyshev distance heuristic"""
        nx, ny = coords[node_id]
        gx, gy = coords[goal_id]
        return max(abs(nx - gx), abs(ny - gy))

    # Initial g for start node includes start node's own weight
    start_g = node_weights.get(start, 0)
    start_h = h(start, goal)
    start_f = start_g + start_h

    # open list entries: [node_id, g, h_val, f]
    open_list = [[start, start_g, start_h, start_f]]

    closed_set = set()
    parent = {}
    g_score = {start: start_g}
    h_score = {start: start_h}
    steps = []

    while open_list:
        # pick node with lowest f = g + h
        open_list.sort(key=lambda n: n[3])
        current = open_list.pop(0)
        cur_id, cur_g, cur_h, cur_f = current

        if cur_id in closed_set:
            continue

        closed_set.add(cur_id)

        goal_reached = cur_id == goal

        steps.append({
            "current_node": cur_id,
            "node_weight": node_weights.get(cur_id, 0),
            "g": round(cur_g, 4),
            "h": round(cur_h, 4),
            "f": round(cur_f, 4),
            "open_set": [n[0] for n in open_list if n[0] not in closed_set],
            "closed_set": list(closed_set),
            "f_scores": {n[0]: round(n[3], 4) for n in open_list if n[0] not in closed_set},
            "g_scores": {nid: round(gs, 4) for nid, gs in g_score.items()},
            "h_scores": {nid: round(hs, 4) for nid, hs in h_score.items()},
            "goal_reached": goal_reached,
        })

        if goal_reached:
            break

        for neighbor_id, edge_weight in graph.get(cur_id, []):
            if neighbor_id in closed_set:
                continue
            # g(neighbor) = (g(cur) - node_weight[cur]) + edge_weight + node_weight[neighbor]
            # i.e. subtract the current node's own weight (already baked in),
            # add the traversed edge, then add only the neighbor's own weight.
            new_g = (cur_g - node_weights.get(cur_id, 0)) + edge_weight + node_weights.get(neighbor_id, 0)
            if new_g < g_score.get(neighbor_id, float("inf")):
                g_score[neighbor_id] = new_g
                new_h = h(neighbor_id, goal)
                new_f = new_g + new_h
                h_score[neighbor_id] = new_h
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

    total_cost = g_score.get(goal, 0)

    return {
        "path": path,
        "cost": total_cost,
        "total_cost": total_cost,
        "steps": steps,
    }