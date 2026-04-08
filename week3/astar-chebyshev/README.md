# A* Path Finder with Chebyshev Distance

This project implements the A* pathfinding algorithm using the Chebyshev distance metric for heuristics.

## Features
- Interactive grid for adding nodes and edges.
- Set Start (S) and Goal (G) nodes.
- Step-by-step visualization of the A* algorithm process.
- FastAPI backend for pure Python pathfinding logic.

## Project Structure
- `backend/`: FastAPI application and A* implementation.
- `frontend/`: React + Vite + Tailwind CSS visualization.

## Setup

### Backend
1. Install dependencies: `pip install -r backend/requirements.txt`
2. Run server: `uvicorn backend.main:app --reload`

### Frontend
1. Install dependencies: `npm install`
2. Run dev server: `npm run dev`
