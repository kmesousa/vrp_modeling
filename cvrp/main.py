from instance import make, from_vrplib, read_vrplib, parse_known_best
from plot import plot_solution
from runConfig import RunConfig, first_solution_opts, metaheuristic_opts
from experiment import run_experiment, export_readable

from typing import Literal, get_args
from datetime import datetime

STAMP = datetime.now().strftime("%Y%m%d_%H%M")

SOLVERS = Literal["pulp-cbc","pulp-gurobi", "gurobipy", "ortools-routing"]
MODELS = Literal["dfj_3i", "mtz_3i", "routing"]


VARIANTES = [
    ("com DFJ e capacidade", {}),
    ("sem DFJ", {"subtour": False}),
    ("sem capacidade", {"capacitated": False}),
    ("sem capacidade, K rotas fixas", {"capacitated": False, "exact_k": True}),
    ("com capacidade, K rotas fixas, sem DFJ", {"subtour":False, "exact_k":True})
]
'''casos de teste'''

# inst = make(5, 3, 0)
# rcfg = RunConfig("dfj_3i").with_options(subtour = False)
# sol = solve(inst, rcfg)
# sol = solve(inst, RunConfig("dfj_3i").with_options(subtour=False))

# print(rcfg.options)
# print(sol)

# 1) mesmo (n, K), várias seeds, mesmo método
def mesmo_nk_varias_seeds (n, k, si=0, sn=5, timeLimit=3600) :

    insts = [make(n, k, s) for s in range(si, sn)]
    cfgs = [RunConfig("mtz_3i", time_limit=timeLimit)]
    nome_arquivo = f"seeds_{STAMP}"
    return insts, cfgs, nome_arquivo

# 2) mesma instância, vários métodos
def mesma_instancia_varios_metodos (n, k, s=0, timeLimit=3600) :
    insts = [make(12, 3, 0)]
    cfgs = [RunConfig("dfj_3i", time_limit=timeLimit), RunConfig("mtz_3i", time_limit=timeLimit)]
    nome_arquivo = f"metodos_{STAMP}"
    return insts, cfgs, nome_arquivo

# 3) mesmo método, vários tamanhos (K fixo)
def mesmo_metodo_varios_tamanhos (ni, nf, paso=5, s=0, timeLimit=3600, modelo:MODELS="mtz_3i", solver:SOLVERS="pulp-cbc", nome_arquivo:str="instancias_") :
    insts = [make(n, int(n/3)+2, s) for n in range(ni, nf+1, paso)]
    cfgs = [RunConfig(modelo, time_limit=timeLimit, solver=solver)]
    #nome_arquivo = f"results/instancias_{STAMP}"
    return insts, cfgs, f"{nome_arquivo}_{STAMP}"

'''

'''

# variação de opção:
# RunConfig("mtz_3i").with_options(subtour=False)

def run (insts, ctfgs, nome_arquivo):
    run_experiment(insts, ctfgs, f"results/{nome_arquivo}.jsonl")
    export_readable(f"results/{nome_arquivo}.jsonl", f"results/{nome_arquivo}_formatado.jsonl")

def main ():
    pass

    #run(*mesmo_metodo_varios_tamanhos(5, 15, timeLimit=60, modelo="mtz_3i"))
    #run(*mesmo_metodo_varios_tamanhos(5,20, modelo="dfj_3i"))
    if False:
        run_experiment([make(7,4,0)], [RunConfig("mtz_3i", solver="pulp-cbc")], "test_solvers.jsonl" )
        run_experiment([make(7,4,0)], [RunConfig("mtz_3i", solver="pulp-gurobi")], "test_solvers.jsonl" )
        run_experiment([make(7,4,0)], [RunConfig("mtz_3i", solver="gurobipy")], "test_solvers.jsonl" )

    cfg = RunConfig(model="routing", solver="ortools-routing", time_limit=60*5).with_heuristic(first_solution="SAVINGS", metaheuristic="GUIDED_LOCAL_SEARCH")

    # run(*mesmo_metodo_varios_tamanhos(5,10,paso=2, solver="gurobipy" ,modelo="mtz_3i", nome_arquivo="gurobipy_n5_n10"))

    cvrplib = ["cvrplib/A-n32-k5.vrp", "cvrplib/A-n80-k10.vrp", "cvrplib/M-n101-k10.vrp"]
    insts = [from_vrplib(i) for i in cvrplib]

    configs_all_heuristics = [RunConfig(model="routing", solver="ortools-routing", time_limit=30).with_heuristic(first_solution=heu, metaheuristic=metaheu) for heu in get_args(first_solution_opts) for metaheu in get_args(metaheuristic_opts)]

    run(insts, configs_all_heuristics, "teste04_heuristicas_variadas")

if __name__ == "__main__":
    main()