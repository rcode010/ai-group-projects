# A* Pathfinder — Graph Pathfinding Visualization
An interactive full-stack application (FastAPI + React) that allows users to draw a graph, set node weights, and visualize the **A* (A-Star) search algorithm** step-by-step using the Chebyshev distance heuristic.

---

## Project Structure
```
week-3-astar-pathfinder/
├── backend/
│   ├── main.py             # FastAPI server, API endpoints, data models
│   ├── astar.py            # A* algorithm implementation (Chebyshev + node weights)
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.tsx         # Core React component (Interactive Graph Board & Results Modal)
│   │   └── ...             # CSS and initialization files
│   ├── package.json        # Node.js dependencies
│   └── vite.config.ts      # Build tool configuration
└── README.md
```

---

## How It Works

The web app allows users to interactively build a graph on a grid, place nodes with custom weights, and connect them with weighted edges. Once a Start and Goal node are defined, the backend calculates the shortest path using the A* algorithm.

**Solve Flow:**
```
User draws graph & clicks "Solve Path"
      │
      ▼
Frontend sends graph data (nodes, edges, start, goal, weights) to FastAPI backend
      │
      ▼
A* algorithm explores node-by-node using f(n) = g(n) + h(n)
      │
      ▼
Algorithm captures step-by-step exploration state (open list, closed list, f/g/h values)
      │
      ▼
Backend returns optimal path, total cost, and execution steps to frontend
      │
      ▼
Frontend displays solution path and opens Step-by-Step Visualization Modal
```


## Installation

**1. Clone the repository**
```bash
git clone https://github.com/rcode010/ai-group-projects.git
cd week-3-astar-pathfinder
```

**2. Setup Backend**
```bash
cd backend
pip install -r requirements.txt
```

**3. Setup Frontend**
Open a new terminal window:
```bash
cd frontend
npm install
```

---

## Running the App

You will need to run the backend and frontend simultaneously.

**Start the Backend:**
```bash
cd backend
uvicorn main:app --reload
# Runs on http://localhost:8000
```

**Start the Frontend:**
```bash
cd frontend
npm run dev
# Vite will provide a localhost URL to open the app (typically http://localhost:5173)
```

**Controls & Tools (Frontend):**
| Tool | Action |
|---|---|
| **Select / Move** | Drag nodes around the grid, or Right-Click to Delete a node |
| **Add Node** | Click anywhere on the grid to create a node. Prompts for node weight. |
| **Add Edge** | Click one node, then another, to add an edge. Prompts for edge weight. |
| **Set Start/Goal**| Select target nodes to set as the starting point and goal point. |

---

## Algorithm — A* (A-Star)

A* uses a best-first search strategy, prioritizing nodes that have the lowest **f(n)** value.
`f(n) = g(n) + h(n)`

- **`g(n)` (Path Cost)**: Calculated as the sum of ALL edge costs traversed from the start node to the current node, PLUS the current node's own weight. (It intentionally strips out parent node internal weights).
- **`h(n)` (Heuristic)**: Calculates the estimated distance to the goal node. This implementation uses the **Chebyshev distance** heuristic: `max(|x1 - x2|, |y1 - y2|)`, which accurately maps out 8-way grid movement.

---

## Key Features

1. **Custom Node Weights:** Calculate true traversal cost where cities or junctions themselves have a delay or cost.
2. **Step-by-Step Transparency:** A detailed exploration model that shows exactly what Open Set and Closed Set elements existed at each node evaluation.
3. **Interactive Grid:** Draggable glassmorphic style nodes with edge distance tooltips and connection highlighting.
