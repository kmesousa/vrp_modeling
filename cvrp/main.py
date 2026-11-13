from instance import make
from plot import plot_solution
from solution import validate
from solve import solve
from runConfig import RunConfig
from record import to_record
from experiment import run_experiment, export_readable

from typing import Literal
from datetime import datetime
STAMP = datetime.now().strftime("%Y%m%d_%H%M")

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
    nome_arquivo = f"results/seeds_{STAMP}"
    return insts, cfgs, nome_arquivo

# 2) mesma instância, vários métodos
def mesma_instancia_varios_metodos (n, k, s=0, timeLimit=3600) :
    insts = [make(12, 3, 0)]
    cfgs = [RunConfig("dfj_3i", time_limit=timeLimit), RunConfig("mtz_3i", time_limit=timeLimit)]
    nome_arquivo = f"results/metodos_{STAMP}"
    return insts, cfgs, nome_arquivo

# 3) mesmo método, vários tamanhos (K fixo)
def mesmo_metodo_varios_tamanhos (ni, nf, paso=5, s=0, timeLimit=3600, modelo:Literal["mtz_3i", "dfj_3i"]="mtz_3i") :
    insts = [make(n, int(n/3)+2, s) for n in range(ni, nf+1, paso)]
    cfgs = [RunConfig(modelo, time_limit=timeLimit)]
    nome_arquivo = f"results/instancias_{STAMP}"
    return insts, cfgs, nome_arquivo

'''

'''

# variação de opção:
# RunConfig("mtz_3i").with_options(subtour=False)

def run (insts, ctfgs, nome_arquivo):
    run_experiment(insts, ctfgs, f"{nome_arquivo}.jsonl")
    export_readable(f"{nome_arquivo}.jsonl", f"{nome_arquivo}_formatado.jsonl")

def main ():
    pass

    run(*mesmo_metodo_varios_tamanhos(5, 15, timeLimit=60, modelo="mtz_3i"))
    #run(*mesmo_metodo_varios_tamanhos(5,20, modelo="dfj_3i"))



if __name__ == "__main__":
    main()