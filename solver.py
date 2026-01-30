import itertools
import time
from typing import Any, Dict, List, Set, Tuple


def _get_frozen_j_subsets(j_subsets: List[Set[int]]) -> List[frozenset]:
    return [frozenset(sub) for sub in j_subsets]


def _covered_j_indices_by_k(k_sub: Tuple[int, ...], frozen_j_subs: List[frozenset], s: int) -> List[int]:
    k_frozen = frozenset(k_sub)
    out = []
    for j_idx, j_sub in enumerate(frozen_j_subs):
        if len(k_frozen & j_sub) >= s:
            out.append(j_idx)
    return out


def solve(params: Dict[str, Any], samples: List[int]) -> Dict[str, Any]:
    t0 = time.perf_counter()

    n = int(params["n"])
    k = int(params["k"])
    j = int(params["j"])
    s = int(params["s"])

    samples_sorted = sorted(samples)
    if len(samples_sorted) != n:
        return {"groups": [], "stats": {"y": 0, "runtime_ms": 0, "method": "greedy_enum", "error": "len(samples)!=n"}}

    n_sample_set = set(samples_sorted)

    j_subsets_set = [set(subset) for subset in itertools.combinations(n_sample_set, j)]
    all_k_subsets = [tuple(sorted(subset)) for subset in itertools.combinations(n_sample_set, k)]

    if not j_subsets_set:
        return {"groups": [], "stats": {"y": 0, "runtime_ms": 0, "method": "greedy_enum", "error": "no j subsets"}}

    frozen_j_subs = _get_frozen_j_subsets(j_subsets_set)

    k_subset_to_covered_js = {}
    for k_idx, k_sub in enumerate(all_k_subsets):
        covered_js = _covered_j_indices_by_k(k_sub, frozen_j_subs, s)
        if covered_js:
            k_subset_to_covered_js[k_idx] = covered_js

    uncovered_js = set(range(len(j_subsets_set)))
    selected_k_indices = []

    while uncovered_js:
        best_k_idx = None
        best_cov = set()
        for k_idx, covered_js in k_subset_to_covered_js.items():
            cov = uncovered_js.intersection(covered_js)
            if len(cov) > len(best_cov):
                best_cov = cov
                best_k_idx = k_idx
        if best_k_idx is None:
            break
        selected_k_indices.append(best_k_idx)
        uncovered_js -= best_cov

    groups = [list(all_k_subsets[idx]) for idx in selected_k_indices]

    t1 = time.perf_counter()
    runtime_ms = int((t1 - t0) * 1000)

    return {
        "groups": groups,
        "stats": {"y": len(groups), "runtime_ms": runtime_ms, "method": "greedy_enum"}
    }
