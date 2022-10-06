from itertools import pairwise
from ortools.linear_solver import pywraplp # type: ignore
from sys import argv
from typing import NoReturn
import time

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
  return (start, start + duration)

def parse_input(path: str) -> Input:
  with open(path, "r") as f:
    num_pictures = int(f.readline())
    pictures = [float(f.readline()) for _ in range(num_pictures)]

    num_blackouts = int(f.readline())
    blackouts = [parse_blackout(f.readline()) for _ in range(num_blackouts)]
    blackouts.sort()

    print("Pictures:", pictures)
    print("Blackouts:", blackouts)

    return (pictures, blackouts)

# Turn a list of blackouts into a list of knapsacks.
def get_knapsacks(pictures: list[float], blackouts: list[Blackout]) -> list[float]:
  return [blackouts[0][0]] + [start - end for ((_, end), (start, _)) in pairwise(blackouts)] + [sum(pictures)]

Output = tuple[list[list[float]], float]

def solve(input: Input) -> Output:
  (pictures, blackouts) = input
  num_pictures = len(pictures)

  if not pictures or not blackouts:
    print("Trivial solution")
    return ([pictures], sum(pictures))

  knapsacks = get_knapsacks(pictures, blackouts)
  num_knapsacks = len(knapsacks)
  print("Knapsacks:", knapsacks)
  print()

  solver = pywraplp.Solver.CreateSolver("SCIP") or fail_with("SCIP solver unavailable")

  #
  # DECISION VARIABLES
  #

  # x[p][k] is 1 if picture `p` is in knapsack `k`
  x = [[solver.BoolVar(f"x[{p}, {k}]") for k in range(num_knapsacks)] for p in range(num_pictures)]

  # c[k] if knapsack k is used
  c = [solver.BoolVar(f"c[{k}]") for k in range(num_knapsacks)]

  # l[k] if knapsack k is last knapsack
  l = [solver.BoolVar(f"l[{k}]") for k in range(num_knapsacks)]

  # same as x but only for the last knapsack
  z = [[solver.BoolVar(f"z[{p}, {k}]") for k in range(num_knapsacks)] for p in range(num_pictures)]

  #
  # CONSTRAINTS
  #

  # Constraint: Each picture is in exactly one knapsack
  for p in range(num_pictures):
    solver.Add(sum(x[p][k] for k in range(num_knapsacks)) == 1)

  # Constraint: The length of the pictures in each knapsack cannot exceed its capacity
  for k in range(num_knapsacks):
    solver.Add(sum(x[p][k] * pictures[p] for p in range(num_pictures)) <= knapsacks[k])

  # Constraint: Taking knapsacks from left, group the knapsacks by 1 first, then by  0
  for k in range(1, num_knapsacks):
    solver.Add((c[k] - c[k - 1]) <= 0)

  # Constraint: All photos have to fit in used knapsacks
  for k in range(1, num_knapsacks):
    solver.Add(sum(x[p][k] - c[k] for p in range(num_pictures)) <= 0)

  # l have to hold last knapsack position only. You can only have it on the position when k is 1
  for k in range(num_knapsacks):
    solver.Add(l[k] - c[k] <= 0)

  # If you move by one and multiply it should be 0 (it should be on the position of rightmost 1)
  for k in range(num_knapsacks - 1):
    solver.Add(l[k] + c[k + 1] <= 1)

  # There is just one last knapsack
  solver.Add(sum(l[k] for k in range(num_knapsacks)) == 1)

  # And set z properly (simulate logical operation (l[j] and x[i][j]))
  for k in range(num_knapsacks):
    for p in range(num_pictures):
      solver.Add(1 - l[k] + z[p][k] <= 1)
      solver.Add(1 - x[p][k] + z[p][k] <= 1)
      solver.Add(x[p][k] + l[k] - z[p][k] <= 1)

  #
  # OBJECTIVE FUNCTION
  #

  knapsacks_used = []
  for k in range(num_knapsacks - 1):
    knapsacks_used.append(c[k + 1] * knapsacks[k])

  photo_sizes_in_last_knapsack = []
  for k in range(num_knapsacks):
    for p in range(num_pictures):
      photo_sizes_in_last_knapsack.append(z[p][k] * pictures[p])

  # Objective: Minimize the coefficients of each picture in each knapsack
  solver.Minimize(solver.Sum(knapsacks_used) + solver.Sum(photo_sizes_in_last_knapsack))

  start = time.time()
  # Run the solver
  status = solver.Solve()
  if status != pywraplp.Solver.OPTIMAL:
    fail_with("No optimal solution")
  print("Solve time:", time.time() - start, "seconds")

  # Compute list of pictures, grouped by their knapsack
  knaps = [[pictures[p] for p in range(num_pictures) if x[p][k].solution_value()] for k in range(num_knapsacks)]

  for k in range(num_knapsacks):
    print("Is used", c[k].name(), c[k].solution_value(), "  Is last", l[k].name(), l[k].solution_value())
    for p in range(num_pictures):
      print(z[p][k].name(), z[p][k].solution_value(), "  ", x[p][k].name(), x[p][k].solution_value())

  # Total time required to send all pictures
  last_full_knapsack = max(k for k in range(num_knapsacks) if knaps[k])
  total_time = blackouts[last_full_knapsack - 1][1] + sum(knaps[last_full_knapsack])

  return (knaps, total_time)

def main() -> None:
  input_path = "../data/big.txt"
  input = parse_input(input_path)
  (knaps, total_time) = solve(input)

  print("Pictures in knapsacks:", knaps)
  print("Total time:", total_time)

if __name__ == "__main__":
  main()
