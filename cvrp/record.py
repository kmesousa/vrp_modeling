from dataclasses import asdict

from instance import Instance
from runConfig import RunConfig
from solution import Solution

def to_record (inst:Instance, config: RunConfig, sol:Solution, errors:list[str | None] | list[str] | None = None, error=None) -> dict:
    return {
        # --- instância ---
        "name": inst.name,
        "n": inst.n_clients,
        "k": inst.k_vehicles,
        "q": inst.capacity,
        "seed": inst.seed,
        "slack": inst.slack,

        # --- config: campos fixos ---
        "model": config.model,
        "solver": config.solver,
        "time_limit": config.time_limit,

        # --- config: opções do modelo (dinâmico, uma coluna por opção) ---
        **asdict(config.options),

        # --- config: opções de heuristicas ---
        "heuristic": True if config.heuristic else False,
        "first_solution": config.heuristic.first_solution if config.heuristic else None,
        "metaheuristic": config.heuristic.metaheuristic if config.heuristic else None,

        # --- resultado do solver ---
        "status": sol.status,
        "obj": sol.obj,                  # None se não houve solução
        "cost": sol.cost,                # None se não houve solução
        "time": sol.time,                # só a resolução
        "build_time": sol.build_time,    # só a construção do modelo
        "n_routes": len(sol.routes),
        "gap": sol.gap,                  # None se o solver não informar
        "bound": sol.bound,              # None se o solver não informar

        # --- conferência ---
        "validate_errors": None if errors is None else len(errors),
        "error": error,                  # mensagem da exceção, None se tudo certo
    }