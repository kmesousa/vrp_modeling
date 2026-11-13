'''run config for solving a instance'''

from dataclasses import dataclass, field, fields, replace
from typing import Literal

@dataclass(frozen=True)
class ModelOptions:
    """Opções que mudam como o modelo é construído. [Os padrões moram só aqui. ] como assim? """
    objective: Literal["min-sum", "max-min"] = "min-sum"
    capacitated: bool = True
    subtour: bool = True
    exact_k: bool = False       # confira se bate com o padrão atual do seu build

    # def list_options(self) -> dict:
    #     return


# @dataclass(frozen=True)
# class ModelType:
#     hetero_capacity: bool = False
#     multi_depot: bool = False

@dataclass(frozen=True)
class RunConfig:
    '''Configurações de como o modelo será solucionado'''
    model: Literal["dfj_3i", "mtz_3i"]
    solver: Literal["pulp-cbc", "gurobi"] = "pulp-cbc"
    time_limit: int | None = 60
    '''em segundos, None = sem limite'''

    options: ModelOptions = field(default_factory=ModelOptions)

    def with_options(self, **kw) -> "RunConfig":
        """Cópia com algumas opções do modelo trocadas."""
        return replace(self, options=replace(self.options, **kw))

    def changed(self) -> dict:
        return {f.name: getattr(self, f.name)
                for f in fields(self)                                # type: ignore
                if getattr(self, f.name) != f.default}

    @property
    def name(self) -> str:
        """Nome legível: só mostra o que foge do padrão."""
        mudou = [f"{f.name}={getattr(self.options, f.name)}"
                 for f in fields(self.options)
                 if getattr(self.options, f.name) != f.default]
        return self.model + (" " + ", ".join(mudou) if mudou else "")