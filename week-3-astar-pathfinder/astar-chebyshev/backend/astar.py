def astar(graph, coords, start, goal):
    # temporary fake result (for testing)
    return {
        "steps": [
            {"current": start, "open": [start], "closed": []},
            {"current": goal, "open": [], "closed": [start]}
        ],
        "path": [start, goal],
        "cost": 1
    }
