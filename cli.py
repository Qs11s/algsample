import argparse
import random
from typing import List

from solver import solve
from validator import validate
from dbio import save_run, list_runs, load_run, delete_run
import os



DB_DIR = "algsample_db"


def parse_samples(text: str) -> List[int]:
    parts = [p.strip() for p in text.split(",") if p.strip()]
    return [int(x) for x in parts]


def cmd_run(args: argparse.Namespace) -> None:
    params_base = {
        "m": args.m,
        "n": args.n,
        "k": args.k,
        "j": args.j,
        "s": args.s,
        "prune": (not args.no_prune),
        "seed": args.seed,
        "max_groups": args.max_groups,
        "time_limit_ms": args.time_limit_ms,
        "trials": args.trials,
        "score_cap": args.score_cap,
        "enum_work_limit": args.enum_work_limit
    }

    if args.samples is None:
        samples = random.sample(range(1, args.m + 1), args.n)
    else:
        samples = parse_samples(args.samples)

    best = None

    for t in range(max(1, args.restarts)):
        params = dict(params_base)
        if args.seed is not None:
            params["seed"] = args.seed + t

        solve_out = solve(params, samples)
        groups = solve_out.get("groups", [])
        stats = solve_out.get("stats", {})
        val_out = validate(params, sorted(samples), groups)

        cand = {
            "params": params,
            "samples": samples,
            "groups": groups,
            "stats": stats,
            "validate": val_out
        }

        if best is None:
            best = cand
            continue

        bpass = best["validate"].get("pass") is True
        cpass = val_out.get("pass") is True

        if cpass and not bpass:
            best = cand
            continue

        if cpass and bpass:
            if len(groups) < len(best["groups"]):
                best = cand
            continue

        if (not cpass) and (not bpass):
            if val_out.get("failed_J_count", 10**18) < best["validate"].get("failed_J_count", 10**18):
                best = cand
            continue

    # 如果启用了 --keep-best-only，检查文件是否已经存在
    if args.keep_best_only:
        filename = f"{best['params']['m']}-{best['params']['n']}-{best['params']['k']}-{best['params']['j']}-{best['params']['s']}-{len(best['groups'])}.json"
        if os.path.exists(os.path.join(DB_DIR, filename)):
            print("已存在相同结果，跳过保存。")
            return

    filename = save_run(DB_DIR, best["params"], best["samples"], best["groups"], best["stats"], best["validate"])

    print("saved:", filename)
    print("params:", best["params"])
    print("samples:", sorted(best["samples"]))
    print("stats:", best["stats"])
    print("validate:", best["validate"])
    print("groups:")
    for i, g in enumerate(best["groups"], 1):
        print(i, g)




def cmd_list(_: argparse.Namespace) -> None:
    files = list_runs(DB_DIR)
    if not files:
        print("no db files")
        return
    for f in files:
        print(f)


def cmd_execute(args: argparse.Namespace) -> None:
    data = load_run(DB_DIR, args.filename)
    if not data:
        print("file not found")
        return

    params = data.get("params", {})
    samples = data.get("samples", [])
    groups = data.get("groups", [])

    val_out = validate(params, samples, groups)

    print("file:", args.filename)
    print("params:", params)
    print("samples:", samples)
    print("stats:", data.get("stats", {}))
    print("validate(db):", data.get("validate", {}))
    print("validate(now):", val_out)

    # 新增：输出覆盖条件定义和关键统计项
    print("\n=== 覆盖条件 ===")
    print(f"j = {params['j']}, s = {params['s']}")
    print(f"每个 j-子集至少要有 {params['s']} 个样本与 k-组的交集")

    print("\n=== 关键统计 ===")
    print(f"总 j-子集数：{data['stats']['total_nCj']}")
    print(f"总 k-子集数：{data['stats']['total_nCk']}")
    print(f"枚举工作量：{data['stats']['enum_work']}")
    print(f"选中的最优组数（y）：{len(groups)}")
    print(f"pruned（去冗余）: {data['stats'].get('pruned', 0)}")

    print("\n=== groups ===")
    for i, g in enumerate(groups, 1):
        print(i, g)



def cmd_delete(args: argparse.Namespace) -> None:
    ok = delete_run(DB_DIR, args.filename)
    print("deleted" if ok else "file not found")


def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    prun = sub.add_parser("run")
    prun.add_argument("--restarts", type=int, default=1)
    prun.add_argument("--no-prune", action="store_true")
    prun.add_argument("--keep-best-only", action="store_true")

    prun.add_argument("--m", type=int, required=True)
    prun.add_argument("--n", type=int, required=True)
    prun.add_argument("--k", type=int, required=True)
    prun.add_argument("--j", type=int, required=True)
    prun.add_argument("--s", type=int, required=True)
    prun.add_argument("--samples", type=str, default=None)
    prun.add_argument("--seed", type=int, default=None)
    prun.add_argument("--max-groups", type=int, default=200)
    prun.add_argument("--time-limit-ms", type=int, default=0)
    prun.add_argument("--trials", type=int, default=10)
    prun.add_argument("--score-cap", type=int, default=5000)
    prun.add_argument("--enum-work-limit", type=int, default=3000000)

    prun.set_defaults(func=cmd_run)

    plist = sub.add_parser("list")
    plist.set_defaults(func=cmd_list)

    pexe = sub.add_parser("execute")
    pexe.add_argument("filename", type=str)
    pexe.set_defaults(func=cmd_execute)

    pdel = sub.add_parser("delete")
    pdel.add_argument("filename", type=str)
    pdel.set_defaults(func=cmd_delete)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
