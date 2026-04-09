from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
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
    name: str
    x: int
    y: int


class GraphInput(BaseModel):
    nodes: List[Node]
    edges: List[List[str]]
    start: str
    goal: str


# -------- VALIDATION -------- #

def validate_graph(data: GraphInput):
    node_names = {node.name for node in data.nodes}

    if data.start not in node_names:
        raise HTTPException(status_code=400, detail="Start node not found")

    if data.goal not in node_names:
        raise HTTPException(status_code=400, detail="Goal node not found")

    for edge in data.edges:
        if len(edge) != 2:
            raise HTTPException(status_code=400, detail="Invalid edge")

        if edge[0] not in node_names or edge[1] not in node_names:
            raise HTTPException(
                status_code=400, detail="Edge has unknown node")


# -------- CONVERT DATA -------- #

def convert_graph(data: GraphInput):
    coords = {}
    graph = {}

    for node in data.nodes:
        coords[node.name] = (node.x, node.y)
        graph[node.name] = []

    for a, b in data.edges:
        graph[a].append(b)
        graph[b].append(a)

    return graph, coords


# -------- ROUTES -------- #

@app.get("/")
def home():
    return {"message": "Backend is working"}


@app.post("/run-astar")
def run_astar(data: GraphInput):
    try:
        validate_graph(data)

        graph, coords = convert_graph(data)

        result = astar(graph, coords, data.start, data.goal)

        if result is None:
            raise HTTPException(status_code=400, detail="No path found")

        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
