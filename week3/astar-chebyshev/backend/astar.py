import math

def chebyshev_distance(x1, y1, x2, y2):
    return max(abs(x1 - x2), abs(y1 - y2))

def solve_astar(graph_data):
    nodes = {n.id: n for n in graph_data.nodes}
    edges_adj = {n.id: {} for n in graph_data.nodes}
    
    # Fill adjacency list
    for edge in graph_data.edges:
        if edge.source in edges_adj and edge.target in edges_adj:
            # We assume bidirectional edges if undirected, but in UI we can make it directed or bidirectional.
            # Let's treat edge as bidirected by default.
            edges_adj[edge.source][edge.target] = edge.weight
            edges_adj[edge.target][edge.source] = edge.weight

    start = graph_data.start_node
    goal = graph_data.goal_node

    if start not in nodes or goal not in nodes:
        return {"path": [], "steps": [], "total_cost": 0, "error": "Start or goal node not found in graph."}

    open_set = {start}
    closed_set = set()

    # For node n, came_from[n] is the node immediately preceding it on the cheapest path from start
    came_from = {}

    # For node n, g_score[n] is the cost of the cheapest path from start to n currently known.
    g_score = {n.id: float('inf') for n in graph_data.nodes}
    g_score[start] = 0

    # For node n, f_score[n] := g_score[n] + h(n).
    f_score = {n.id: float('inf') for n in graph_data.nodes}
    f_score[start] = chebyshev_distance(nodes[start].x, nodes[start].y, nodes[goal].x, nodes[goal].y)

    steps = []

    while open_set:
        # Get node in open_set with lowest f_score value
        current = min(open_set, key=lambda n: f_score[n])

        # Record step
        h_scores = {n: chebyshev_distance(nodes[n].x, nodes[n].y, nodes[goal].x, nodes[goal].y) for n in open_set.union(closed_set).union({current})}
        h_scores[current] = chebyshev_distance(nodes[current].x, nodes[current].y, nodes[goal].x, nodes[goal].y)

        steps.append({
            "current_node": current,
            "open_set": list(open_set),
            "closed_set": list(closed_set),
            "f_scores": {k: v for k, v in f_score.items() if v != float('inf')},
            "g_scores": {k: v for k, v in g_score.items() if v != float('inf')},
            "h_scores": h_scores,
        })

        if current == goal:
            # Reconstruct path
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.insert(0, current)
            return {"path": path, "steps": steps, "total_cost": g_score[goal]}

        open_set.remove(current)
        closed_set.add(current)

        for neighbor, weight in edges_adj[current].items():
            tentative_g_score = g_score[current] + weight

            if tentative_g_score < g_score[neighbor]:
                # This path to neighbor is better than any previous one. Record it!
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + chebyshev_distance(nodes[neighbor].x, nodes[neighbor].y, nodes[goal].x, nodes[goal].y)
                
                if neighbor not in closed_set and neighbor not in open_set:
                    open_set.add(neighbor)

    return {"path": [], "steps": steps, "total_cost": 0, "error": "No path found."}
