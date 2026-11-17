"""Executa experimentos (instâncias x configs), grava JSONL e permite recarregar."""

import json, time, traceback
from dataclasses import fields
from pathlib import Path

from instance import Instance                 # ajuste os imports ao seu pacote
from solution import Solution, validate
from solve import solve
from runConfig import RunConfig, ModelOptions, HeuristicOptions
from record import to_record

SCHEMA = 1


def _failed_solution(config: RunConfig, elapsed: float) -> Solution:
    return Solution(model=config.model, status="erro", obj=None, arcs=set(),
                    routes=[], cost=None, time=elapsed, build_time=None)


def _fmt(x, nd=2):
    return "-" if x is None else f"{x:.{nd}f}"


def run_experiment(insts:list[Instance], cfgs:list[RunConfig], path):
    """Roda cada par (instância, config), grava uma linha JSON por execução.

    Devolve a lista de trios (inst, cfg, sol).
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    results, total, done = [], len(insts) * len(cfgs), 0

    with path.open("a", encoding="utf-8") as f:
        for inst in insts:
            for cfg in cfgs:
                done += 1
                t0 = time.perf_counter()
                try:
                    sol, error = solve(inst, cfg), None
                except Exception as e:          # não pega Ctrl+C
                    traceback.print_exc()        # <- mostra arquivo e linha do KeyError
                    sol = _failed_solution(cfg, time.perf_counter() - t0)
                    error = f"{type(e).__name__}: {e}"

                errors = None                    # só valida se há solução
                if sol.obj is not None:
                    try:
                        errors = validate(inst, sol, capacitated=cfg.options.capacitated)
                    except Exception as e:
                        errors = [f"validate falhou: {type(e).__name__}: {e}"]

                line = {
                    "schema": SCHEMA,
                    "record": to_record(inst, cfg, sol, errors=errors, error=error),
                    "routes": sol.routes,
                    "arcs": sorted(sol.arcs),
                    "coords": inst.coords,
                    "demand": inst.demand,
                }
                f.write(json.dumps(line, default=str) + "\n")
                f.flush()                        # cada execução fica salva na hora

                results.append((inst, cfg, sol))
                print(f"[{done}/{total}] {inst.name} | {cfg.name} | status={sol.status} "
                      f"custo={_fmt(sol.cost)} tempo={_fmt(sol.time, 1)}s"
                      + (f" ERRO={error}" if error else ""), flush=True)
    return results


def _rebuild(d: dict):
    if d.get("schema") != SCHEMA:
        raise ValueError(f"schema {d.get('schema')!r} não suportado")
    rec = d["record"]
    inst = Instance(name=rec["name"], coords=[tuple(p) for p in d["coords"]],
                    demand=d["demand"], capacity=rec["q"], k_vehicles=rec["k"],
                    n_clients=rec["n"], slack=rec["slack"], seed=rec["seed"])
    opts = ModelOptions(**{f.name: rec[f.name] for f in fields(ModelOptions) if f.name in rec})
    cfg = RunConfig(model=rec["model"], options=opts, solver=rec["solver"],
                    time_limit=rec["time_limit"])
    sol = Solution(model=rec["model"], status=rec["status"], obj=rec["obj"],
                   arcs={tuple(a) for a in d["arcs"]}, routes=d["routes"],
                   cost=rec["cost"], time=rec["time"], build_time=rec["build_time"])
    h = (HeuristicOptions(first_solution=rec["first_solution"], metaheuristic=rec["metaheuristic"])
        if rec.get("first_solution") else None)
    cfg = RunConfig(model=rec["model"], options=opts, solver=rec["solver"],
                    time_limit=rec["time_limit"], heuristic=h)
    return inst, cfg, sol


def load_runs(path):
    """Lê o JSONL e devolve a lista de trios (inst, cfg, sol)."""
    runs = []
    with Path(path).open(encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:         # última linha cortada por uma queda
                print(f"linha {n} ignorada (incompleta?)")
                continue
            runs.append(_rebuild(d))
    return runs


#                      TRANSFORMAR O JSON EM TXT LEGIVEL

def format_run(d: dict) -> str:
    """Uma execução em várias linhas: uma chave por linha; listas continuam compactas."""
    def linha(k, v, ind):
        return f'{" " * ind}{json.dumps(k)}: {json.dumps(v)}'

    partes = []
    for k, v in d.items():
        if k == "record":
            campos = ",\n".join(linha(kk, vv, 4) for kk, vv in v.items())
            partes.append(f'  "record": {{\n{campos}\n  }}')
        else:
            partes.append(linha(k, v, 2))
    return "{\n" + ",\n".join(partes) + "\n}"


def export_readable(src, dst):
    """Gera um arquivo só para leitura; o JSONL original não é alterado."""
    with Path(src).open(encoding="utf-8") as f, Path(dst).open("w", encoding="utf-8") as out:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:          # última linha cortada
                continue
            out.write(format_run(d) + "\n\n")