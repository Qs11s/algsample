import tkinter as tk
from tkinter import messagebox
from solver import solve
from validator import validate
from dbio import save_run, list_runs, load_run


class SampleSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Optimal Samples Selection System")

        # 输入参数区域
        self.m_label = tk.Label(root, text="m:")
        self.m_label.grid(row=0, column=0)
        self.m_entry = tk.Entry(root)
        self.m_entry.grid(row=0, column=1)

        self.n_label = tk.Label(root, text="n:")
        self.n_label.grid(row=1, column=0)
        self.n_entry = tk.Entry(root)
        self.n_entry.grid(row=1, column=1)

        self.k_label = tk.Label(root, text="k:")
        self.k_label.grid(row=2, column=0)
        self.k_entry = tk.Entry(root)
        self.k_entry.grid(row=2, column=1)

        self.j_label = tk.Label(root, text="j:")
        self.j_label.grid(row=3, column=0)
        self.j_entry = tk.Entry(root)
        self.j_entry.grid(row=3, column=1)

        self.s_label = tk.Label(root, text="s:")
        self.s_label.grid(row=4, column=0)
        self.s_entry = tk.Entry(root)
        self.s_entry.grid(row=4, column=1)

        # 用户输入样本
        self.samples_label = tk.Label(root, text="Samples (comma separated):")
        self.samples_label.grid(row=5, column=0)
        self.samples_entry = tk.Entry(root)
        self.samples_entry.grid(row=5, column=1)

        # 操作按钮
        self.run_button = tk.Button(root, text="Run", command=self.run_algorithm)
        self.run_button.grid(row=6, column=0)

        self.load_button = tk.Button(root, text="Load", command=self.load_result)
        self.load_button.grid(row=6, column=1)

        self.delete_button = tk.Button(root, text="Delete", command=self.delete_result)
        self.delete_button.grid(row=6, column=2)

        # 结果显示区域
        self.result_text = tk.Text(root, height=10, width=50)
        self.result_text.grid(row=7, column=0, columnspan=3)

    def run_algorithm(self):
        try:
            m = int(self.m_entry.get())
            n = int(self.n_entry.get())
            k = int(self.k_entry.get())
            j = int(self.j_entry.get())
            s = int(self.s_entry.get())
            samples = list(map(int, self.samples_entry.get().split(',')))

            params = {"m": m, "n": n, "k": k, "j": j, "s": s}
            solve_out = solve(params, samples)
            groups = solve_out.get("groups", [])
            stats = solve_out.get("stats", {})
            val_out = validate(params, sorted(samples), groups)

            # 输出结果
            result_str = f"Params: {params}\n"
            result_str += f"Stats: {stats}\n"
            result_str += f"Validation: {val_out}\n"
            result_str += f"Groups:\n"
            for i, g in enumerate(groups, 1):
                result_str += f"{i}. {g}\n"
            
            # 显示结果
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result_str)

            # 保存结果
            save_run("algsample_db", params, samples, groups, stats, val_out)
            messagebox.showinfo("Success", "Results saved successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def load_result(self):
        filename = self.samples_entry.get()  # For simplicity, use samples input as filename
        result = load_run("algsample_db", filename)
        if result:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Loaded result:\n{result}")
        else:
            messagebox.showerror("Error", "Result file not found.")

    def delete_result(self):
        filename = self.samples_entry.get()
        if delete_run("algsample_db", filename):
            messagebox.showinfo("Success", "File deleted successfully!")
        else:
            messagebox.showerror("Error", "File not found.")


if __name__ == "__main__":
    root = tk.Tk()
    app = SampleSelectorApp(root)
    root.mainloop()
