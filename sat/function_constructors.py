import heapq
from pysat.pb import PBEnc
from pysat.formula import IDPool
from typing import List

def sum(literals: List[int], id_pool: IDPool) -> int:
    literals = set(literals.copy())
    def res(model: list[int]):
        total = 0
        for lit in model:
            if lit < 0:
                continue
            if lit in literals:
                total += 1

        return total, PBEnc.atmost(literals, bound=total - 1, vpool=id_pool).clauses
    return res


def linear(literals: List[int], weights: List[int], id_pool: IDPool):
    lit_weights_dict = dict()
    for lit, weight in zip(literals, weights):
        lit_weights_dict[lit] = weight
    def res(model):
        total = 0
        for lit in model:
            if lit < 0:
                continue
            weight = lit_weights_dict.get(lit, 0)
            total += weight
        # TODO Should probably reuse vars
        return total, PBEnc.atmost(literals, weights, total - 1, vpool=id_pool).clauses
    return res