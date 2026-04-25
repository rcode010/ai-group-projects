"""
FastAPI backend for Jigsaw Puzzle Solver.
Handles image upload, GA solving in background, and generation history.

Entry point: python main.py  (or uvicorn main:app)
"""

import threading
import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from concurrent.futures import ThreadPoolExecutor

from puzzle import JigsawPuzzle
from ga import GeneticAlgorithm

app = FastAPI(title="Jigsaw Puzzle GA Solver")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global solver state
# ---------------------------------------------------------------------------

class SolverState:
    """Manages the shared state of the puzzle solver."""

    def __init__(self):
        self.puzzle: Optional[JigsawPuzzle] = None
        self.ga: Optional[GeneticAlgorithm] = None
        self.is_solving: bool = False
        self.should_stop: bool = False
        self.lock = threading.Lock()

    def reset(self):
        """Reset all state for a new puzzle."""
        with self.lock:
            self.puzzle = None
            self.ga = None
            self.is_solving = False
            self.should_stop = False


state = SolverState()
executor = ThreadPoolExecutor(max_workers=4)


# ---------------------------------------------------------------------------
# Background GA loop
# ---------------------------------------------------------------------------

def run_generations_loop(target_generations: int = 200) -> None:
    """Run the GA for *target_generations* steps, one generation at a time.

    Results are appended to ``state.ga.generation_history`` so the frontend
    can poll ``/api/generations`` to get the full scrollable history.
    """
    try:
        while not state.should_stop:
            with state.lock:
                if state.ga is None:
                    break
                current_gen = state.ga.generation

            if current_gen >= target_generations:
                break

            # run_generation() internally calls evaluate_population() which
            # appends to ga.generation_history
            state.ga.run_generation()

            # Small sleep so the polling endpoint can breathe
            time.sleep(0.05)
    finally:
        with state.lock:
            state.is_solving = False


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload an image and split it into 400 puzzle pieces (20×20 grid).

    Returns the piece data and an initial *shuffled* arrangement so the
    frontend can render the scrambled board immediately.
    """
    state.reset()

    upload_dir = Path(__file__).parent / "uploads"
    upload_dir.mkdir(exist_ok=True)

    file_path = upload_dir / file.filename
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    try:
        state.puzzle = JigsawPuzzle(str(file_path), grid_size=20)

        state.ga = GeneticAlgorithm(
            pieces=state.puzzle.pieces,
            grid_size=20,
            population_size=100,
            elitism_count=5,
            mutation_rate=0.02,
            tournament_size=5,
        )
        state.ga.create_initial_population()

        initial_arrangement = state.puzzle.get_random_arrangement()

        return JSONResponse({
            "success": True,
            "pieces": state.puzzle.get_pieces_data(),
            "initial_arrangement": initial_arrangement,
            "message": f"Image split into {state.puzzle.total_pieces} pieces",
        })

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process image: {str(e)}")


@app.post("/api/solve/start")
async def start_solving():
    """Start the GA solver in a background thread."""
    if state.puzzle is None:
        raise HTTPException(
            status_code=400, detail="No puzzle loaded. Upload an image first.")

    with state.lock:
        if state.is_solving:
            return JSONResponse({"success": True, "message": "Solver already running"})

        # Reset history for a fresh solve run
        if state.ga:
            state.ga.create_initial_population()

        state.is_solving = True
        state.should_stop = False

    executor.submit(run_generations_loop, 200)

    return JSONResponse({"success": True, "message": "Solver started"})


@app.post("/api/solve/stop")
async def stop_solving():
    """Signal the background loop to halt after the current generation."""
    with state.lock:
        state.should_stop = True
        state.is_solving = False

    return JSONResponse({"success": True, "message": "Solver stopped"})


@app.get("/api/solve/status")
async def get_status():
    """Return current solver status — polled by the frontend every 500 ms."""
    with state.lock:
        current_gen = state.ga.generation if state.ga else 0
        best_fitness = state.ga.get_best_fitness() if state.ga else 0.0
        total_saved = len(state.ga.generation_history) if state.ga else 0

    return JSONResponse({
        "is_solving": state.is_solving,
        "current_generation": current_gen,
        "best_fitness": round(best_fitness, 2),
        "total_generations_saved": total_saved,
    })


@app.get("/api/generations")
async def get_generations():
    """Return summary list of all saved generations (no chromosome payload).

    The frontend uses this to build the scrollable history list.
    Each entry: ``{id, generation, fitness}``.
    """
    with state.lock:
        if state.ga is None:
            return JSONResponse({"generations": []})

        summary = [
            {
                # use generation number as stable ID
                "id": entry["generation"],
                "generation": entry["generation"],
                "fitness": round(entry["fitness"], 2),
            }
            for entry in state.ga.generation_history
        ]

    return JSONResponse({"generations": summary})


@app.get("/api/generations/{gen_id}")
async def get_generation(gen_id: int):
    """Return the full chromosome + rendered images for a specific generation.

    The frontend calls this when the user clicks a history entry.
    ``gen_id`` is the generation number (same value used as ``id`` in the list).
    """
    with state.lock:
        if state.ga is None:
            raise HTTPException(status_code=404, detail="No solver loaded")

        entry = next(
            (e for e in state.ga.generation_history if e["generation"] == gen_id),
            None,
        )

        if entry is None:
            raise HTTPException(
                status_code=404, detail=f"Generation {gen_id} not found")

        chromosome = entry["chromosome"]
        images = state.puzzle.get_arrangement_images(
            chromosome) if state.puzzle else []

    return JSONResponse({
        "generation": entry["generation"],
        "fitness": round(entry["fitness"], 2),
        "chromosome": chromosome,
        "images": images,
    })


@app.get("/api/current-best")
async def get_current_best():
    """Return the best chromosome seen across all generations so far."""
    with state.lock:
        if state.ga is None or not state.ga.generation_history:
            return JSONResponse({"message": "No generations yet"})

        best = max(state.ga.generation_history, key=lambda e: e["fitness"])
        chromosome = best["chromosome"]
        images = state.puzzle.get_arrangement_images(
            chromosome) if state.puzzle else []

    return JSONResponse({
        "generation": best["generation"],
        "fitness": round(best["fitness"], 2),
        "chromosome": chromosome,
        "images": images,
    })


@app.delete("/api/reset")
async def reset_solver():
    """Tear down all solver state so the user can start fresh."""
    state.reset()
    return JSONResponse({"success": True, "message": "Solver reset"})


@app.get("/api/health")
async def health_check():
    """Simple liveness probe."""
    return JSONResponse({"status": "ok"})


# ---------------------------------------------------------------------------
# Single entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
