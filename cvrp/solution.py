from dataclasses import dataclass
from instance import Instance

@dataclass
class Solution:
    '''defines a format for solutions, model independent'''
    model: str
    status: str

    obj: float | None
    arcs: set
    routes: list
    cost: float | None

    time: float
    build_time: float | None = None

    gap: float | None = None
    bound: float | None = None


def arcs_to_routes(arcs):
    '''converts (x, y) arcs to n1, n2 ... routes '''
    succ, starts = {}, []
    for i, j in arcs:
        if i == 0:
            starts.append(j)
        else:
            succ[i] = j
    routes = []
    for s in starts:
        r = [s]
        while succ[r[-1]] != 0:
            r.append(succ[r[-1]])
        routes.append(r)
    return routes


def validate(inst: Instance, sol: Solution, capacitated=True) -> list[str | None]:
    """Devolve lista de erros; lista vazia = solução válida."""

    erros = []
    visitados = sorted(i for r in sol.routes for i in r)

    if visitados != list(range(1, inst.n_clients + 1)):
        erros.append("clientes não visitados ou repetidos (possível subciclo)")

    if len(sol.routes) > inst.k_vehicles:
        erros.append("mais rotas que veículos")

    if capacitated:
        for r in sol.routes:
            if sum(inst.demand[i] for i in r) > inst.capacity + 1e-9:
                erros.append(f"capacidade excedida na rota {r}")

    cobertos = {(a, b) for r in sol.routes
                for a, b in zip([0] + r, r + [0])}
    if sol.arcs - cobertos:
        erros.append("há arcos fora das rotas (subciclos)")

    if sol.obj is not None and sol.cost is not None and abs(sol.obj - sol.cost) > 1e-6:
        erros.append("objetivo do solver difere do custo recalculado")

    return erros