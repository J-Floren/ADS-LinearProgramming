from ortools.linear_solver import pywraplp
from utils import *

# LP solver
solver = pywraplp.Solver.CreateSolver('BOP')
if not solver:
    exit()

# Input
p = [5, 4, 2, 2]
c = [6, 4, 10]
n = len(p)
m = len(c)

c_max = get_max(c)

# Variable
x = bool_array_gen(solver, n, m)

# Constraints
for j in range(m):
    solver.Add(solver.Sum([p[i] * x[i][j] for i in range(n)]) <= c[j])

for i in range(n):
    solver.Add(solver.Sum(x[i][j] for j in range(m)) == 1)

# Objective
solver.Minimize(solver.Sum(x[i][j] * p[i] * (j * j) for j in range(m) for i in range(n)))


# Output
status = solver.Solve()
if status == pywraplp.Solver.OPTIMAL:
    o = []
    for j in range(m):
        o.append([])
        for i in range(n):
            print('x[%i][%i]: %i' % (i, j, x[i][j].solution_value()))
            if x[i][j].solution_value():
                o[j].append(p[i])
    print(o)
else:
    print('The problem does not have an optimal solution.')
