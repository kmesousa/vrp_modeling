import math
from functools import lru_cache
from itertools import combinations, permutations

from instance import Instance

def brute_force(inst: Instance):
    """Custo ótimo exato por enumeração; math.inf se a instância é infactível."""
    n, K, Q = inst.n_clients, inst.k_vehicles, inst.capacity
    d, q = inst.dist, inst.demand
    clients = range(1, n + 1)

    # melhor rota (testando todas as ordens) para cada subconjunto que cabe em Q
    best = {}
    for r in range(1, n + 1):
        for S in combinations(clients, r):
            if sum(q[i] for i in S) > Q:
                continue
            best[S] = min(
                d[0][p[0]] + sum(d[a][b] for a, b in zip(p, p[1:])) + d[p[-1]][0]
                for p in permutations(S)
            )

    @lru_cache(maxsize=None)
    def partition(remaining, k):
        if not remaining:
            return 0.0
        if k == 0:
            return math.inf
        first = min(remaining)
        rest = sorted(remaining - {first})
        res = math.inf
        for r in range(len(rest) + 1):
            for others in combinations(rest, r):
                S = (first,) + others
                if S in best:
                    res = min(res, best[S] + partition(remaining - frozenset(S), k - 1))
        return res

    return partition(frozenset(clients), K)