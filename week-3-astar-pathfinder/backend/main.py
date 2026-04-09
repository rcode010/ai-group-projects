from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from astar import astar
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------- DATA MODELS -------- #

class Node(BaseModel):
    id: str
    x: int
    y: int


class Edge(BaseModel):
    source: str
    target: str
    weight: Optional[int] = 1


class GraphInput(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    start_node: str
    goal_node: str


# -------- VALIDATION -------- #

def validate_graph(data: GraphInput):
    node_ids = {node.id for node in data.nodes}

    if data.start_node not in node_ids:
        raise HTTPException(status_code=400, detail="Start node not found")

    if data.goal_node not in node_ids:
        raise HTTPException(status_code=400, detail="Goal node not found")

    for edge in data.edges:
        if edge.source not in node_ids or edge.target not in node_ids:
            raise HTTPException(status_code=400, detail=f"Edge references unknown node: {edge.source} -> {edge.target}")


# -------- CONVERT DATA -------- #

def convert_graph(data: GraphInput):
    coords = {}
    graph = {}

    for node in data.nodes:
        coords[node.id] = (node.x, node.y)
        graph[node.id] = []

    for edge in data.edges:
        graph[edge.source].append(edge.target)
        graph[edge.target].append(edge.source)

    return graph, coords


# -------- ROUTES -------- #

@app.get("/")
def home():
    return {"message": "A* Pathfinder backend is running"}


@app.post("/api/solve")
def solve(data: GraphInput):
    try:
        validate_graph(data)

        graph, coords = convert_graph(data)

        result = astar(graph, coords, data.start_node, data.goal_node)

        if result is None:
            raise HTTPException(status_code=400, detail="No path found between start and goal")

        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
