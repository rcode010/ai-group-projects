import os
import datetime



def print_board_to_file(file, state):
    for i in range(0, 9, 3):
        file.write(f"{state[i]} {state[i+1]} {state[i+2]}\n")
    file.write("\n")


def print_board_console(state):
    for i in range(0, 9, 3):
        print(state[i], state[i+1], state[i+2])
    print()


def apply_move(state, move):
    state = list(state)
    zero_index = state.index(0)

    if move == "UP":
        swap_index = zero_index - 3
    elif move == "DOWN":
        swap_index = zero_index + 3
    elif move == "LEFT":
        swap_index = zero_index - 1
    elif move == "RIGHT":
        swap_index = zero_index + 1
    else:
        return tuple(state)

    state[zero_index], state[swap_index] = state[swap_index], state[zero_index]
    return tuple(state)


def write_solution(initial_state, solution_steps, total_cost):
    current_state = initial_state

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_folder = os.path.join(project_root, "output")
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, "solution.txt")

    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(output_path, "w") as file:
        file.write("\n\n")
        file.write("=====================================\n")
        file.write("        8-PUZZLE SOLUTION\n")
        file.write(f"Generated on: {current_time}\n")
        file.write("=====================================\n\n")

        file.write("Initial State:\n")
        print_board_to_file(file, current_state)
        print("Initial State:")
        print_board_console(current_state)

        for step_number, move in enumerate(solution_steps, start=1):
            current_state = apply_move(current_state, move)

            file.write(f"Step {step_number}: Move {move}\n")
            print(f"Step {step_number}: Move {move}")

            print_board_to_file(file, current_state)
            print_board_console(current_state)

        file.write("Goal State Reached!\n")
        print("Goal State Reached!")
        print_board_to_file(file, current_state)
        print_board_console(current_state)

        move_word = "move" if total_cost == 1 else "moves"
        file.write(f"Total Cost: {total_cost} {move_word}\n")
        print(f"Total Cost: {total_cost} {move_word}")


if __name__ == "__main__":
    initial_state = (1, 2, 3, 4, 5, 6, 7, 0, 8)
    solution_steps = ["RIGHT"]
    total_cost = 1

    write_solution(initial_state, solution_steps, total_cost)