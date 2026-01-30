import itertools
import os
import json
import random
from typing import List, Set, Tuple

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

    def generate_initial_n_samples(self, m: int, n: int, custom_samples: List[int] = None) -> Tuple[Set[int], List[int]]:
        if custom_samples:
            if len(custom_samples) != n or max(custom_samples) > m or min(custom_samples) < 1:
                raise ValueError("自定义样本不合法")
            sample_set = set(custom_samples)
            sample_list = sorted(custom_samples)
        else:
            sample_list = random.sample(range(1, m+1), n)
            sample_set = set(sample_list)
        return sample_set, sample_list

    def get_all_j_subsets(self, n_samples: Set[int], j: int) -> Tuple[List[Set[int]], List[List[int]]]:
        subsets_set = [set(subset) for subset in itertools.combinations(n_samples, j)]
        subsets_list = [sorted(list(subset)) for subset in itertools.combinations(n_samples, j)]
        return subsets_set, subsets_list

    def get_all_k_subsets(self, n_samples: Set[int], k: int) -> List[List[int]]:
        return [sorted(list(subset)) for subset in itertools.combinations(n_samples, k)]

    def find_min_valid_k_subsets(self, m: int, n: int, k: int, j: int, s: int, custom_samples: List[int] = None) -> Tuple[List[List[int]], dict]:
        if not self.validate_params(m, n, k, j, s):
            return [], {}
        n_sample_set, n_sample_list = self.generate_initial_n_samples(m, n, custom_samples)
        j_subsets_set, j_subsets_list = self.get_all_j_subsets(n_sample_set, j)
        all_k_subsets = self.get_all_k_subsets(n_sample_set, k)
        total_m_choose_n = self.combination(m, n)
        total_n_choose_j = len(j_subsets_list)
        total_n_choose_k = len(all_k_subsets)
        
        if not j_subsets_set:
            print("无有效j子集")
            return [], {}
        
        frozen_j_subs = get_frozen_j_subsets(j_subsets_set)
        covered_js_list = [validate_k_subset(tuple(k_sub), frozen_j_subs, s) for k_sub in all_k_subsets]
        
        k_subset_to_covered_js = {}
        valid_k_indices = []
        valid_k_subsets = []
        for k_idx, (k_sub, covered_js) in enumerate(zip(all_k_subsets, covered_js_list)):
            if covered_js:
                k_subset_to_covered_js[k_idx] = covered_js
                valid_k_indices.append(k_idx)
                valid_k_subsets.append(k_sub)
        
        uncovered_js = set(range(len(j_subsets_set)))
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
        
        selected_k_subsets = [all_k_subsets[idx] for idx in selected_k_indices]
        selected_count = len(selected_k_subsets)
        
        detail_info = {
            "total_m_choose_n": total_m_choose_n,
            "total_n_choose_j": total_n_choose_j,
            "total_n_choose_k": total_n_choose_k,
            "initial_n_samples": n_sample_list,
            "all_j_subsets": j_subsets_list,
            "all_k_subsets": all_k_subsets,
            "valid_k_subsets_count": len(valid_k_subsets),
            "selected_k_subsets_count": selected_count
        }
        
        print("\n=== 样本选择详细信息 ===")
        print(f"参数：m={m}, n={n}, k={k}, j={j}, s={s}")
        print(f"从m={m}个样本中选n={n}个的总组合数：{total_m_choose_n}")
        print(f"初始选中的n个样本：{n_sample_list}")
        print(f"从n={n}个样本中选j={j}个的总组合数：{total_n_choose_j}")
        print(f"从n={n}个样本中选k={k}个的总组合数：{total_n_choose_k}")
        print(f"有效k样本子集总数（满足条件）：{len(valid_k_subsets)}")
        print(f"优化后最小有效k样本子集数：{selected_count}")
        print("\n=== 优化后最小有效k样本子集 ===")
        for i, subset in enumerate(selected_k_subsets, 1):
            print(f"{i}. {subset}")
        print("\n" + "="*50)
        
        return selected_k_subsets, detail_info

    def combination(self, a: int, b: int) -> int:
        if b < 0 or b > a:
            return 0
        if b == 0 or b == a:
            return 1
        b = min(b, a - b)
        result = 1
        for i in range(1, b+1):
            result = result * (a - b + i) // i
        return result

    def save_to_db(self, m: int, n: int, k: int, j: int, s: int, subsets: List[List[int]], detail_info: dict) -> str:
        run_count = len([f for f in os.listdir(self.db_dir) if f.startswith(f"{m}-{n}-{k}-{j}-{s}")]) + 1
        result_count = len(subsets)
        filename = f"{m}-{n}-{k}-{j}-{s}-{run_count}-{result_count}.json"
        file_path = os.path.join(self.db_dir, filename)
        
        data = {
            "params": {"m": m, "n": n, "k": k, "j": j, "s": s},
            "detail_info": detail_info,
            "selected_k_subsets": subsets
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"结果已保存到：{file_path}")
        print(f"文件包含：参数、所有组合数、初始样本、所有j/k子集、有效子集、选中子集")
        return file_path

    def load_from_db(self, filename: str) -> dict:
        file_path = os.path.join(self.db_dir, filename)
        if not os.path.exists(file_path):
            print("文件不存在")
            return {}
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print("\n=== 从DB文件加载的信息 ===")
        print(f"参数：m={data['params']['m']}, n={data['params']['n']}, k={data['params']['k']}, j={data['params']['j']}, s={data['params']['s']}")
        print(f"从m个样本中选n个的总组合数：{data['detail_info']['total_m_choose_n']}")
        print(f"初始选中的n个样本：{data['detail_info']['initial_n_samples']}")
        print(f"从n个样本中选j个的总组合数：{data['detail_info']['total_n_choose_j']}")
        print(f"从n个样本中选k个的总组合数：{data['detail_info']['total_n_choose_k']}")
        print(f"有效k样本子集总数：{data['detail_info']['valid_k_subsets_count']}")
        print(f"优化后最小有效k样本子集数：{data['detail_info']['selected_k_subsets_count']}")
        print("\n=== 所有j样本子集 ===")
        for i, subset in enumerate(data['detail_info']['all_j_subsets'], 1):
            print(f"{i}. {subset}")
        print("\n=== 优化后最小有效k样本子集 ===")
        for i, subset in enumerate(data['selected_k_subsets'], 1):
            print(f"{i}. {subset}")
        print("\n" + "="*50)
        return data

    def delete_from_db(self, filename: str) -> bool:
        file_path = os.path.join(self.db_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"已删除DB文件：{file_path}")
            return True
        print("文件不存在，删除失败")
        return False

if __name__ == "__main__":
    from solver import solve
    from validator import validate

    m = 45
    n = 7
    k = 6
    j = 5
    s = 5

    params = {"m": m, "n": n, "k": k, "j": j, "s": s}

    custom_samples = None

    if custom_samples is None:
        import random
        samples = random.sample(range(1, m + 1), n)
    else:
        samples = custom_samples

    solve_out = solve(params, samples)
    groups = solve_out["groups"]
    stats = solve_out["stats"]

    val_out = validate(params, sorted(samples), groups)

    print("params:", params)
    print("samples:", sorted(samples))
    print("stats:", stats)
    print("validate:", val_out)
    print("groups:")
    for i, g in enumerate(groups, 1):
        print(i, g)


    # selector.load_from_db("45-7-6-5-5-1-6.json")
    

    # selector.delete_from_db("45-7-6-5-5-1-6.json")