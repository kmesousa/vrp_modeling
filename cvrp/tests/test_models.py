''''''
import pytest
import math
import matplotlib.pyplot as plt

from bruteforce import brute_force
from solve import solve
from instance import make
from plot import plot_solution
from solution import validate
from runConfig import RunConfig

MARGEM = 1e-4
CASOS = [(4, 2, 0), (5, 2, 1), (5, 3, 2), (6, 2, 3), (6, 3, 4), (7, 3, 5)]  # (n, K, seed)
MODELOS = ["dfj_3i", "mtz_3i"]

def otimo_ou_skip(inst):
    otimo = brute_force(inst)
    if math.isinf(otimo):
        pytest.skip("instância infactível (slack/demandas); troque a semente")
    return otimo

@pytest.mark.parametrize("model", MODELOS)
@pytest.mark.parametrize("n, K, seed", CASOS)
def test_modelo_bate_com_forca_bruta(n, K, seed, model):
    inst = make(n, K, seed)
    otimo = otimo_ou_skip(inst)
    sol = solve(inst, RunConfig(model))
    assert sol.obj is not None, f"sem solução, status: {sol.status}"
    assert validate(inst, sol) == []
    assert sol.cost == pytest.approx(otimo, abs=MARGEM)

@pytest.mark.parametrize("model", MODELOS)
@pytest.mark.parametrize("n, K, seed", CASOS)
def test_sem_subtour_nao_encarece(n, K, seed, model):
    inst = make(n, K, seed)
    otimo_ou_skip(inst)
    com = solve(inst, RunConfig(model))
    sem = solve(inst, RunConfig(model).with_options(subtour=False))
    if sem.cost and com.cost:
        assert sem.cost <= com.cost + MARGEM      # relaxar restrição nunca piora o ótimo


@pytest.mark.parametrize("model", MODELOS)
@pytest.mark.parametrize("n, K, seed", CASOS)
def test_sem_capacidade_nao_encarece(n, K, seed, model):
    inst = make(n, K, seed)
    otimo_ou_skip(inst)
    com = solve(inst, RunConfig(model))
    sem = solve(inst, RunConfig(model).with_options(capacitated=False))
    if sem.cost and com.cost:
        assert sem.cost <= com.cost + MARGEM      # relaxar restrição nunca piora o ótimo
    assert validate(inst, sem, capacitated=False) == []

@pytest.mark.parametrize("model", MODELOS)
@pytest.mark.parametrize("n, K, seed", CASOS) #FALHOU NESSE, TANTO COM MTZ QUANTO DFJ, PQ E O Q ISSO IMPLICA?
def test_exact_k_usa_todos_os_veiculos(n, K, seed, model):
    inst = make(n, K, seed)
    otimo = otimo_ou_skip(inst)
    sol = solve(inst, RunConfig(model).with_options(exact_k=True))
    assert len(sol.routes) == K
    assert validate(inst, sol) == []
    if sol.cost:
        assert sol.cost >= otimo - MARGEM         # forçar K rotas não pode ser melhor


def test_gerador_reproduzivel():
    a, b = make(6, 2, 7), make(6, 2, 7)
    assert a.coords == b.coords and a.demand == b.demand and a.capacity == b.capacity


# def test_plot_nao_quebra(tmp_path): #refazer plot
#     plt.switch_backend("Agg")              # sem abrir janela
#     inst = make(5, 2, 1)
#     otimo_ou_skip(inst)
#     for opts in [True, False]:  # com e sem subciclos
#         sol = solve(inst, RunConfig("dfj_3i").with_options(subtour=opts))
#         ax = plot_solution(inst, sol)
#         arq = tmp_path / f"rotas_{opts}.png"
#         ax.figure.savefig(arq) # type: ignore
#         plt.close(ax.figure)  # type: ignore
#         assert arq.stat().st_size > 0