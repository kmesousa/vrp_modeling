import time, math
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from instance import Instance
from runConfig import RunConfig
from solution import Solution, arcs_to_routes
# importe Solution de onde ele vive no seu projeto

SCALE = 1000  # o OR-Tools exige custo inteiro: custo = round(dist * SCALE)

STATUS_DICT = {
    0: "NOT_SOLVED",
    1: "SUCCESS",
    2: "PARTIAL_SUCCESS_LOCAL_OPTIMUM_NOT_REACHED",
    3: "FAIL",
    4: "FAIL_TIMEOUT",
    5: "INVALID",
    6: "INFEASIBLE"
}

# -----------------------------------------------------------------------


def solve_routing(inst: Instance, config: RunConfig) -> "Solution":
    if config.heuristic is None:
        raise ValueError("solve_routing requer config.heuristic")
    if config.time_limit is None:
        # a metaheurística nunca termina sozinha
        raise ValueError("ortools-routing requer time_limit (não pode ser None)")

    t0 = time.perf_counter()

    dist = inst.dist
    demand = inst.demand
    n = len(dist)
    K = inst.k_vehicles
    Q = math.floor(inst.capacity)   # OR-Tools exige int

    scaled = [[int(round(d * SCALE)) for d in row] for row in dist]

    manager = pywrapcp.RoutingIndexManager(n, K, 0)
    routing = pywrapcp.RoutingModel(manager)

    if config.heuristic== "SWEEP" and not hasattr(routing, "SetSweepArranger"): #sweep  precisa das coordenadas, modelo só entrega a matrix de distâncias
            raise NotImplementedError("SWEEP não disponível nesta versão do OR-Tools")

    # if config.heuristic == "SWEEP":
    #     routing.SetSweepArranger(pywrapcp.SweepArranger([list(c) for c in inst.coords]))

    def dist_cb(i, j):
        return scaled[manager.IndexToNode(i)][manager.IndexToNode(j)]

    transit = routing.RegisterTransitCallback(dist_cb)
    routing.SetArcCostEvaluatorOfAllVehicles(transit)

    if config.options.capacitated:
        def demand_cb(i):
            return demand[manager.IndexToNode(i)]

        dem = routing.RegisterUnaryTransitCallback(demand_cb)
        routing.AddDimensionWithVehicleCapacity(dem, 0, [Q] * K, True, "Capacity")

    if config.options.exact_k:
        s = routing.solver()
        for v in range(K):
            s.Add(routing.NextVar(routing.Start(v)) != routing.End(v))

    h = config.heuristic
    p = pywrapcp.DefaultRoutingSearchParameters()
    p.first_solution_strategy = getattr(
        routing_enums_pb2.FirstSolutionStrategy, h.first_solution)
    p.local_search_metaheuristic = getattr(
        routing_enums_pb2.LocalSearchMetaheuristic, h.metaheuristic)
    p.time_limit.seconds = config.time_limit
    #p.log_search = True #mostra quando ocorreu a ultima melhora

    build_time = time.perf_counter() - t0

    t1 = time.perf_counter()
    sol = routing.SolveWithParameters(p)
    solve_time = time.perf_counter() - t1

    arcs: set = set()
    routes: list = []
    cost = None


    if sol is None:
        status = {3: "no_solution", 4: "timeout", 5: "invalid", 6: "infeasible"}.get(
            routing.status(), "failed")
    else:
        #status = STATUS_DICT[routing.status()].lower()
        status = STATUS_DICT.get(routing.status(), "unknow")
        for v in range(K):
            idx = routing.Start(v)
            nodes = [manager.IndexToNode(idx)]          # [0, ..., 0]
            while not routing.IsEnd(idx):
                idx = sol.Value(routing.NextVar(idx))
                nodes.append(manager.IndexToNode(idx))
            if len(nodes) > 2:                          # ignora veículo sem rota
                arcs.update(zip(nodes, nodes[1:]))

        routes = arcs_to_routes(arcs)
        cost = sum(dist[a][b] for a, b in arcs)         # custo real, sem escala

        # confere a extração: objetivo escalado do OR-Tools ≈ custo real
        # (cada arco arredonda no máximo 0.5/SCALE)
        if abs(sol.ObjectiveValue() / SCALE - cost) > len(arcs) * 0.5 / SCALE + 1e-9:
            raise RuntimeError("extração de rotas inconsistente com o objetivo do OR-Tools")

    return Solution(model=config.model, status=status, obj=cost, arcs=arcs, routes=routes,
    cost=cost, time=solve_time, build_time=build_time)