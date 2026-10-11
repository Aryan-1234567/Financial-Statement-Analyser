"""Plain-English interpretations and possible improvement actions."""


_MEANINGS_AND_ACTIONS = {
    "Gross profit margin": ("the share of sales remaining after direct production or purchase costs", "Review supplier terms, purchasing, waste, pricing and product mix."),
    "Operating profit margin": ("the share of sales left after operating costs, before finance and tax", "Review overheads and operating processes, and assess whether pricing and sales mix cover costs."),
    "Net profit margin": ("the share of sales retained as profit after finance costs and tax", "Review operating costs, borrowing costs and tax planning; check whether pricing reflects total costs."),
    "Return on assets": ("how effectively the asset base generates profit", "Improve asset utilisation, address idle capacity and focus investment on productive assets."),
    "Return on equity": ("the accounting return generated on shareholders' funds", "Improve sustainable earnings and use capital efficiently; consider whether leverage is increasing risk."),
    "Inventory turnover": ("how quickly inventory is sold or used during the period", "Review slow-moving stock, purchasing quantities, demand forecasts and production planning."),
    "Trade receivable days": ("the approximate time taken to collect customer balances", "Tighten credit checks, invoice promptly, follow up overdue accounts and review payment terms."),
    "Trade payable days": ("the approximate time taken to pay suppliers", "Compare payment timing with agreed terms and cash needs; preserve supplier relationships and avoid late fees."),
    "Total asset turnover": ("how much revenue is generated per unit of assets", "Review underused assets, capacity and sales productivity before committing to additional assets."),
    "Debt-to-equity": ("borrowings relative to shareholders' equity", "Consider debt repayment, retained earnings or new equity, while protecting investment and liquidity needs."),
    "Gearing": ("the proportion of debt plus equity funding represented by borrowings", "Assess debt affordability, cash-flow resilience and options to reduce borrowing or strengthen equity."),
    "Current ratio": ("short-term assets available relative to short-term liabilities", "Improve cash collection, manage working capital and plan short-term obligations."),
    "Quick ratio": ("liquid current assets available to meet short-term liabilities, excluding inventory", "Improve cash collection and cash planning, and manage short-term liabilities; inventory may not convert quickly."),
}


def explain(name: str, value: float, benchmark: float, direction: str) -> tuple[str, str]:
    """Return the benchmark interpretation and suggested action for a ratio."""
    difference = value - benchmark
    if abs(difference) < 0.005:
        comparison, favourable = "in line with", None
    elif difference > 0:
        comparison, favourable = "above", direction == "higher"
    else:
        comparison, favourable = "below", direction == "lower"

    meaning, action = _MEANINGS_AND_ACTIONS[name]
    if direction == "context":
        judgement = (
            "This is a context-dependent result; longer payment times can support cash flow "
            "but may strain supplier relationships. Compare it with agreed terms and the company's cash position."
        )
    elif favourable is True:
        judgement = "This is generally favourable against the benchmark."
    elif favourable is False:
        judgement = "This may indicate an area to investigate against the benchmark."
    else:
        judgement = "This is broadly in line with the benchmark."
    insight = f"{name} is {comparison} the industry benchmark. It measures {meaning}. {judgement}"
    return insight, action
