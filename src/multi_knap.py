from itertools import pairwise
from ortools.linear_solver import pywraplp # type: ignore
from sys import argv
from typing import NoReturn

# Algorithm overview:

# Assuming we have K blackouts, we treat the problem as if we have K knapsacks:
# The first knapsack correspons to the timeframe from time 0 to the beginning of the first blackout,
# and the rest of the knapsacks are the periods of time in between each blackout.
# Note that the period _after_ the last blackout is _not_ considered a knapsack.

# Then, we apply an algorithm for "multiple knapsack problem" on the K knapsacks.
# This will fill all the knapsacks in the most efficient way.

# There may be "leftover" pictures, that remain to be sent _after_ the last blackout.
# In this case, knowing that all the knapsacks are "filled to the brim", the total time will be:
# end_of_last_blackout + sum(leftover_pictures)

# If there are no "leftover" pictures, then the formula is adjusted to use the "last full knapsack"
# instead of the leftover pictures.

# Here's a visual diagram (Inputs are from data/set1.txt):

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

# Based on: https://developers.google.com/optimization/bin/multiple_knapsack

def fail_with(message: str) -> NoReturn:
  print(message)
  exit(1)

Blackout = tuple[float, float]
Input = tuple[list[float], list[Blackout]]

def parse_input(path: str) -> Input:
  with open(path, "r") as f:
    num_pictures = int(f.readline())
    pictures = [float(f.readline()) for _ in range(num_pictures)]

    num_blackouts = int(f.readline())
    blackouts = [tuple(map(float, f.readline().split(","))) for _ in range(num_blackouts)]
    blackouts = list(sorted(map(lambda s: (s[0], s[0] + s[1]), blackouts)))

    print("Blackouts:", blackouts)
    return (pictures, blackouts)

# Turn a list of blackouts into a list of knapsacks.
def get_knapsacks(blackouts: list[Blackout]) -> list[float]:
  return [blackouts[0][0]] + [start - end for ((_, end), (start, _)) in pairwise(blackouts)]

Output = tuple[list[list[float]], float]

def solve(input: Input) -> Output:
  (pictures, blackouts) = input
  num_pictures = len(pictures)

  if not pictures or not blackouts:
    print("Trivial solution")
    return ([pictures], sum(pictures))

  knapsacks = get_knapsacks(blackouts)
  num_knapsacks = len(knapsacks)

  solver = pywraplp.Solver.CreateSolver("SCIP") or fail_with("SCIP solver unavailable")

  # x[p][k] is 1 if picture `p` is in knapsack `k`
  x = [[solver.BoolVar(f"x[{p}, {k}]") for k in range(num_knapsacks)] for p in range(num_pictures)]

  # Constraint: Each picture is in at most one knapsack
  for p in range(num_pictures):
    solver.Add(sum(x[p][k] for k in range(num_knapsacks)) <= 1)

  # Constraint: The length of the pictures in each knapsack cannot exceed its capacity
  for k in range(num_knapsacks):
    solver.Add(sum(x[p][k] * pictures[p] for p in range(num_pictures)) <= knapsacks[k])

  # Objective: Maximize the length of pictures in each knapsack
  obj = solver.Objective()
  for p in range(num_pictures):
    for k in range(num_knapsacks):
      obj.SetCoefficient(x[p][k], pictures[p] * (num_knapsacks - k))
  obj.SetMaximization()

  status = solver.Solve()
  if status != pywraplp.Solver.OPTIMAL:
    fail_with("No optimal solution")

  # Compute list of pictures, grouped by their knapsack
  knaps = [[pictures[p] for p in range(num_pictures) if x[p][k].solution_value()] for k in range(num_knapsacks)]
  leftover = [pictures[p] for p in range(num_pictures) if not any(x[p][k].solution_value() for k in range(num_knapsacks))]

  # Total time required to send all pictures
  if leftover:
    total_time = blackouts[-1][1] + sum(leftover)
  else:
    last_full_knapsack = max(k for k in range(num_knapsacks) if knaps[k])
    total_time = blackouts[last_full_knapsack - 1][1] + sum(knaps[last_full_knapsack])

  return (knaps + [leftover], total_time)

def main() -> None:
  input_path = argv[1]
  input = parse_input(input_path)
  (knapsacks, total_time) = solve(input)

  print("Knapsacks:", knapsacks)
  print("Total time:", total_time)

if __name__ == "__main__":
  main()
