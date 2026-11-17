'''run config for solving a instance'''

from dataclasses import dataclass, field, fields, replace, MISSING
from typing import Literal

@dataclass(frozen=True)
class ModelOptions:
    """Opções que mudam como o modelo é construído. [Os padrões moram só aqui. ] como assim? """
    objective: Literal["min-sum", "max-min"] = "min-sum"
    capacitated: bool = True
    subtour: bool = True
    exact_k: bool = False       # confira se bate com o padrão atual do seu build


@dataclass(frozen=True)
class HeuristicOptions:
    '''Opções para solução com heurísitcas'''
    first_solution: Literal["SAVINGS"] = "SAVINGS"
    metaheuristic: Literal["GUIDED_LOCAL_SEARCH"] = "GUIDED_LOCAL_SEARCH"

# @dataclass(frozen=True)        # também precisaria q a instancia seja adequada, então não sei se guardaria aqui, a menos q use instancias mais completas, com todas as informações, mesmo que alguns dados fossem ser ignorados
# class ModelType:
#     hetero_capacity: bool = False
#     multi_depot: bool = False

@dataclass(frozen=True)
class RunConfig:
    '''Configurações de como o modelo será solucionado'''
    model: Literal["dfj_3i", "mtz_3i", "routing"] = "mtz_3i"
    solver: Literal["pulp-cbc","pulp-gurobi", "gurobipy", "ortools-routing"] = "pulp-cbc"
    time_limit: int | None = 60
    '''em segundos, None = sem limite'''

    options: ModelOptions = field(default_factory=ModelOptions)
    heuristic: HeuristicOptions | None = None

    def with_options(self, **kw) -> "RunConfig":
        """Cópia com algumas opções do modelo trocadas."""
        return replace(self, options=replace(self.options, **kw))

    def with_heuristic(self, **kw) -> "RunConfig":
        """Cópia com opções da heurística trocadas (parte do padrão se ainda não havia)."""
        base = self.heuristic or HeuristicOptions()
        return replace(self, heuristic=replace(base, **kw))

    def changed(self) -> dict:
        def _default(f):
                return f.default_factory() if f.default_factory is not MISSING else f.default
        return {f.name: getattr(self, f.name)
                for f in fields(self)                                # type: ignore
                if getattr(self, f.name) != _default(f)}

    @property
    def name(self) -> str:
        """Nome legível: só mostra o que foge do padrão."""
        mudou = [f"{f.name}={getattr(self.options, f.name)}"
             for f in fields(self.options)
             if getattr(self.options, f.name) != f.default]
        if self.heuristic is not None:
            mudou += [f"{f.name}={getattr(self.heuristic, f.name)}"
                    for f in fields(self.heuristic)
                    if getattr(self.heuristic, f.name) != f.default]
        return self.model + (" " + ", ".join(mudou) if mudou else "")

    def __post_init__(self):
        routing = self.solver == "ortools-routing"
        if routing and self.heuristic is None:
            # dataclass frozen: precisa do object.__setattr__ dentro do __post_init__
            object.__setattr__(self, "heuristic", HeuristicOptions())
        if not routing and self.heuristic is not None:
            raise ValueError("heuristic só é válido com solver='ortools-routing'")
        if routing != (self.model == "routing"):
            raise ValueError("model='routing' e solver='ortools-routing' andam juntos")