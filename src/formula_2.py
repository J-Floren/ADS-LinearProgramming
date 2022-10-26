#from more_itertools import pairwise
from itertools import pairwise   # must have python 3.10 for this to work

from ortools.linear_solver import pywraplp # type: ignore
from sys import argv
from typing import NoReturn
import timeit

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

    #print("Pictures:", pictures)
    #print("Blackouts:", blackouts)

    return (pictures, blackouts)

# Turn a list of blackouts into a list of knapsacks.
def get_knapsacks(pictures: list[float], blackouts: list[Blackout]) -> list[float]:
  knaps = [blackouts[0][0]] + [start - end for ((_, end), (start, _)) in pairwise(blackouts)] + [sum(pictures)]
  return [round(k, 3) for k in knaps]

Output = tuple[float, list[float], float, int, int, int]

def solve(input: Input) -> Output:
  (pictures, blackouts) = input
  num_pictures = len(pictures)
  num_blackouts = len(blackouts)

  if not pictures or not blackouts:
    fail_with("Trivial solution")

  knapsacks = get_knapsacks(pictures, blackouts)
  num_knapsacks = len(knapsacks)
  print("Knapsacks:", knapsacks)
  #print()

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

  start = timeit.default_timer()
  # Run the solver
  status = solver.Solve()
  if status != pywraplp.Solver.OPTIMAL:
    fail_with("No optimal solution")
  solve_time = timeit.default_timer() - start
  #print("Solve time:", time.time() - start, "seconds")

  # Compute list of pictures, grouped by their knapsack
  knaps = [[p for p in range(num_pictures) if x[p][k].solution_value()] for k in range(num_knapsacks)]
  print("Pictures in knapsacks:", knaps)
  filled = []

  for i in range(len(knaps)):
      diff = knapsacks[i] - sum(knaps[i])
      if len(knaps[i]) == 0 or diff > 0:
          filled.append(False)
      else:
          filled.append(True)

  num_full_knaps = sum(1 for i in filled if i)
  num_used_knaps = max([i for i in range(num_knapsacks) if len(knaps[i]) > 0])


  '''
  # Output all variables
  for k in range(num_knapsacks):
    print("Is used", c[k].name(), c[k].solution_value(), "  Is last", l[k].name(), l[k].solution_value())
    for p in range(num_pictures):
      print(z[p][k].name(), z[p][k].solution_value(), "  ", x[p][k].name(), x[p][k].solution_value())
  '''

  # Total time required to send all pictures
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

  return (total_time, times, solve_time, num_full_knaps, num_used_knaps, num_knapsacks)

def main(input_path):
  input = parse_input(input_path)
  (total_time, times, solve_time, num_full_knaps, num_used_knaps, num_knapsacks) = solve(input)

  #print("Total time:", total_time)
  #print("Sending times:", times)

  return (solve_time, total_time, num_full_knaps, num_used_knaps, num_knapsacks)

if __name__ == "__main__":
  INSTANCE_PATH = argv[1]
  #INSTANCE_PATH = "../../experiment_instances/11_2.txt"

  main(INSTANCE_PATH)
