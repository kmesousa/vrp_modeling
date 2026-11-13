from itertools import combinations
from pulp import LpProblem, LpMinimize, LpBinary, lpSum       #   PuLP  4.0.1
from .. import register

from instance import Instance
from collections.abc import Callable

from typing import Literal

@register("dfj_3i", backend="pulp")
def build(inst:Instance, capacitated=True, subtour=True, exact_k=False, solver:Literal["pulp-cbc","gurobi"]="pulp-cbc") -> tuple[LpProblem, Callable[[], set[tuple]]]:

    n, K, Q = inst.n_clients, inst.k_vehicles, inst.capacity
    c, q = inst.dist, inst.demand       #custo das rotas (distancias), demanda dos clientes
    V, N, KS = range(n + 1), range(1, n + 1), range(K)  #conjuntos vertices, clientes, veículos

    prob = LpProblem("dfj_3i", LpMinimize)

    x = prob.add_variable_dicts("x", [(i, j, k) for k in KS for i in V for j in V if i != j], cat=LpBinary)          #variáveis de decisão

    prob += lpSum(c[i][j] * x[i, j, k] for (i, j, k) in x)      #função objetivo, custo da rota por estado da rota para cada rota + veículo

    for i in N:             #há exatamente uma saída em cada cliente
        prob += lpSum(x[i, j, k] for k in KS for j in V if j != i) == 1

    for k in KS:            #todos veículos usados devem sair do depósito
        saida = lpSum(x[0, j, k] for j in N)
        prob += (saida == 1) if exact_k else (saida <= 1)

        for h in V:         #entradas de um veículo em um cliente é igual a saídas
            prob += (lpSum(x[i, h, k] for i in V if i != h)
                     == lpSum(x[h, j, k] for j in V if j != h))

        if capacitated:     #demanda total dos clientes atendidos pelo veículo k deve ser menor ou igual à capacidade Q
            prob += lpSum(q[i] * x[i, j, k] for i in N for j in V if j != i) <= Q

    if subtour:             # DFJ explícito: 2^n - n - 1 restrições
        for r in range(2, n + 1):
            for S in combinations(N, r):
                prob += lpSum(x[i, j, k] for k in KS for i in S for j in S
                              if i != j) <= len(S) - 1

    def extract():
        '''returns the used arcs set'''
        return {(i, j) for (i, j, k), v in x.items() if v.value() > 0.5}
    return prob, extract