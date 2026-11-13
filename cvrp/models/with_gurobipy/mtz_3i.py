from .. import register

from instance import Instance
from collections.abc import Callable

from typing import Literal

@register("mtz_3i", backend="gurobipy")
def build(inst: Instance, capacitated=True, subtour=True, exact_k=False, solver:Literal["pulp-cbc","gurobi"]="pulp-cbc") -> tuple[Callable[[], set[tuple]]]:

    n, K, Q = inst.n_clients, inst.k_vehicles, inst.capacity
    c, q = inst.dist, inst.demand       #custo das rotas (distancias), demanda dos clientes
    V, N, KS = range(n + 1), range(1, n + 1), range(K)  #conjuntos vertices, clientes, veículos


    def extract():
        '''returns the used arcs set'''
        pass
    return prob, extract