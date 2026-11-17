from typing import Callable, TypeVar, Any

REGISTRY: dict[tuple[str, str], Callable] = {}

# qual backend (pasta/API) cada solver usa
BACKEND_OF = {
    "pulp-cbc": "pulp",
    "pulp-gurobi": "pulp",   # mesmo build do PuLP, só muda o solver no solve()
    "gurobipy": "gurobipy",
}

def register(name: str, backend: str):
    def deco(fn):
        REGISTRY[(name, backend)] = fn
        return fn
    return deco

def get_builder(name: str, solver: str) -> Callable:
    try:
        backend = BACKEND_OF[solver]
    except KeyError:
        raise ValueError(f"solver {solver!r} sem backend; válidos: {list(BACKEND_OF)}") from None
    try:
        return REGISTRY[(name, backend)]
    except KeyError:
        raise NotImplementedError(
            f"formulação {name!r} não implementada para o solver {solver!r}"
        ) from None

# IMPORTS NO FINAL: register já existe aqui, e importar o módulo dispara o @register
import exact_methods.with_pulp.mtz_3i  # noqa: F401
import exact_methods.with_pulp.dfj_3i  # noqa: F401
try:
    import exact_methods.with_gurobipy.mtz_3i  # noqa: F401
except ModuleNotFoundError as e:
    if e.name != "gurobipy":    # só tolera a falta do gurobipy
        raise