from pysat.solvers import Solver, Lingeling, Minisat22
from pysat.pb import PBEnc
from pysat import formula
from pysat.examples.fm import  FM
from typing import List, Tuple
from time import time

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

def max_sat(constraints: formula.CNF, optim_literals: List[int], weights: List[int],  solver: Solver="cadical153") -> Tuple[List[int], int]:
    assert len(optim_literals) == len(weights), "the weights and literals should have the same length"
    wcnf = formula.WCNF()
    # Add original Hard clauses
    for clause in constraints:
        wcnf.append(clause)
    # Add soft clauses for optimization func
    for lit, weight in zip(optim_literals, weights):
        wcnf.append([-lit], weight)
    print("Starting solver")
    solv = FM(wcnf, solver=solver)
    start_time = time()
    if solv.compute():
        print(f"% time elapsed: {time() - start_time}")
        return solv.model, solv.cost
    else:
        return None, None