import itertools
import time
import random
from typing import Any, Dict, List, Tuple


def _nCk(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    r = 1
    for i in range(1, k + 1):
        r = r * (n - k + i) // i
    return r


def _mask_to_group(mask: int, samples_sorted: List[int]) -> List[int]:
    out = []
    for i, v in enumerate(samples_sorted):
        if (mask >> i) & 1:
            out.append(v)
    return out


def _bits_of_mask(mask: int, n: int) -> List[int]:
    out = []
    for i in range(n):
        if (mask >> i) & 1:
            out.append(i)
    return out


def _prune_groups(params: Dict[str, Any], samples_sorted: List[int], groups: List[List[int]]) -> Tuple[List[List[int]], int]:
    from validator import validate

    removed = 0
    changed = True
    while changed and len(groups) > 1:
        changed = False
        i = 0
        while i < len(groups) and len(groups) > 1:
            candidate = groups[:i] + groups[i + 1 :]
            r = validate(params, samples_sorted, candidate)
            if r.get("pass") is True:
                groups = candidate
                removed += 1
                changed = True
            else:
                i += 1
    return groups, removed


def _solve_greedy_enum(n: int, k: int, j: int, s: int, samples_sorted: List[int]) -> List[List[int]]:
    n_set = set(samples_sorted)
    j_subsets = [frozenset(sub) for sub in itertools.combinations(n_set, j)]
    all_k = [tuple(sorted(sub)) for sub in itertools.combinations(n_set, k)]

    k_to_cov = {}
    for k_idx, k_sub in enumerate(all_k):
        kf = frozenset(k_sub)
        cov = []
        for j_idx, jf in enumerate(j_subsets):
            if len(kf & jf) >= s:
                cov.append(j_idx)
        if cov:
            k_to_cov[k_idx] = cov

    uncovered = set(range(len(j_subsets)))
    selected = []

    while uncovered:
        best_k = None
        best_cov = set()
        for k_idx, cov_list in k_to_cov.items():
            cov = uncovered.intersection(cov_list)
            if len(cov) > len(best_cov):
                best_cov = cov
                best_k = k_idx
        if best_k is None:
            break
        selected.append(best_k)
        uncovered -= best_cov

    return [list(all_k[idx]) for idx in selected]


def _solve_constructive(
    n: int,
    k: int,
    j: int,
    s: int,
    samples_sorted: List[int],
    seed: Any,
    max_groups: int,
    time_limit_ms: int,
    trials: int,
    score_cap: int
) -> Tuple[List[List[int]], str]:
    rng = random.Random(seed) if seed is not None else random.Random()

    j_masks = []
    for comb in itertools.combinations(range(n), j):
        m = 0
        for idx in comb:
            m |= 1 << idx
        j_masks.append(m)

    uncovered = list(range(len(j_masks)))
    groups_masks = []

    t0 = time.perf_counter()

    def iter_bits(x: int):
        while x:
            lsb = x & -x
            yield lsb.bit_length() - 1
            x ^= lsb

    def score_mask(cand_mask: int, eval_indices: List[int]) -> int:
        sc = 0
        for idx in eval_indices:
            if (cand_mask & j_masks[idx]).bit_count() >= s:
                sc += 1
        return sc

    while uncovered:
        if max_groups > 0 and len(groups_masks) >= max_groups:
            return [_mask_to_group(m, samples_sorted) for m in groups_masks], "max_groups"

        if time_limit_ms > 0:
            now_ms = int((time.perf_counter() - t0) * 1000)
            if now_ms >= time_limit_ms:
                return [_mask_to_group(m, samples_sorted) for m in groups_masks], "time_limit"

        if score_cap > 0 and len(uncovered) > score_cap:
            eval_indices = rng.sample(uncovered, score_cap)
        else:
            eval_indices = uncovered

        freq = [0] * n
        for idx in eval_indices:
            for b in iter_bits(j_masks[idx]):
                freq[b] += 1

        pivot_mask = j_masks[uncovered[0]]
        pivot_bits = list(iter_bits(pivot_mask))

        best_mask = None
        best_score = -1

        order = list(range(n))
        order.sort(key=lambda i: (freq[i], rng.random()), reverse=True)

        t = max(1, trials)
        for t_i in range(t):
            if s == j:
                chosen = list(pivot_bits)
            else:
                if t_i % 3 == 0:
                    chosen = rng.sample(pivot_bits, s)
                else:
                    p_order = list(pivot_bits)
                    p_order.sort(key=lambda i: (freq[i], rng.random()), reverse=True)
                    chosen = p_order[:s]

            chosen_set = set(chosen)
            cand = 0
            for b in chosen:
                cand |= 1 << b

            need = k - len(chosen)
            if need < 0:
                continue

            added = 0
            for i in order:
                if i in chosen_set:
                    continue
                cand |= 1 << i
                added += 1
                if added >= need:
                    break

            if cand.bit_count() != k:
                continue

            sc = score_mask(cand, eval_indices)
            if sc > best_score:
                best_score = sc
                best_mask = cand

        if best_mask is None:
            return [_mask_to_group(m, samples_sorted) for m in groups_masks], "no_candidate"

        groups_masks.append(best_mask)

        new_uncovered = []
        for idx in uncovered:
            if (best_mask & j_masks[idx]).bit_count() < s:
                new_uncovered.append(idx)
        uncovered = new_uncovered

    return [_mask_to_group(m, samples_sorted) for m in groups_masks], "ok"



def solve(params: Dict[str, Any], samples: List[int]) -> Dict[str, Any]:
    t0 = time.perf_counter()

    n = int(params["n"])
    k = int(params["k"])
    j = int(params["j"])
    s = int(params["s"])

    do_prune = bool(params.get("prune", True))
    seed = params.get("seed", None)
    max_groups = int(params.get("max_groups", 200))
    time_limit_ms = int(params.get("time_limit_ms", 0))
    trials = int(params.get("trials", 10))
    score_cap = int(params.get("score_cap", 5000))
    enum_work_limit = int(params.get("enum_work_limit", 3000000))

    samples_sorted = sorted(samples)
    if len(samples_sorted) != n:
        return {"groups": [], "stats": {"y": 0, "runtime_ms": 0, "method": "error", "error": "len(samples)!=n"}}

    total_j = _nCk(n, j)
    total_k = _nCk(n, k)
    work = total_j * total_k

    removed = 0

    if work <= enum_work_limit:
        groups = _solve_greedy_enum(n, k, j, s, samples_sorted)
        method = "greedy_enum"
        stopped = "ok"
    else:
        groups, stopped = _solve_constructive(
            n, k, j, s, samples_sorted, seed, max_groups, time_limit_ms, trials, score_cap
        )
        method = "constructive"
        if stopped != "ok" and stopped != "time_limit" and stopped != "max_groups":
            pass

    if do_prune and groups:
        groups, removed = _prune_groups(params, samples_sorted, groups)

    t1 = time.perf_counter()
    runtime_ms = int((t1 - t0) * 1000)

    return {
        "groups": groups,
        "stats": {
            "y": len(groups),
            "runtime_ms": runtime_ms,
            "method": method,
            "pruned": removed,
            "total_nCj": total_j,
            "total_nCk": total_k,
            "enum_work": work,
            "stopped": stopped
        }
    }
