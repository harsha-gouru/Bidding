"""Typed data models for bidding estimator."""
from typing import List, Literal

from pydantic import BaseModel, Field, PositiveInt, NonNegativeFloat

__all__ = [
    "LineItem",
    "BidInput",
]


class LineItem(BaseModel):
    """Single material / labor line item."""

    name: str
    quantity: PositiveInt
    mto_cost_unit: NonNegativeFloat
    minutes_per_unit: PositiveInt
    mto_mu: float = Field(1.2, gt=0, description="Material markup factor")


class BidInput(BaseModel):
    """Complete bid request parsed from user text."""

    bid_type: Literal["Regular", "Communication", "Electrical", "Plumbing"]
    tax_percent: float = Field(..., ge=0)
    items: List[LineItem] 