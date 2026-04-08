from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from astar import solve_astar

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Node(BaseModel):
    id: str
    x: float
    y: float

class Edge(BaseModel):
    source: str
    target: str
    weight: float

class GraphData(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    start_node: str
    goal_node: str

@app.post("/api/solve")
async def solve(graph_data: GraphData):
    result = solve_astar(graph_data)
    return result
