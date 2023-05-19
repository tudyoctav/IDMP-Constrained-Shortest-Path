from pysat.solvers import Solver, Lingeling, Minisat22
from pysat.pb import PBEnc
from pysat import formula
from pysat.examples.fm import  FM
from typing import List, Tuple

def linear_search(constraints: formula.CNF, optim_func, solver: str="m22") -> Tuple[List[int], int]:
    model = None
    optim_val = -1
    with Solver(solver) as solver:
        # TODO should the assumptions be set somehow???
        while solver.solve():
            model = solver.get_model()
            optim_val, new_clause = optim_func(model)
            solver.append_formula(new_clause, False)
            print(solver.solve())

    return model, optim_val

def max_sat(constraints: formula.CNF, optim_literals: List[int], weights: List[int],  solver: Solver="m22") -> Tuple[List[int], int]:
    assert len(optim_literals) == len(weights), "the weights and literals should have the same length"
    wcnf = formula.WCNF()
    # Add original Hard clauses
    for clause in constraints:
        wcnf.append(clause)
    # Add soft clauses for optimization func
    for lit, weight in zip(optim_literals, weights):
        wcnf.append([-lit], weight)

    solv = FM(wcnf, solver=solver)
    if solv.compute():
        return solv.model, solv.cost
    else:
        return False