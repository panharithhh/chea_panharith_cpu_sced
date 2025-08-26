import tkinter as tk
from tkinter import ttk, messagebox

from models import Proc, compute_metrics
from algorithms import (
    schedule_fcfs,
    schedule_rr,
    schedule_srtf,
    schedule_sjf_np,
    schedule_mlfq,
)
from gantt import draw_gantt


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CPU Scheduling Simulator")
        self.geometry("980x640")
        self._build()
        self.next_num = 1

    def _build(self):
        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        top = ttk.Frame(root)
        top.pack(fill="x", pady=4)

        ttk.Label(top, text="Algorithm").pack(side="left")

        self.alg = tk.StringVar(value="FCFS")
        self.alg_cb = ttk.Combobox(
            top,
            textvariable=self.alg,
            state="readonly",
            values=["FCFS", "RR", "SRTF", "SJF", "MLFQ"],
            width=12,
        )
        self.alg_cb.pack(side="left", padx=6)
        self.alg_cb.bind("<<ComboboxSelected>>", lambda e: self._toggle())

        self.q_lbl = ttk.Label(top, text="Quantum")
        self.q_var = tk.StringVar(value="2")
        self.q_ent = ttk.Entry(top, textvariable=self.q_var, width=6)

        self.mlfq_lbl = ttk.Label(top, text="MLFQ q")
        self.mlfq_var = tk.StringVar(value="4,8,12")
        self.mlfq_ent = ttk.Entry(top, textvariable=self.mlfq_var, width=12)

        self._toggle()

        ttk.Button(top, text="Run", command=self.run).pack(side="right")
        ttk.Button(top, text="Clear", command=self.clear_all).pack(side="right", padx=6)

        inp = ttk.Frame(root)
        inp.pack(fill="x", pady=4)

        self.pid = tk.StringVar(value="P1")
        self.at = tk.StringVar(value="0")
        self.bt = tk.StringVar(value="5")

        ttk.Label(inp, text="PID").grid(row=0, column=0, padx=3)
        ttk.Entry(inp, textvariable=self.pid, width=8).grid(row=1, column=0, padx=3)

        ttk.Label(inp, text="Arrival").grid(row=0, column=1, padx=3)
        ttk.Entry(inp, textvariable=self.at, width=8).grid(row=1, column=1, padx=3)

        ttk.Label(inp, text="Burst").grid(row=0, column=2, padx=3)
        ttk.Entry(inp, textvariable=self.bt, width=8).grid(row=1, column=2, padx=3)

        ttk.Button(inp, text="Add", command=self.add_proc).grid(row=1, column=3, padx=8)
        ttk.Button(inp, text="Delete", command=self.del_sel).grid(row=1, column=4, padx=0)

        table = ttk.Frame(root)
        table.pack(fill="x", pady=4)

        self.tree = ttk.Treeview(
            table,
            columns=("pid", "at", "bt"),
            show="headings",
            height=6,
        )
        for c, w in [("pid", 80), ("at", 100), ("bt", 100)]:
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=w, anchor="center")
        self.tree.pack(side="left", fill="x", expand=True)

        vsb = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        vsb.pack(side="left", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)

        gbox = ttk.LabelFrame(root, text="Gantt")
        gbox.pack(fill="both", expand=True, pady=6)

        self.canvas = tk.Canvas(gbox, height=220, bg="white")
        self.canvas.pack(fill="both", expand=True, padx=6, pady=6)

        mbox = ttk.LabelFrame(root, text="Metrics")
        mbox.pack(fill="both", expand=True)

        self.metrics = ttk.Treeview(
            mbox,
            columns=("pid", "waiting", "turn", "resp", "comp"),
            show="headings",
            height=8,
        )
        for c, w in [
            ("pid", 80),
            ("waiting", 100),
            ("turn", 110),
            ("resp", 100),
            ("comp", 110),
        ]:
            self.metrics.heading(c, text=c.upper())
            self.metrics.column(c, width=w, anchor="center")
        self.metrics.pack(side="left", fill="both", expand=True, padx=6, pady=6)

        vsb2 = ttk.Scrollbar(mbox, orient="vertical", command=self.metrics.yview)
        vsb2.pack(side="left", fill="y")
        self.metrics.configure(yscrollcommand=vsb2.set)

        self.avg = ttk.Label(root, text="Averages: Waiting=— Turnaround=— Response=—")
        self.avg.pack(anchor="w", pady=4)

        for r in [("P1", 0, 7), ("P2", 2, 4), ("P3", 4, 1), ("P4", 5, 4)]:
            self.tree.insert("", "end", values=r)

        try:
            s = ttk.Style()
            if "clam" in s.theme_names():
                s.theme_use("clam")
        except Exception:
            pass

    def _toggle(self):
        for w in (self.q_lbl, self.q_ent, self.mlfq_lbl, self.mlfq_ent):
            w.pack_forget()

        a = self.alg.get()

        if a == "RR":
            self.q_lbl.pack(side="left")
            self.q_ent.pack(side="left", padx=4)

        if a == "MLFQ":
            self.mlfq_lbl.pack(side="left")
            self.mlfq_ent.pack(side="left", padx=4)

    def add_proc(self):
        pid = self.pid.get().strip() or f"P{self.next_num}"

        try:
            at = int(self.at.get())
            bt = int(self.bt.get())
            if at < 0 or bt <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Bad input")
            return

        for iid in self.tree.get_children():
            if self.tree.item(iid, "values")[0] == pid:
                messagebox.showerror("Error", "Duplicate PID")
                return

        self.tree.insert("", "end", values=(pid, at, bt))
        self.next_num += 1
        self.pid.set(f"P{self.next_num}")

    def del_sel(self):
        for iid in self.tree.selection():
            self.tree.delete(iid)

    def clear_all(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        for iid in self.metrics.get_children():
            self.metrics.delete(iid)

        self.canvas.delete("all")
        self.avg.config(text="Averages: Waiting=— Turnaround=— Response=—")

        self.next_num = 1
        self.pid.set("P1")
        self.at.set("0")
        self.bt.set("5")

    def _collect(self):
        rows = []
        for iid in self.tree.get_children():
            pid, at, bt = self.tree.item(iid, "values")
            rows.append((pid, int(at), int(bt)))

        rows.sort(key=lambda r: (r[1], r[0]))
        return [Proc(pid, at, bt) for pid, at, bt in rows]

    def run(self):
        procs = self._collect()

        if not procs:
            messagebox.showwarning("Empty", "Add processes")
            return

        a = self.alg.get()

        try:
            if a == "FCFS":
                timeline, done = schedule_fcfs(procs)
            elif a == "RR":
                q = int(self.q_var.get())
                timeline, done = schedule_rr(procs, q)
            elif a == "SRTF":
                timeline, done = schedule_srtf(procs)
            elif a == "SJF":
                timeline, done = schedule_sjf_np(procs)
            elif a == "MLFQ":
                qs = [int(x.strip()) for x in self.mlfq_var.get().split(",") if x.strip()]
                timeline, done = schedule_mlfq(procs, qs)
            else:
                raise ValueError
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        draw_gantt(self.canvas, timeline)
        self._metrics(done)

    def _metrics(self, done):
        for iid in self.metrics.get_children():
            self.metrics.delete(iid)

        m = compute_metrics(done)

        if not m:
            self.avg.config(text="Averages: Waiting=— Turnaround=— Response=—")
            return

        tw = 0
        tt = 0
        tr = 0

        for p in sorted(done, key=lambda x: x.pid):
            d = m[p.pid]
            self.metrics.insert(
                "",
                "end",
                values=(p.pid, d["waiting"], d["turnaround"], d["response"], d["completion"]),
            )
            tw += d["waiting"]
            tt += d["turnaround"]
            tr += d["response"]

        n = len(done)
        self.avg.config(
            text=f"Averages: Waiting={tw / n:.2f}  "
                 f"Turnaround={tt / n:.2f}  "
                 f"Response={tr / n:.2f}"
        )


if __name__ == "__main__":
    App().mainloop()
