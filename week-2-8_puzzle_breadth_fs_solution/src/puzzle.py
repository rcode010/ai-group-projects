import random

GOAL_STATE = (1, 2, 3,
              4, 5, 6,
              7, 8, 0)

class Puzzle:

    @staticmethod
    def generate_random_board():
        while True:
            board_list = list(range(9)) 
            random.shuffle(board_list)
            board_tuple = tuple(board_list)
            if Puzzle.is_solvable(board_tuple):
                return board_tuple

    @staticmethod
    def is_solvable(board):
        inversions = 0
        for i in range(8):
            for j in range(i + 1, 9):
                if board[i] != 0 and board[j] != 0 and board[i] > board[j]:
                    inversions += 1
        return inversions % 2 == 0

    @staticmethod
    def get_neighbors(state):
        neighbors = []
        zero_index = state.index(0)
        row, col = divmod(zero_index, 3)
        directions = {
            "UP": (-1, 0),
            "DOWN": (1, 0),
            "LEFT": (0, -1),
            "RIGHT": (0, 1)
        }
        for move_name, (row_change, col_change) in directions.items():
            new_row = row + row_change
            new_col = col + col_change
            if 0 <= new_row < 3 and 0 <= new_col < 3:
                new_index = new_row * 3 + new_col
                new_state = list(state)
                new_state[zero_index], new_state[new_index] = new_state[new_index], new_state[zero_index]
                neighbors.append((tuple(new_state), move_name))
        return neighbors

if __name__ == "__main__":
    random_board = Puzzle.generate_random_board()
    print("Random Board:")
    for i in range(0, 9, 3):
        print(random_board[i:i + 3])
    print("\nIs this board solvable?", Puzzle.is_solvable(random_board))
    print("\nPossible Moves from initial state:")
    for new_state, move in Puzzle.get_neighbors(random_board):
        print(f"Move: {move}, Resulting State: {new_state}")