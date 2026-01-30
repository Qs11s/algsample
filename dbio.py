import json
import os
from typing import Any, Dict, List


def ensure_db_dir(db_dir: str) -> None:
    os.makedirs(db_dir, exist_ok=True)


def next_run_id(db_dir: str, prefix: str) -> int:
    ensure_db_dir(db_dir)
    mx = 0
    for f in os.listdir(db_dir):
        if not (f.startswith(prefix + "-") and f.endswith(".json")):
            continue
        core = f[:-5]
        parts = core.split("-")
        if len(parts) < 7:
            continue
        try:
            rid = int(parts[5])
        except Exception:
            continue
        if rid > mx:
            mx = rid
    return mx + 1



def save_run(db_dir: str, params: Dict[str, Any], samples: List[int], groups: List[List[int]], stats: Dict[str, Any], validate_out: Dict[str, Any]) -> str:
    ensure_db_dir(db_dir)
    prefix = f"{params['m']}-{params['n']}-{params['k']}-{params['j']}-{params['s']}"
    run_id = next_run_id(db_dir, prefix)
    y = len(groups)
    filename = f"{prefix}-{run_id}-{y}.json"
    path = os.path.join(db_dir, filename)

    data = {
        "params": params,
        "samples": sorted(samples),
        "groups": groups,
        "stats": stats,
        "validate": validate_out
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filename


def list_runs(db_dir: str) -> List[str]:
    ensure_db_dir(db_dir)
    files = [f for f in os.listdir(db_dir) if f.endswith(".json")]
    files.sort()
    return files


def load_run(db_dir: str, filename: str) -> Dict[str, Any]:
    path = os.path.join(db_dir, filename)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def delete_run(db_dir: str, filename: str) -> bool:
    path = os.path.join(db_dir, filename)
    if not os.path.exists(path):
        return False
    os.remove(path)
    return True
