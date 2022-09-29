from ortools.linear_solver import pywraplp # type: ignore
from random import randint, uniform

def bool_array_gen(solver, n, m):
  return [[solver.BoolVar(f"x[{i}][{j}]") for j in range(m)] for i in range(n)]

# LP solver
# (BOP) is the algorithm I picked one in a tutorial might not be the right one for our usecase
solver = pywraplp.Solver.CreateSolver('SCIP') or exit(1)

# Input
p = [round(uniform(1, 10), 2) for _ in range(50)]
c = [round(uniform(1, 20), 2) for _ in range(50)]
n = len(p)
m = len(c)

# Variable
x = bool_array_gen(solver, n, m)

# Constraints
for j in range(m):
  solver.Add(solver.Sum([p[i] * x[i][j] for i in range(n)]) <= c[j])

for i in range(n):
  solver.Add(solver.Sum(x[i][j] for j in range(m)) == 1)

# Objective
solver.Minimize(solver.Sum(x[i][j] * p[i] * j * j for j in range(m) for i in range(n)))

# Output
status = solver.Solve()
if status == pywraplp.Solver.OPTIMAL:
    o = []
    for j in range(m):
        l = []
        for i in range(n):
            # print(f"x[{i}][{j}]: {x[i][j].solution_value()}")

            if x[i][j].solution_value():
                l.append(p[i])
        o.append(l)
    print(o)
else:
    print('The problem does not have an optimal solution.')
