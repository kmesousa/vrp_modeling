'''instancias para cvrp'''

from dataclasses import dataclass
from typing import Any
from functools import cached_property
import math
import random

@dataclass
class Instance():
    '''instances for cvrp'''
    name: str
    coords: list[tuple[int, int]]      # índice 0 = depósito
    demand: list[int]                #  demand[0] = 0
    capacity: float
    k_vehicles: int
    n_clients: int
    slack: float
    seed: Any

    #furture #melhor ser uma class filha!!!
    #capacities: list[float] # for heteregenous fleat
    #depots: list [float, float] #for multidepot
    #k_from_depot: list[int] #de qual depot o veiculo k pertence

    def __post_init__(self):
        assert len(self.coords) == len(self.demand) == self.n_clients + 1

    @cached_property #"atributo" property calculado apenas uma vez, então guardado
    def dist(self):
        '''Return the (n+1) x (n+1) matrix of Euclidean distances between vertices.'''
        return [[math.hypot(xi - xj, yi - yj) for (xj, yj) in self.coords]
            for (xi, yi) in self.coords]

def random_instance(n: int, K:int, seed:Any=0, grid:int=100, max_demand:int=10, homogeneous:bool=True, slack:float=1.5):
    '''generate instance for N clients, K vehicles'''
    rng = random.Random(seed)

    coords = [(0,0)] + [(rng.randint(-grid, grid), rng.randint(-grid, grid))
                        for _ in range(n)]
    demand = [0] + [rng.randint(1, max_demand) for _ in range(n)]

    assert(len(coords) == len(demand) == n + 1)
    assert(demand[0] == 0 and coords[0] == (0,0))
    assert(max(demand) <= max_demand)

    if homogeneous:
        while True:
            capacity = max(math.ceil(slack * sum(demand) / K), max(demand)) #definir capacidade, maximo entre a maior demeanda e a demanda total / frota * slack

            if sum(demand) <= capacity*K: #garantir que a instancia seja factível
                break
    else:
        #capacities = [rng.random(math.ceil((rng.random(1, slack*2)) * sum(demand) / K), max.demand) for _ in range(k)]
        raise NotImplementedError

    #obs: se quiser que todos os veículos sejam usados (exact k), K <= n (fazer essa validação dps)

    return Instance(f"rand_n{n}_K{K}_s{seed}", coords, demand, capacity, K, n, slack, seed)

def make(n, K, seed):
    return random_instance(n, K, seed=seed)