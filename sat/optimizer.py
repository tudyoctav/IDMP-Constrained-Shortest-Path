from pysat.solvers import Solver, Lingeling, Minisat22
from pysat.pb import PBEnc
from pysat import formula
from typing import List, Tuple

def linear_search(constraints: formula.CNF, optim_func, solver: Solver=Minisat22) -> Tuple[List[int], int]:
    model = None
    optim_val = -1
    with solver(constraints) as solver:
        # TODO should the assumptions be set somehow???
        while solver.solve():
            model = solver.get_model()
            optim_val, new_clause = optim_func(model)
            solver.append_formula(new_clause, False)
            print(solver.solve())

    return model, optim_val