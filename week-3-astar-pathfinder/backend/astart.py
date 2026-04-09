# path  → ["S", "A", "C", "G"]

# steps → [
#     "Step 1: Exploring S  | f=4, g=0, h=4 | Open: [A, B]",
#     "Step 2: Exploring A  | f=4, g=1, h=3 | Open: [B, C]",
#     "Step 3: Exploring C  | f=4, g=2, h=2 | Open: [B, G]",
#     "Step 4: Exploring G  | Goal Reached!",
# ]
node_map = {
    "S": (0, 0),
    "A": (1, 2),
    "B": (3, 1),
    "C": (2, 3),
    "G": (4, 4),
}
edges = [
    ("S", "A"),
    ("S", "B"),
    ("A", "C"),
    ("B", "C"),
    ("C", "G"),
]
start = "S"
goal  = "G"
graph = {}
for u, v in edges:
    if u not in graph:
        graph[u] = []
    if v not in graph:
        graph[v] = []
    graph[u].append(v)
    graph[v].append(u)



def h(node, goalNode):
    return max(abs(node[1] - goalNode[1]), abs(node[0] - goalNode[0]))

open_list = []
closed_list = []

parent = {}


# store as [name, g, h, f]
open_list.append([start, 0, h(node_map[start], node_map[goal]), 0 + h(node_map[start], node_map[goal])])
while open_list:
    lowest= float("inf")
    current = ""
    for node in open_list:
        value = node[1]+node[2]

        if value < lowest:
            lowest = value
            current = node
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

print(parent)
path = []
current = goal
while current != start:
    path.append(current)
    current = parent[current]
path.append(start)
path.reverse()
print(path)