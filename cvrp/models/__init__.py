from typing import Callable, TypeVar, Any

# from .with_pulp import dfj_3i

# # PULP           4.0.1
# # GUROBI         13.0.3

# F = TypeVar("F", bound=Callable)

# REGISTRY:dict[str, Any] = {}

# def register(name:str) -> Callable[[F], F]:
#     '''register vrp models'''
#     def deco(fn: F) -> F:
#         REGISTRY[name] = fn
#         return fn
#     return deco

# from .with_pulp import mtz_3i

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
    backend = BACKEND_OF[solver]
    try:
        return REGISTRY[(name, backend)]
    except KeyError:
        raise NotImplementedError(
            f"formulação {name!r} não implementada para o solver {solver!r}"
        ) from None

# IMPORTS NO FINAL: register já existe aqui, e importar o módulo dispara o @register
import models.with_pulp.mtz_3i  # noqa: F401
import models.with_pulp.dfj_3i  # noqa: F401
try:
    import models.with_gurobipy.mtz_3i  # noqa: F401
except ModuleNotFoundError as e:
    if e.name != "gurobipy":    # só tolera a falta do gurobipy
        raise