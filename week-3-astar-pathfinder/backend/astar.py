def astar(graph, coords, start, goal):
    def h(node, goalNode):
        return max(abs(node[1] - goalNode[1]), abs(node[0] - goalNode[0]))

    node_map = coords
    open_list = []
    closed_list = []
    parent = {}
    
    # We will build these steps for the frontend UI
    frontend_steps = []

    # store as [name, g, h, f]
    open_list.append([start, 0, h(node_map[start], node_map[goal]), 0 + h(node_map[start], node_map[goal])])
    
    while open_list:
        lowest = float("inf")
        current = ""
        for node in open_list:
            value = node[1] + node[2]
            if value < lowest:
                lowest = value
                current = node
                
        # --- Added this single block just to send data to your React frontend ---
        frontend_steps.append({
            "current_node": current[0],
            "open_set": [n[0] for n in open_list],
            "closed_set": [n[0] for n in closed_list],
            "f_scores": {n[0]: n[1]+n[2] for n in open_list},
            "h_scores": {n[0]: n[2] for n in open_list}
        })
        # ----------------------------------------------------------------------
                
        if current[0] == goal:
            break
            
        open_list.pop(open_list.index(current))
        closed_list.append(current)
        
        for node in graph[current[0]]:
            if node in [n[0] for n in closed_list]:
                continue
            new_g = current[1] + 1
            open_list.append([node, new_g, h(node_map[node], node_map[goal]), new_g + h(node_map[node], node_map[goal])])
            parent[node] = current[0]

    # Reconstruct path based on your exact loop
    if current[0] != goal:
        return None
        
    path = []
    current_node = goal
    while current_node != start:
        path.append(current_node)
        current_node = parent[current_node]
    path.append(start)
    path.reverse()

    return {
        "path": path,
        "total_cost": current[1], # current[1] is the final 'g' cost
        "steps": frontend_steps
    }
