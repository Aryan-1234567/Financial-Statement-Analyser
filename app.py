"""Financial Statement Analyser — a small Tkinter desktop application.

Run with: python3 main.py
All amounts should be entered in the same currency and scale.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from analysis_report import explain
from ratios import FIELDS, RATIO_META, compute_ratios, fmt


class AnalyserApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Financial Statement Analyser")
        self.geometry("1120x820")
        self.minsize(900, 650)
        self.configure(bg="#f4f6f8")
        self.entries: dict[str, ttk.Entry] = {}
        self.benchmark_entries: dict[str, ttk.Entry] = {}
        self._build()

    def _build(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f4f6f8")
        style.configure("Card.TLabelframe", background="white", padding=12)
        style.configure("Card.TLabelframe.Label", background="white", foreground="#183153", font=("Arial", 11, "bold"))
        style.configure("TLabel", background="#f4f6f8", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10, "bold"), padding=8)
        style.configure("Treeview", rowheight=27, font=("Arial", 9))
        style.configure("Treeview.Heading", font=("Arial", 9, "bold"))

        header = ttk.Frame(self, padding=(18, 14, 18, 5))
        header.pack(fill="x")
        ttk.Label(header, text="Financial Statement Analyser", font=("Arial", 20, "bold"), foreground="#183153").pack(anchor="w")
        ttk.Label(header, text="Enter one period of company figures and industry benchmarks. Use consistent currency units throughout.", foreground="#536273").pack(anchor="w", pady=(4, 0))

        body = ttk.Frame(self, padding=(18, 10, 18, 12))
        body.pack(fill="both", expand=True)
        left_shell = ttk.Frame(body)
        left_shell.pack(side="left", fill="y", padx=(0, 14))
        left_canvas = tk.Canvas(left_shell, width=345, bg="#f4f6f8", highlightthickness=0)
        left_scroll = ttk.Scrollbar(left_shell, orient="vertical", command=left_canvas.yview)
        left_canvas.configure(yscrollcommand=left_scroll.set)
        left_scroll.pack(side="right", fill="y")
        left_canvas.pack(side="left", fill="y", expand=True)
        left = ttk.Frame(left_canvas)
        left_window = left_canvas.create_window((0, 0), window=left, anchor="nw")
        left.bind("<Configure>", lambda _event: left_canvas.configure(scrollregion=left_canvas.bbox("all")))
        left_canvas.bind("<Configure>", lambda event: left_canvas.itemconfigure(left_window, width=event.width))

        company_card = ttk.LabelFrame(left, text="Company details", style="Card.TLabelframe")
        company_card.pack(fill="x", pady=(0, 10))
        self.company = self._field(company_card, "Company name", "Company")
        self.period = self._field(company_card, "Reporting period", "Latest financial year")

        for section, title in (("Income statement", "Income statement"), ("Statement of financial position", "Statement of financial position")):
            card = ttk.LabelFrame(left, text=title, style="Card.TLabelframe")
            card.pack(fill="x", pady=(0, 10))
            for key, (label, group) in FIELDS.items():
                if group == section:
                    self.entries[key] = self._field(card, label)

        bench_card = ttk.LabelFrame(left, text="Industry benchmarks", style="Card.TLabelframe")
        bench_card.pack(fill="x", pady=(0, 10))
        ttk.Label(bench_card, text="Leave blank to omit a comparison. Use %, days or x as shown.", wraplength=270, foreground="#536273").pack(anchor="w", pady=(0, 6))
        for name, unit, _, key in RATIO_META:
            self.benchmark_entries[key] = self._field(bench_card, f"{name} ({unit})")

        ttk.Button(left, text="Analyse statements", command=self.analyse).pack(fill="x", pady=(2, 6))
        ttk.Button(left, text="Clear all inputs", command=self.clear).pack(fill="x")

        right = ttk.Frame(body)
        right.pack(side="left", fill="both", expand=True)
        ratios_card = ttk.LabelFrame(right, text="Ratio results", style="Card.TLabelframe")
        ratios_card.pack(fill="both", expand=True, pady=(0, 10))
        cols = ("category", "ratio", "company", "industry", "reading")
        self.table = ttk.Treeview(ratios_card, columns=cols, show="headings", height=14)
        for col, label, width in zip(cols, ("Category", "Ratio", "Company", "Industry", "Comparison"), (125, 185, 90, 90, 105)):
            self.table.heading(col, text=label)
            self.table.column(col, width=width, anchor="w" if col in ("category", "ratio", "reading") else "center")
        self.table.pack(fill="both", expand=True)

        report_card = ttk.LabelFrame(right, text="Plain-English report", style="Card.TLabelframe")
        report_card.pack(fill="both", expand=True)
        report_tools = ttk.Frame(report_card)
        report_tools.pack(fill="x", pady=(0, 5))
        ttk.Button(report_tools, text="Save report as .txt", command=self.save_report).pack(side="right")
        self.report = tk.Text(report_card, wrap="word", height=16, font=("Arial", 10), padx=10, pady=8, relief="flat", bg="#fbfcfd")
        scroll = ttk.Scrollbar(report_card, command=self.report.yview)
        self.report.configure(yscrollcommand=scroll.set)
        self.report.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.report.insert("1.0", "Your analysis will appear here after you enter the financial figures and select Analyse statements.")

    @staticmethod
    def _field(parent: ttk.Widget, label: str, default: str = "") -> ttk.Entry:
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=2)
        ttk.Label(row, text=label, width=31, wraplength=210).pack(side="left", anchor="w")
        entry = ttk.Entry(row, width=16)
        entry.pack(side="right")
        if default:
            entry.insert(0, default)
        return entry

    def _read_number(self, entry: ttk.Entry, label: str, *, optional: bool = False) -> float | None:
        raw = entry.get().strip().replace(",", "").replace("£", "").replace("$", "").replace("€", "")
        if not raw:
            if optional:
                return None
            raise ValueError(f"Enter a value for {label} (use 0 if it does not apply).")
        try:
            value = float(raw)
        except ValueError as exc:
            raise ValueError(f"{label} must be a number.") from exc
        if value < 0:
            raise ValueError(f"{label} cannot be negative.")
        return value

    def analyse(self) -> None:
        try:
            values = {key: self._read_number(entry, key) for key, entry in self.entries.items()}
            values = {k: float(v) for k, v in values.items() if v is not None}
            benchmarks = {key: self._read_number(entry, name, optional=True) for name, _, _, key in RATIO_META for entry in [self.benchmark_entries[key]]}
        except ValueError as error:
            messagebox.showerror("Check your inputs", str(error))
            return
        results = compute_ratios(values)
        for item in self.table.get_children():
            self.table.delete(item)
        categories = {
            "Profitability": {"gross_margin", "operating_margin", "net_margin", "roa", "roe"},
            "Efficiency": {"inventory_turnover", "receivable_days", "payable_days", "asset_turnover"},
            "Gearing": {"debt_equity", "gearing"},
            "Liquidity": {"current_ratio", "quick_ratio"},
        }
        paragraphs = [f"FINANCIAL STATEMENT ANALYSIS — {self.company.get().strip() or 'Company'}", f"Reporting period: {self.period.get().strip() or 'Not specified'}", "", "The analysis uses the figures entered and the industry benchmarks supplied by the user. Ratios are indicative and can vary with industry definitions and accounting policies.", ""]
        for name, unit, direction, key in RATIO_META:
            value, benchmark = results[key], benchmarks[key]
            category = next(cat for cat, keys in categories.items() if key in keys)
            if value is None:
                company_text, reading = "N/A", "Not calculable"
            else:
                company_text = fmt(value, unit)
                if benchmark is None:
                    reading = "No benchmark"
                else:
                    reading = "In line" if abs(value - benchmark) < 0.005 else ("Above" if value > benchmark else "Below")
            self.table.insert("", "end", values=(category, name, company_text, fmt(benchmark, unit), reading))
            if value is None:
                paragraphs.append(f"{name}: Could not be calculated because a required denominator is zero. Check the figures.")
            elif benchmark is None:
                paragraphs.append(f"{name}: {company_text}. Add an industry benchmark to receive a comparison and interpretation.")
            else:
                insight, action = explain(name, value, benchmark, direction)
                paragraphs.append(f"{name} ({company_text}; industry {fmt(benchmark, unit)}): {insight} Possible action: {action}")
        self.report.delete("1.0", "end")
        self.report.insert("1.0", "\n\n".join(paragraphs))

    def clear(self) -> None:
        for entry in list(self.entries.values()) + list(self.benchmark_entries.values()):
            entry.delete(0, "end")
        for item in self.table.get_children():
            self.table.delete(item)
        self.report.delete("1.0", "end")
        self.report.insert("1.0", "Your analysis will appear here after you enter the financial figures and select Analyse statements.")

    def save_report(self) -> None:
        from tkinter import filedialog

        content = self.report.get("1.0", "end").strip()
        if not content or content.startswith("Your analysis will appear"):
            messagebox.showinfo("No report yet", "Analyse the statements before saving a report.")
            return
        path = filedialog.asksaveasfilename(title="Save analysis report", defaultextension=".txt", filetypes=[("Text report", "*.txt")], initialfile="financial_analysis_report.txt")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as file:
                    file.write(content)
            except OSError as error:
                messagebox.showerror("Could not save report", str(error))
                return
            messagebox.showinfo("Report saved", f"Saved report to:\n{path}")

