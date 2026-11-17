import gurobipy as gp
from gurobipy import GRB

from .. import register

from instance import Instance
from runConfig import ModelOptions
from collections.abc import Callable

@register("mtz_3i", backend="gurobipy")
def build(inst: Instance, options: ModelOptions) -> tuple[gp.Model, Callable[[], set[tuple]]]:
    # options: o mesmo ModelOptions que o build do PuLP recebe (capacitated, subtour, exact_k)

    n, K, Q = inst.n_clients, inst.k_vehicles, inst.capacity
    c, q = inst.dist, inst.demand
    V, N, KS = range(n + 1), range(1, n + 1), range(K)

    m = gp.Model("mtz_3i")

    x = m.addVars([(i, j, k) for k in KS for i in V for j in V if i != j],
                  vtype=GRB.BINARY, name="x")

    m.setObjective(gp.quicksum(c[i][j] * x[i, j, k] for (i, j, k) in x), GRB.MINIMIZE)

    for i in N:             # há exatamente uma saída em cada cliente
        m.addConstr(gp.quicksum(x[i, j, k] for k in KS for j in V if j != i) == 1)

    for k in KS:            # todos veículos usados devem sair do depósito
        saida = gp.quicksum(x[0, j, k] for j in N)
        m.addConstr(saida == 1 if options.exact_k else saida <= 1)

        for h in V:         # entradas de um veículo em um nó = saídas
            m.addConstr(gp.quicksum(x[i, h, k] for i in V if i != h)
                        == gp.quicksum(x[h, j, k] for j in V if j != h))

        if options.capacitated:   # demanda atendida pelo veículo k <= Q
            m.addConstr(gp.quicksum(q[i] * x[i, j, k] for i in N for j in V if j != i) <= Q)

    if options.subtour:     # MTZ
        u = m.addVars(N, lb=1, ub=n, vtype=GRB.CONTINUOUS, name="u")
        for i in N:
            for j in N:
                if i != j:
                    m.addConstr(u[i] - u[j] + n * gp.quicksum(x[i, j, k] for k in KS) <= n - 1)

    def extract():
        '''returns the used arcs set (só chamar depois de otimizar, com solução)'''
        return {(i, j) for (i, j, k), v in x.items() if v.X > 0.5}

    return m, extract