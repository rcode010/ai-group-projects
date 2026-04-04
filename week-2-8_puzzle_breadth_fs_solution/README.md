# 8-Puzzle — Breadth-First Search Solver
An interactive 8-puzzle game with a BFS solver, glassmorphic GUI, and step-by-step solution logging.

---

## Project Structure
```
week-2-8_puzzle_breadth_fs_solution/
├── src/
│   ├── __init__.py
│   ├── solver.py           # BFS algorithm — finds optimal solution
│   ├── puzzle.py           # Board generation, solvability check, neighbors
│   ├── file_writer.py      # Writes step-by-step solution to output/
│   └── gui.py              # Glassmorphic HTML/JS frontend (pywebview)
├── output/
│   └── solution.txt        # Auto-generated solution log
├── main.py                 # Entry point — connects all modules via pywebview API
└── README.md
```

---

## How It Works

The puzzle board is a 3×3 grid with tiles 1–8 and one blank space. The player can move tiles manually or let the BFS solver find the optimal solution automatically.

**Solve Flow:**
```
User clicks SOLVE
      │
      ▼
BFS explores states layer by layer (shortest path guaranteed)
      │
      ▼
Solution path reconstructed (list of moves: UP / DOWN / LEFT / RIGHT)
      │
      ▼
GUI animates each tile slide step-by-step with progress bar
      │
      ▼
solution.txt written to output/ with every board state
      │
      ▼
Confetti celebration + SOLVED badge
```


## Installation

**1. Clone the repository**
```bash
git clone https://github.com/rcode010/ai-group-projects.git
cd week-2-8_puzzle_breadth_fs_solution
```

**2. Install dependencies**
```bash
pip install pywebview
```

---

## Running the App

```bash
python main.py
```

This will:
- Generate a random solvable 8-puzzle board
- Open the glassmorphic GUI window (700 × 820)

**Controls:**
| Action | How |
|---|---|
| Move a tile | Click any tile adjacent to the blank |
| Auto-solve (BFS) | Click **⚡ SOLVE** or press `S` |
| Shuffle board | Click **✦ SHUFFLE** or press `R` |
| Reset to goal | Click **↺ RESET** or press `G` |

---

## Modules

| File | Responsibility |
|---|---|
| `solver.py` | BFS with `Node` class, visited set, path reconstruction |
| `puzzle.py` | Random solvable board generation, inversion-count solvability check |
| `file_writer.py` | `apply_move` logic, writes full step-by-step log to `output/solution.txt` |
| `gui.py` | Full glassmorphic UI — tiles, animations, confetti, progress bar, keyboard shortcuts |
| `main.py` | Bridges Python API to JS frontend; orchestrates solve/shuffle/reset/manual-move |

---

## Solution Output

Every time the solver runs, `output/solution.txt` is overwritten with:

```
=====================================
        8-PUZZLE SOLUTION
Generated on: 2026-03-28 17:54:38
=====================================

Initial State:
1 6 2
7 8 0
5 3 4

Step 1: Move DOWN
1 6 2
7 8 4
5 3 0
...
Goal State Reached!
1 2 3
4 5 6
7 8 0

Total Cost: 15 moves
```

---

## Algorithm — BFS

BFS guarantees the **minimum number of moves** to reach the goal state `(1 2 3 / 4 5 6 / 7 8 0)`.

- Time complexity: **O(b^d)** where b = branching factor (~3), d = solution depth
- Space complexity: **O(b^d)** — all visited states stored in memory
- Solvability is pre-checked using **inversion count** (even = solvable) before searching

---

## Team

| Name | Responsibility |
|---|---|
| Raman | Project architecture, `solver.py` — BFS algorithm and path reconstruction  |
| Rand | `gui.py` — glassmorphic frontend, animations, confetti |
| Zmnako| `puzzle.py` — board generation and solvability check |
| Bahoz | `file_writer.py` — solution logging and move application |
| Hunar | `main.py`, pywebview API integration |