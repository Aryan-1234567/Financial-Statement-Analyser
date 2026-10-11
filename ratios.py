"""Financial ratio definitions and calculations."""

FIELDS = {
    "Revenue": ("Revenue", "Income statement"),
    "Cost of sales": ("Cost of sales", "Income statement"),
    "Operating expenses": ("Operating expenses", "Income statement"),
    "Finance costs": ("Finance costs", "Income statement"),
    "Tax expense": ("Tax expense", "Income statement"),
    "Current assets": ("Current assets", "Statement of financial position"),
    "Inventory": ("Inventory", "Statement of financial position"),
    "Trade receivables": ("Trade receivables", "Statement of financial position"),
    "Cash and cash equivalents": ("Cash and cash equivalents", "Statement of financial position"),
    "Current liabilities": ("Current liabilities", "Statement of financial position"),
    "Trade payables": ("Trade payables", "Statement of financial position"),
    "Total assets": ("Total assets", "Statement of financial position"),
    "Total equity": ("Total equity", "Statement of financial position"),
    "Total borrowings": ("Total borrowings", "Statement of financial position"),
}

# A higher result is generally favourable unless marked lower or context.
RATIO_META = [
    ("Gross profit margin", "%", "higher", "gross_margin"),
    ("Operating profit margin", "%", "higher", "operating_margin"),
    ("Net profit margin", "%", "higher", "net_margin"),
    ("Return on assets", "%", "higher", "roa"),
    ("Return on equity", "%", "higher", "roe"),
    ("Inventory turnover", "x", "higher", "inventory_turnover"),
    ("Trade receivable days", "days", "lower", "receivable_days"),
    ("Trade payable days", "days", "context", "payable_days"),
    ("Total asset turnover", "x", "higher", "asset_turnover"),
    ("Debt-to-equity", "x", "lower", "debt_equity"),
    ("Gearing", "%", "lower", "gearing"),
    ("Current ratio", "x", "higher", "current_ratio"),
    ("Quick ratio", "x", "higher", "quick_ratio"),
]


def _divide(numerator: float, denominator: float) -> float | None:
    """Return None for undefined ratios instead of raising ZeroDivisionError."""
    return numerator / denominator if denominator else None


def compute_ratios(values: dict[str, float]) -> dict[str, float | None]:
    """Calculate ratios from statement values expressed in consistent units."""
    revenue = values["Revenue"]
    gross_profit = revenue - values["Cost of sales"]
    operating_profit = gross_profit - values["Operating expenses"]
    profit_before_tax = operating_profit - values["Finance costs"]
    net_profit = profit_before_tax - values["Tax expense"]
    return {
        "gross_margin": _divide(gross_profit * 100, revenue),
        "operating_margin": _divide(operating_profit * 100, revenue),
        "net_margin": _divide(net_profit * 100, revenue),
        "roa": _divide(net_profit * 100, values["Total assets"]),
        "roe": _divide(net_profit * 100, values["Total equity"]),
        "inventory_turnover": _divide(values["Cost of sales"], values["Inventory"]),
        "receivable_days": _divide(values["Trade receivables"] * 365, revenue),
        "payable_days": _divide(values["Trade payables"] * 365, values["Cost of sales"]),
        "asset_turnover": _divide(revenue, values["Total assets"]),
        "debt_equity": _divide(values["Total borrowings"], values["Total equity"]),
        "gearing": _divide(values["Total borrowings"] * 100, values["Total borrowings"] + values["Total equity"]),
        "current_ratio": _divide(values["Current assets"], values["Current liabilities"]),
        "quick_ratio": _divide(values["Current assets"] - values["Inventory"], values["Current liabilities"]),
    }


def fmt(value: float | None, unit: str) -> str:
    """Format a ratio using the unit shown in the interface."""
    if value is None:
        return "N/A"
    if unit == "%":
        return f"{value:.1f}%"
    if unit == "days":
        return f"{value:.1f} days"
    return f"{value:.2f}x"
