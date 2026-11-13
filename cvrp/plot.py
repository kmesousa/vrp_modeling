import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.backends.backend_pdf import PdfPages

from instance import Instance
from solution import Solution


def _draw_arc(ax: Axes, xy, a: int, b: int, cost: float, color, ls: str,
              rad: float, show_cost: bool = True) -> None:
    """Draw arc a->b and, optionally, its cost at the middle of the arc."""
    ax.annotate("", xy=xy[b], xytext=xy[a],
                arrowprops=dict(arrowstyle="->", color=color, ls=ls, lw=1.6,
                                shrinkA=6, shrinkB=6,
                                connectionstyle=f"arc3,rad={rad}"))
    if not show_cost:
        return
    (xa, ya), (xb, yb) = xy[a], xy[b]
    # meio da curva: meio do segmento deslocado 0.5*rad na direção perpendicular
    mx = (xa + xb) / 2 + 0.5 * rad * (yb - ya)
    my = (ya + yb) / 2 - 0.5 * rad * (xb - xa)
    ax.text(mx, my, f"{cost:.1f}", color=color, fontsize=7, ha="center", va="center",
            zorder=5,
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))


def plot_solution(inst: Instance, sol: Solution, ax: Axes | None = None,
                  title: str | None = None, show_costs: bool = True) -> Axes:
    """Draw the routes (one color each); arcs outside any route are red dashed.

    Node: bold black = client index, blue 'q=' = demand. Each arc shows its cost.
    The legend lists vehicles used/available, capacity and load/cost per route.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 7), layout="constrained")
    xy, d = inst.coords, inst.dist
    Q, K = inst.capacity, inst.k_vehicles
    cmap = plt.get_cmap("tab10")

    route_arcs = {}                              # (a, b) -> índice da rota
    for idx, route in enumerate(sol.routes):
        path = [0] + route + [0]
        for a, b in zip(path, path[1:]):
            route_arcs[(a, b)] = idx
    loose = sol.arcs - set(route_arcs)           # subciclos
    all_arcs = set(route_arcs) | loose

    def rad(a: int, b: int) -> float:
        # se existe o arco contrário (ex.: rota de um só cliente), curva os dois
        # para lados opostos, para as setas e os custos não se sobreporem
        return 0.2 if (b, a) in all_arcs else 0.0

    for (a, b), idx in route_arcs.items():
        _draw_arc(ax, xy, a, b, d[a][b], cmap(idx % 10), "-", rad(a, b), show_costs)
    for a, b in loose:
        _draw_arc(ax, xy, a, b, d[a][b], "red", "--", rad(a, b), show_costs)

    # vértices: índice (negrito, preto) e demanda (azul, "q=") em textos separados
    ax.scatter([p[0] for p in xy[1:]], [p[1] for p in xy[1:]], c="k", zorder=3)
    ax.scatter(*xy[0], marker="s", s=140, c="gold", edgecolors="k", zorder=4)
    for i, (px, py) in enumerate(xy):
        ax.annotate(str(i), (px, py), xytext=(6, 4), textcoords="offset points",
                    fontsize=9, fontweight="bold", ha="left", va="bottom", zorder=6)
        if i > 0:
            ax.annotate(f"q={inst.demand[i]}", (px, py), xytext=(6, -4),
                        textcoords="offset points", fontsize=8, color="tab:blue",
                        ha="left", va="top", zorder=6)

    # legenda abaixo do gráfico: frota, capacidade e uma linha por rota
    handles = []
    for idx, route in enumerate(sol.routes):
        path = [0] + route + [0]
        load = sum(inst.demand[i] for i in route)
        route_cost = sum(d[a][b] for a, b in zip(path, path[1:]))
        handles.append(Line2D([], [], color=cmap(idx % 10), lw=2,
                              label=f"Rota {idx + 1}: carga {load}/{Q}, custo {route_cost:.1f}"))
    if loose:
        handles.append(Line2D([], [], color="red", ls="--", lw=2,
                              label="Subciclo (arcos fora de rotas)"))
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.06),
              title=f"Veículos usados: {len(sol.routes)} de {K}  |  capacidade Q = {Q}",
              fontsize=8, title_fontsize=9, frameon=False)

    ax.set_aspect("equal")
    ax.set_title(title or f"{sol.model}  custo={sol.cost:.1f} tempo={sol.time} status={sol.status}")
    return ax

def plot_pdf ():
    pass

# def plot_pdf (n=3, K=3, qteTestes=3, max_seed=100, mostrar=False): #fazer isso
#     achadas = 0
#     pdf=f"resultados_n={n}_k={K}.pdf"
#     with PdfPages(pdf) as paginas:
#         for seed in range(max_seed):
#             inst = make(n, K, seed)
#             sols = [(nome, opts, solve(inst, "dfj_3i", **opts))
#                     for nome, opts in VARIANTES]
#             if sols[0][2].obj is None:          # infactível: tenta a próxima semente
#                 continue

#             otimo = brute_force(inst) if n <= 8 else None
#             print(f"\n=== seed={seed}  n={n}  K={K}  Q={inst.capacity}"
#                     + (f"  ótimo (força bruta)={otimo:.3f}" if otimo else ""))

#             fig, axs = plt.subplots(2, 2, figsize=(13, 14), layout="constrained",
#                                     squeeze=False)
#             axs = axs.ravel()
#             for ax, (nome, opts, s) in zip(axs, sols):
#                 erros = validate(inst, s, capacitated=opts.get("capacitated", True))
#                 print(f"{nome:32s} status={s.status}  custo={s.cost:.3f}  "
#                         f"tempo={s.time:.2f}s  rotas={len(s.routes)}  validate={erros}")
#                 plot_solution(inst, s, ax=ax, title=f"{nome}\ncusto={s.cost:.1f} tempo={s.time:.2f} status:{s.status}")
#             fig.suptitle(f"Instância seed={seed}  (n={n}, K={K}, Q={inst.capacity})")

#             paginas.savefig(fig)
#             if not mostrar:
#                 plt.close(fig)

#             achadas += 1
#             if achadas == qteTestes:
#                 break

#     print(f"\n{achadas} instância(s) salva(s) em {pdf}")
#     if mostrar:
#         plt.show()