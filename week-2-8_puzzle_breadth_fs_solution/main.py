import json, sys, os, io
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import webview
from src.puzzle import Puzzle, GOAL_STATE
from src.file_writer import write_solution, apply_move
from src.gui import HTML

# solver.py prints on import — suppress that without changing the file
sys.stdout = io.StringIO()
from src.solver import bfs_solve
sys.stdout = sys.__stdout__
 




# ── Helper: turn a list of move strings into step-by-step board snapshots ────
def make_steps(state, moves):
    steps = []
    for move in moves:
        empty = state.index(0)
        state = apply_move(state, move)
        steps.append({
            "board":    list(state),
            "from_idx": state.index(0),  # tile came from here
            "to_idx":   empty,           # tile slid into old empty spot
        })
    return steps


# ── Python API — every method here is callable from the JS frontend ───────────
class API:
    def __init__(self):
        self.state = Puzzle.generate_random_board()

    def get_state(self):
        return json.dumps({"board": list(self.state)})

    def solve(self):
        moves = bfs_solve(self.state)
        if moves is None:
            return json.dumps({"solution": None, "total": 0})
        steps = make_steps(self.state, moves)
        write_solution(self.state, moves, len(moves))   # save output/solution.txt
        self.state = GOAL_STATE
        return json.dumps({"solution": steps, "total": len(steps)})

    def shuffle(self):
        self.state = Puzzle.generate_random_board()
        return json.dumps({"board": list(self.state)})

    def reset(self):
        self.state = GOAL_STATE
        return json.dumps({"board": list(self.state)})

    def manual_move(self, index):
        empty = list(self.state).index(0)
        er, ec = divmod(empty, 3)
        tr, tc = divmod(index, 3)
        if abs(er - tr) + abs(ec - tc) != 1:          # not adjacent → ignore
            return json.dumps({"moved": False})
        s = list(self.state)
        s[empty], s[index] = s[index], s[empty]
        self.state = tuple(s)
        return json.dumps({
            "moved": True, "board": list(self.state),
            "from_idx": index, "to_idx": empty,
            "is_goal": self.state == GOAL_STATE,
        })


# ── Launch ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    api = API()
    webview.create_window("8-Puzzle — BFS Solver", html=HTML, js_api=api, width=700, height=820)
    webview.start()
