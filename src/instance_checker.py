from more_itertools import pairwise
from ortools.linear_solver import pywraplp  # type: ignore
from sys import argv
from typing import NoReturn


# Algorithm overview:

# Assuming we have K blackouts, we treat the problem as if we have K+1 knapsacks:
# One knapsack for the interval before the first blackout, then knapsacks for the intervals between
# each blackout, and one "infinite" knapsack _after_ the last blackout.
# For ease of implementation, we assign the last knapsack capacity equal to the sum of all pictures.

# Then, we solve the problem as if it were a "multiple knapsack problem", but with a twist:
# The knapsacks have an exponentially increasing penalty, represented by a constant C (here C = 10).
# e.g. first knapsack has penalty C, the second knapsack has penalty C², the third has penalty C³,
# and so on.

# Here's a visual diagram (Inputs are equivalent to those from data/set1.txt):

# Input picture lengths: 2, 2, 3, 4, 1
# Input blackouts: 3 5, 8 12
# (i.e. the first blackout starts at 3, and the first "free" time after it is 5)

# Timeline of blackouts (each dot represents a time unit, hashes represent blackouts):
# 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20
#  .  .  .  #  #  .  .  .  #  #  #  #  .  .  .  .  .  .  .  .  .

# Timeline of pictures (each picture is delimited by [ and ]):
# 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20
#  .  .  .  #  #  .  .  .  #  #  #  #  .  .  .  .  .  .  .  .  .
#  [  .  ]  #  #  [  ] []  #  #  #  #  [  ]  [  .  .  ]  .  .  .

# The output will be:
# [[3], [2, 1], [2, 4]]
# 18

# Reference: https://developers.google.com/optimization/bin/multiple_knapsack

def fail_with(message: str) -> NoReturn:
    print(message)
    exit(1)


Blackout = tuple[float, float]
Input = tuple[list[float], list[Blackout]]


def parse_blackout(line: str) -> Blackout:
    [start, duration] = map(float, line.split(","))
    return start, start + duration


def parse_input(path: str) -> tuple[list[float], list[Blackout], float]:
    with open(path, "r") as f:
        num_pictures = int(f.readline())
        pictures = [float(f.readline()) for _ in range(num_pictures)]

        num_blackouts = int(f.readline())
        blackouts = [parse_blackout(f.readline()) for _ in range(num_blackouts)]
        blackouts.sort()

        expected_total_cost = float(f.readline())

        print("Pictures:", pictures)
        print("Blackouts:", blackouts)
        print("ExpectedTotalCost:", expected_total_cost)

        return pictures, blackouts, expected_total_cost


# Turn a list of blackouts into a list of knapsacks.
def get_knapsacks(pictures: list[float], blackouts: list[Blackout]) -> list[float]:
    return \
        [blackouts[0][0]] \
        + [start - end for ((_, end), (start, _)) in pairwise(blackouts)] \
        + [sum(pictures)]


Output = tuple[float, list[float]]


def solve(parsed_input: Input) -> Output:
    (pictures, blackouts) = parsed_input
    num_pictures = len(pictures)

    if not pictures or not blackouts:
        fail_with("Trivial solution")

    knapsacks = get_knapsacks(pictures, blackouts)
    num_knapsacks = len(knapsacks)
    print("Knapsacks:", knapsacks)
    print()

    solver = pywraplp.Solver.CreateSolver("SCIP") or fail_with("SCIP solver unavailable")

    # x[p][k] is 1 if picture `p` is in knapsack `k`
    x = [[solver.BoolVar(f"x[{p}, {k}]") for k in range(num_knapsacks)] for p in range(num_pictures)]

    # Constraint: Each picture is in exactly one knapsack
    for p in range(num_pictures):
        solver.Add(sum(x[p][k] for k in range(num_knapsacks)) == 1)

    # Constraint: The length of the pictures in each knapsack cannot exceed its capacity
    for k in range(num_knapsacks):
        solver.Add(sum(x[p][k] * pictures[p] for p in range(num_pictures)) <= knapsacks[k])

    # Objective: Minimize the coefficients of each picture in each knapsack
    solver.Minimize(
        solver.Sum(x[p][k] * pictures[p] * (k + 1) ** 2 for k in range(num_knapsacks) for p in range(num_pictures)))

    # Run the solver
    status = solver.Solve()
    if status != pywraplp.Solver.OPTIMAL:
        fail_with("No optimal solution")

    # Compute the output
    knaps = [[p for p in range(num_pictures) if x[p][k].solution_value()] for k in range(num_knapsacks)]
    print("Pictures in knapsacks:", knaps)

    times = [0.] * num_pictures
    t = 0

    for i, knap in enumerate(knaps):
        if i > 0:
            t = blackouts[i - 1][1]

        for p in knap:
            times[p] = t
            t += pictures[p]

    last_pic = max(times)
    total_time = last_pic + pictures[times.index(last_pic)]

    return total_time, times


def main() -> None:
    input_path = argv[1]
    (pictures, blackouts, expected_total_cost) = parse_input(input_path)
    (total_time, times) = solve((pictures, blackouts))

    print("Total time:", total_time)
    print("Sending times:", times)
    print("\nCorrect Instance:", total_time == expected_total_cost)


if __name__ == "__main__":
    main()
