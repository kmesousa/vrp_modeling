import time
from typing import Literal

import pulp

from models import REGISTRY, get_builder
from instance import Instance
from runConfig import RunConfig
from solution import Solution, arcs_to_routes

#region solve antigo, sem runconfig
# def solve(inst: Instance, model: str, time_limit: int = 60,
#           msg: bool = False, **opts) -> Solution:
#     """Build the chosen model, solve it with CBC and return a Solution."""

#     prob, extract = REGISTRY[model](inst, **opts)

#     t0 = time.perf_counter()
#     stats = prob.solve(pulp.COIN_CMD(msg=msg, timeLimit=time_limit))
#     elapsed = time.perf_counter() - t0

#     # has_solution cobre "ótimo" e também "parou no limite de tempo com solução"
#     if stats.has_solution:
#         arcs = extract()
#         obj = stats.objective
#     else:
#         arcs, obj = set(), None

#     cost = sum(inst.dist[i][j] for i, j in arcs)
#     return Solution(model, stats.status_str, obj, arcs,
#                     arcs_to_routes(arcs), cost, elapsed)
#endregion

def solve(inst: Instance, config:RunConfig, msg: bool = False) -> Solution:
    """Build the chosen model, solve it with CBC and return a Solution."""

    if config.solver != "pulp-cbc":
        raise NotImplementedError(f"solver {config.solver!r} ainda não implementado")

    if config.solver == "pulp-cbc":

        t0 = time.perf_counter()
        prob, extract = REGISTRY[config.model](inst, config.options)
        build_time = time.perf_counter() - t0

        t0 = time.perf_counter()
        stats = prob.solve(pulp.COIN_CMD(msg=msg, timeLimit=config.time_limit))
        elapsed = time.perf_counter() - t0

        # has_solution cobre "ótimo" e também "parou no limite de tempo com solução"
        if stats.has_solution:
            arcs = extract()
            obj = stats.objective
            cost = sum(inst.dist[i][j] for i, j in arcs)
        else:
            arcs, obj, cost = set(), None, None

        status = stats.status_str
        gap = None
        bound = None

    return Solution(config.model, status, obj, arcs,
                    arcs_to_routes(arcs), cost, elapsed, build_time, gap, bound)