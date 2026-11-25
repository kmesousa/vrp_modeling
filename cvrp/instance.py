'''instancias para cvrp'''

from dataclasses import dataclass
from typing import Any, Literal
from functools import cached_property
import math, random, re
from pathlib import Path

@dataclass
class Instance():
    '''instances for cvrp'''
    name: str
    coords: list[tuple[int, int]]      # índice 0 = depósito
    demand: list[int]                #  demand[0] = 0
    capacity: float
    k_vehicles: int
    n_clients: int
    slack: float | None
    seed: Any
    rounded: bool = True               # True = convenção TSPLIB/CVRPLIB (EUC_2D)
    known_best: float | None = None         #otimos encontrados, para instâncias do cvrplib

    #depot_position: Literal["center", "corner", "random"] = "center"

    #furture #melhor ser uma class filha!!!
    #capacities: list[float] # for heteregenous fleat
    #depots: list [float, float] #for multidepot
    #k_from_depot: list[int] #de qual depot o veiculo k pertence

    def __post_init__(self):
        assert len(self.coords) == len(self.demand) == self.n_clients + 1

    @cached_property #"atributo" property calculado apenas uma vez, então guardado
    def dist(self):
        '''(n+1) x (n+1) matrix of Euclidean distances between vertices.'''
        def d(a, b):
            h = math.hypot(a[0] - b[0], a[1] - b[1])
            return int(h + 0.5) if self.rounded else h
        return [[d(a, b) for b in self.coords] for a in self.coords]

def random_instance(n: int, K:int, seed:Any=0, grid:int=100, max_demand:int=10, homogeneous:bool=True, slack:float=1.5):
    '''generate instance for N clients, K vehicles'''
    rng = random.Random(seed)

    coords = [(0,0)] + [(rng.randint(-grid, grid), rng.randint(-grid, grid))
                        for _ in range(n)]
    demand = [0] + [rng.randint(1, max_demand) for _ in range(n)]

    assert(len(coords) == len(demand) == n + 1)
    assert(demand[0] == 0) #depósito não tem demanda
    assert(coords[0] == (0,0)) #depósito sempre está na posição 0,0    não precisa ser obrigatório, posso fazer opções de instancias com depósito no centro, borda ou aleatório, e usar o assert só quando for no centro ou borda
    assert(max(demand) <= max_demand)

    if homogeneous:
        capacity = max(math.ceil(slack * sum(demand) / K), max(demand)) #definir capacidade, maximo entre a maior demeanda e a demanda total / frota * slack

        assert sum(demand) <= capacity*K #garantir que a instancia seja factível

    else:
        #capacities = [rng.random(math.ceil((rng.random(1, slack*2)) * sum(demand) / K), max.demand) for _ in range(k)]
        raise NotImplementedError

    return Instance(f"rand_n{n}_K{K}_s{seed}", coords, demand, capacity, K, n, slack, seed)

def make(n, K, seed):
    return random_instance(n, K, seed=seed)


#         INSTANCIAS DO CVRPLIB

def read_vrplib(path) -> dict:
    '''Lê um arquivo .vrp do CVRPLIB e devolve um dict com os dados crus.'''
    header, coords, demand, depots = {}, {}, {}, []
    section = None

    for raw in Path(path).read_text().splitlines():
        line = raw.strip()
        if not line or line == "EOF":
            continue

        if line.endswith("_SECTION"):
            section = line
            continue

        if section is None:                          # cabeçalho "CHAVE : valor"
            key, _, val = line.partition(":")
            header[key.strip()] = val.strip()
        elif section == "NODE_COORD_SECTION":
            i, x, y = line.split()[:3]
            coords[int(i)] = (float(x), float(y))
        elif section == "DEMAND_SECTION":
            i, d = line.split()[:2]
            demand[int(i)] = int(d)
        elif section == "DEPOT_SECTION":
            v = int(line.split()[0])
            if v != -1:
                depots.append(v)

    return {"header": header, "coords": coords, "demand": demand, "depots": depots}

def parse_known_best(header):
    '''Extrai o valor ótimo/melhor conhecido do COMMENT, ou None se não houver.'''
    comment = header.get("COMMENT")
    if not comment:                                   # sem chave ou vazio
        return None

    try:                                              # COMMENT : 16212.74
        return float(comment)
    except ValueError:
        pass

    m = re.search(r"optimal value:\s*(\d+(?:\.\d+)?)", comment, re.IGNORECASE)
    return float(m.group(1)) if m else None           # (... Optimal value: 784)

def from_vrplib(path, rounded=True):
    '''Cria uma Instance a partir de um arquivo .vrp do CVRPLIB.'''
    raw = read_vrplib(path)
    h = raw["header"]

    assert h.get("TYPE") == "CVRP", f"TYPE inesperado: {h.get('TYPE')}"
    assert h.get("EDGE_WEIGHT_TYPE") == "EUC_2D", "só EUC_2D é suportado"
    assert raw["depots"] == [1], "esperado um único depósito no nó 1"

    n_nodes = int(h["DIMENSION"])
    ids = range(1, n_nodes + 1)                      # ids do arquivo começam em 1
    coords = [raw["coords"][i] for i in ids]         # índice 0 = depósito
    demand = [raw["demand"][i] for i in ids]
    assert demand[0] == 0

    name = h["NAME"]
    capacity = int(h["CAPACITY"])

    # K: primeiro tenta o nome (A-n32-k5), depois o comentário (No of trucks: 5)
    m = re.search(r"-k(\d+)", name) or re.search(r"trucks:\s*(\d+)", h.get("COMMENT", ""))
    if m is None:
        raise ValueError(f"não consegui extrair K de {name!r}")
    k = int(m.group(1))

    # inverso de: capacity = max(ceil(slack * sum(demand) / K), max(demand))
    slack = capacity * k / sum(demand)

    known_best = parse_known_best(header=h)

    return Instance(
        name=name,
        coords=coords,
        demand=demand,
        capacity=capacity,
        k_vehicles=k,
        n_clients=n_nodes - 1,
        slack=slack,
        seed=None,
        rounded=rounded,
        known_best=known_best,
    )

assert(parse_known_best({"COMMENT": "(Augerat et al, No of trucks: 5, Optimal value: 784)"})==784)
assert(parse_known_best({"COMMENT": "16212.74"})==16212.74)
assert(parse_known_best({"as": 100})==None)