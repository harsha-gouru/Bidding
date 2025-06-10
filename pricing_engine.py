"""Pure calculation engine – contains no I/O or LLM calls."""
from dataclasses import dataclass
from typing import List, Dict, Any

from schema import LineItem

__all__ = [
    "Rates",
    "RATES",
    "price_line",
    "price_bid",
]


@dataclass(frozen=True)
class Rates:
    burden_incl: float  # $/mhr including burden
    fringe: float  # $/mhr fringe (currently unused in sale calc but kept for audit)
    total_mhr_sale: float  # sell rate $/mhr for customer pricing


# Master rate table (extend if needed)
RATES: Dict[str, Rates] = {
    "Regular": Rates(40.00, 0.00, 57.47),
    "Communication": Rates(77.15, 32.00, 110.44),
    "Electrical": Rates(89.13, 36.00, 127.53),
    "Plumbing": Rates(93.84, 36.00, 134.25),
}


def price_line(item: LineItem, rates: Rates) -> Dict[str, Any]:
    """Return cost / sale breakdown for one line item."""

    labor_unit_hr = item.minutes_per_unit / 60
    labor_unit_sale = labor_unit_hr * rates.total_mhr_sale
    labor_total_sale = labor_unit_sale * item.quantity

    man_hours = labor_unit_hr * item.quantity

    material_cost = item.mto_cost_unit * item.quantity
    material_sale_unit = item.mto_cost_unit * item.mto_mu
    material_sale = material_sale_unit * item.quantity

    return {
        "name": item.name,
        "quantity": item.quantity,
        "labor_unit_sale": labor_unit_sale,
        "labor_total_sale": labor_total_sale,
        "man_hours": man_hours,
        "material_cost": material_cost,
        "material_sale": material_sale,
    }


def price_bid(items: List[LineItem], bid_type: str, tax_percent: float) -> Dict[str, Any]:
    """Aggregate line pricing and compute bid totals."""

    if bid_type not in RATES:
        raise ValueError(f"Unsupported bid_type '{bid_type}'. Allowed: {list(RATES)}")

    rates = RATES[bid_type]

    details = [price_line(i, rates) for i in items]

    labor = sum(d["labor_total_sale"] for d in details)
    material = sum(d["material_sale"] for d in details)
    tax = material * tax_percent
    total = labor + material + tax

    return {
        "lines": details,
        "labor": labor,
        "material": material,
        "tax": tax,
        "total": total,
        "bid_type": bid_type,
        "tax_percent": tax_percent,
    } 