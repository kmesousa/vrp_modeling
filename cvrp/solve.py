import time
import pulp

from exact_methods import get_builder
from heuristics.ortools_routing import solve_routing

from instance import Instance
from runConfig import RunConfig
from solution import Solution, arcs_to_routes

GRB_STATUS = { #para nao precisar importar o gurobi e continuar rodando em maquinas sem ele instalado
    2: "Optimal",      # GRB.OPTIMAL
    3: "Infeasible",   # GRB.INFEASIBLE
    4: "Infeasible or Unbounded",  # GRB.INF_OR_UNBD
    5: "Unbounded",    # GRB.UNBOUNDED
    9: "Time limit",   # GRB.TIME_LIMIT
}

def solve(inst: Instance, config: RunConfig, msg: bool = False) -> Solution:
    """Build the chosen model, solve it with the chosen solver, return a Solution."""
    if config.options.exact_k and inst.k_vehicles > inst.n_clients:
        raise ValueError (f"k exato requer k <= n (k={inst.k_vehicles}, n={inst.n_clients})")

    if config.solver == "ortools-routing":
        return solve_routing(inst, config)

    build = get_builder(config.model, config.solver)

    t0 = time.perf_counter()
    model, extract = build(inst, config.options)
    if config.solver == "gurobipy":
        model.update()               # senão o tempo de construção cai dentro do optimize()
    build_time = time.perf_counter() - t0

    bound = gap = None
    t0 = time.perf_counter()

    if config.solver == "pulp-cbc":
        stats = model.solve(pulp.COIN_CMD(msg=msg, timeLimit=config.time_limit))
        has_solution, status, obj = stats.has_solution, stats.status_str, stats.objective

    elif config.solver == "pulp-gurobi":
        stats = model.solve(pulp.GUROBI(msg=msg, timeLimit=config.time_limit))
        has_solution, status, obj = stats.has_solution, stats.status_str, stats.objective
        if has_solution:
            gm = model.solverModel   # o gp.Model que o PuLP criou por baixo
            bound, gap = gm.ObjBound, gm.MIPGap

    elif config.solver == "gurobipy":
        from gurobipy import GRB
        model.Params.OutputFlag = int(msg)
        model.Params.TimeLimit = config.time_limit
        model.optimize()
        has_solution = model.SolCount > 0
        status = GRB_STATUS.get(model.Status, f"status_{model.Status}")
        obj = model.ObjVal if has_solution else None
        if has_solution:
            bound, gap = model.ObjBound, model.MIPGap

    else:
        raise NotImplementedError(f"solver {config.solver!r} desconhecido")

    elapsed = time.perf_counter() - t0

    if has_solution:
        arcs = extract()
        cost = sum(inst.dist[i][j] for i, j in arcs)
    else:
        arcs, obj, cost = set(), None, None

    return Solution(config.model, status, obj, arcs, arcs_to_routes(arcs),
                    cost, elapsed, build_time, bound=bound, gap=gap)