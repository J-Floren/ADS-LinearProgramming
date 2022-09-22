def bool_array_gen(solver, _n, _m):
    _x = []
    for _i in range(_n):
        _x.append([])
        for _j in range(_m):
            _x[_i].append(solver.BoolVar('x[%i][%i]' % (_i, _j)))
    return _x


def get_max(array):
    i = -1
    for a in array:
        if a > i:
            i = a
    return a
