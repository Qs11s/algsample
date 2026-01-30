import itertools
from typing import Any, Dict, List, Tuple


def _norm_samples(samples: List[int]) -> List[int]:
    if not isinstance(samples, list):
        raise TypeError("samples")
    if any(not isinstance(x, int) for x in samples):
        raise TypeError("samples")
    if len(samples) != len(set(samples)):
        raise ValueError("samples")
    return sorted(samples)


def _norm_groups(groups: List[List[int]], k: int, sample_set: set) -> List[Tuple[int, ...]]:
    if not isinstance(groups, list):
        raise TypeError("groups")
    out = []
    seen = set()
    for g in groups:
        if not isinstance(g, list):
            raise TypeError("groups")
        if len(g) != k:
            raise ValueError("groups")
        if any(not isinstance(x, int) for x in g):
            raise TypeError("groups")
        tg = tuple(sorted(g))
        if len(set(tg)) != k:
            raise ValueError("groups")
        if any(x not in sample_set for x in tg):
            raise ValueError("groups")
        if tg not in seen:
            seen.add(tg)
            out.append(tg)
    return out


def validate(params: Dict[str, Any], samples: List[int], groups: List[List[int]]) -> Dict[str, Any]:
    try:
        n = int(params["n"])
        k = int(params["k"])
        j = int(params["j"])
        s = int(params["s"])
    except Exception:
        return {"pass": False, "failed_J_count": -1, "min_coverage": 0, "details": "params"}

    if not (s <= j <= k):
        return {"pass": False, "failed_J_count": -1, "min_coverage": 0, "details": "s<=j<=k"}

    try:
        samples_sorted = _norm_samples(samples)
    except Exception:
        return {"pass": False, "failed_J_count": -1, "min_coverage": 0, "details": "samples"}

    if len(samples_sorted) != n:
        return {"pass": False, "failed_J_count": -1, "min_coverage": 0, "details": "len(samples)!=n"}

    sample_set = set(samples_sorted)

    try:
        norm_groups = _norm_groups(groups, k, sample_set)
    except Exception:
        return {"pass": False, "failed_J_count": -1, "min_coverage": 0, "details": "groups"}

    if not norm_groups:
        return {"pass": False, "failed_J_count": -1, "min_coverage": 0, "details": "empty groups"}

    group_sets = [set(g) for g in norm_groups]

    failed = 0
    min_cov = 10**9
    first_fail = None

    for J in itertools.combinations(samples_sorted, j):
        Jset = set(J)
        best = 0
        for Gset in group_sets:
            inter = len(Jset & Gset)
            if inter > best:
                best = inter
                if best >= s:
                    break
        if best < s:
            failed += 1
            if first_fail is None:
                first_fail = list(J)
        if best < min_cov:
            min_cov = best

    if min_cov == 10**9:
        min_cov = 0

    if failed == 0:
        return {"pass": True, "failed_J_count": 0, "min_coverage": int(min_cov), "details": "OK"}

    return {
        "pass": False,
        "failed_J_count": failed,
        "min_coverage": int(min_cov),
        "details": f"uncovered example: {first_fail}"
    }
