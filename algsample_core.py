import itertools
import os
import json
from typing import List, Set
import multiprocessing
from functools import lru_cache

class AlgSampleSelector:
    def __init__(self):
        self.db_dir = "algsample_db"
        os.makedirs(self.db_dir, exist_ok=True)

    def validate_params(self, m: int, n: int, k: int, j: int, s: int) -> bool:
        if not (45 <= m <= 54):
            print("错误：m必须在45-54之间")
            return False
        if not (7 <= n <= 25):
            print("错误：n必须在7-25之间")
            return False
        if not (4 <= k <= 7):
            print("错误：k必须在4-7之间")
            return False
        if not (s <= j <= k):
            print("错误：j必须满足s≤j≤k")
            return False
        if not (3 <= s <= 7):
            print("错误：s必须在3-7之间")
            return False
        if n > m:
            print("错误：n不能大于m")
            return False
        return True

    def generate_initial_n_samples(self, m: int, n: int, custom_samples: List[int] = None) -> Set[int]:
        if custom_samples:
            if len(custom_samples) != n or max(custom_samples) > m or min(custom_samples) < 1:
                raise ValueError("自定义样本不合法")
            return set(custom_samples)
        return set(itertools.sample(range(1, m+1), n))

    def get_all_j_subsets(self, n_samples: Set[int], j: int) -> List[Set[int]]:
        return [set(subset) for subset in itertools.combinations(n_samples, j)]

@lru_cache(maxsize=None)
def get_frozen_j_subsets(j_subsets: List[Set[int]]) -> List[frozenset]:
    return [frozenset(sub) for sub in j_subsets]

def validate_k_subset(k_sub: tuple, frozen_j_subs: List[frozenset], s: int) -> List[int]:
    covered_js = []
    k_frozen = frozenset(k_sub)
    for j_idx, j_sub in enumerate(frozen_j_subs):
        if len(k_frozen & j_sub) >= s:
            covered_js.append(j_idx)
    return covered_js

class AlgSampleSelector:
    def __init__(self):
        self.db_dir = "algsample_db"
        os.makedirs(self.db_dir, exist_ok=True)

    def validate_params(self, m: int, n: int, k: int, j: int, s: int) -> bool:
        if not (45 <= m <= 54):
            print("错误：m必须在45-54之间")
            return False
        if not (7 <= n <= 25):
            print("错误：n必须在7-25之间")
            return False
        if not (4 <= k <= 7):
            print("错误：k必须在4-7之间")
            return False
        if not (s <= j <= k):
            print("错误：j必须满足s≤j≤k")
            return False
        if not (3 <= s <= 7):
            print("错误：s必须在3-7之间")
            return False
        if n > m:
            print("错误：n不能大于m")
            return False
        return True

    def generate_initial_n_samples(self, m: int, n: int, custom_samples: List[int] = None) -> Set[int]:
        if custom_samples:
            if len(custom_samples) != n or max(custom_samples) > m or min(custom_samples) < 1:
                raise ValueError("自定义样本不合法")
            return set(custom_samples)
        return set(itertools.sample(range(1, m+1), n))

    def get_all_j_subsets(self, n_samples: Set[int], j: int) -> List[Set[int]]:
        return [set(subset) for subset in itertools.combinations(n_samples, j)]

    def find_min_valid_k_subsets(self, m: int, n: int, k: int, j: int, s: int, custom_samples: List[int] = None) -> List[List[int]]:
        if not self.validate_params(m, n, k, j, s):
            return []
        n_samples = self.generate_initial_n_samples(m, n, custom_samples)
        j_subsets = self.get_all_j_subsets(n_samples, j)
        if not j_subsets:
            print("无有效j子集")
            return []
        frozen_j_subs = get_frozen_j_subsets(tuple(j_subsets))
        all_k_subsets = list(itertools.combinations(n_samples, k))
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            tasks = [(k_sub, frozen_j_subs, s) for k_sub in all_k_subsets]
            covered_js_list = pool.starmap(validate_k_subset, tasks)
        k_subset_to_covered_js = {}
        for k_idx, covered_js in enumerate(covered_js_list):
            if covered_js:
                k_subset_to_covered_js[k_idx] = covered_js
        uncovered_js = set(range(len(j_subsets)))
        selected_k_indices = []
        while uncovered_js:
            best_k_idx = None
            best_coverage = set()
            for k_idx, covered_js in k_subset_to_covered_js.items():
                coverage = set(covered_js) & uncovered_js
                if len(coverage) > len(best_coverage):
                    best_coverage = coverage
                    best_k_idx = k_idx
            if best_k_idx is None:
                break
            selected_k_indices.append(best_k_idx)
            uncovered_js -= best_coverage
        selected_k_subsets = [sorted(list(all_k_subsets[idx])) for idx in selected_k_indices]
        print(f"优化后最小有效组数：{len(selected_k_subsets)}")
        return selected_k_subsets

    def save_to_db(self, m: int, n: int, k: int, j: int, s: int, subsets: List[List[int]]) -> str:
        run_count = len([f for f in os.listdir(self.db_dir) if f.startswith(f"{m}-{n}-{k}-{j}-{s}")]) + 1
        result_count = len(subsets)
        filename = f"{m}-{n}-{k}-{j}-{s}-{run_count}-{result_count}.json"
        file_path = os.path.join(self.db_dir, filename)
        data = {
            "params": {"m": m, "n": n, "k": k, "j": j, "s": s},
            "initial_n_samples": sorted(list(self.generate_initial_n_samples(m, n))),
            "valid_k_subsets": subsets
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"结果已保存到：{file_path}")
        return file_path

    def load_from_db(self, filename: str) -> dict:
        file_path = os.path.join(self.db_dir, filename)
        if not os.path.exists(file_path):
            print("文件不存在")
            return {}
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def delete_from_db(self, filename: str) -> bool:
        file_path = os.path.join(self.db_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"已删除：{file_path}")
            return True
        print("文件不存在")
        return False

if __name__ == "__main__":
    selector = AlgSampleSelector()
    m = 45
    n = 7
    k = 6
    j = 5
    s = 5
    valid_subsets = selector.find_min_valid_k_subsets(m, n, k, j, s)
    if valid_subsets:
        selector.save_to_db(m, n, k, j, s, valid_subsets)