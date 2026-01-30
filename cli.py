import argparse
import random
from typing import List

from solver import solve
from validator import validate
from dbio import save_run, list_runs, load_run, delete_run


DB_DIR = "algsample_db"


def parse_samples(text: str) -> List[int]:
    parts = [p.strip() for p in text.split(",") if p.strip()]
    return [int(x) for x in parts]


def cmd_run(args: argparse.Namespace) -> None:
    params = {"m": args.m, "n": args.n, "k": args.k, "j": args.j, "s": args.s}

    if args.samples is None:
        samples = random.sample(range(1, args.m + 1), args.n)
    else:
        samples = parse_samples(args.samples)

    solve_out = solve(params, samples)
    groups = solve_out.get("groups", [])
    stats = solve_out.get("stats", {})
    val_out = validate(params, sorted(samples), groups)

    filename = save_run(DB_DIR, params, samples, groups, stats, val_out)

    print("saved:", filename)
    print("params:", params)
    print("samples:", sorted(samples))
    print("stats:", stats)
    print("validate:", val_out)
    print("groups:")
    for i, g in enumerate(groups, 1):
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
    print("groups:")
    for i, g in enumerate(groups, 1):
        print(i, g)


def cmd_delete(args: argparse.Namespace) -> None:
    ok = delete_run(DB_DIR, args.filename)
    print("deleted" if ok else "file not found")


def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    prun = sub.add_parser("run")
    prun.add_argument("--m", type=int, required=True)
    prun.add_argument("--n", type=int, required=True)
    prun.add_argument("--k", type=int, required=True)
    prun.add_argument("--j", type=int, required=True)
    prun.add_argument("--s", type=int, required=True)
    prun.add_argument("--samples", type=str, default=None)
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
