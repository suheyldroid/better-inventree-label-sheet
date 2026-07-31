"""
Helpers for resolving how many labels to print for each selected item.
"""

from __future__ import annotations

import math
from typing import Literal

QuantityMode = Literal["uniform", "stock_quantity"]

QUANTITY_MODE_CHOICES: list[tuple[str, str]] = [
    ("uniform", "Same count for every selected item"),
    ("stock_quantity", "Use each item's stock quantity"),
]


def resolve_item_label_count(
    item: object,
    quantity_mode: str,
    default_count: int,
) -> int:
    """Return how many labels to print for a single selected item.

    Args:
        item: Database model instance passed to the label template (e.g. StockItem).
        quantity_mode: ``uniform`` or ``stock_quantity``.
        default_count: Fallback / uniform count from the print dialog.

    Returns:
        Non-negative integer label count for this item.
    """
    if default_count < 0:
        raise ValueError("default_count must be >= 0")

    if quantity_mode != "stock_quantity":
        return default_count

    quantity = _extract_stock_quantity(item)
    if quantity is None:
        return default_count

    # Round up fractional stock so partial units still get a label.
    return max(0, int(math.ceil(quantity)))


def expand_items_by_quantity(
    items: list[object],
    quantity_mode: str,
    default_count: int,
) -> list[object]:
    """Expand selected items into a flat label list according to quantity mode."""
    expanded: list[object] = []
    for item in items:
        count = resolve_item_label_count(item, quantity_mode, default_count)
        expanded.extend([item] * count)
    return expanded


def _extract_stock_quantity(item: object) -> float | None:
    """Best-effort extraction of a numeric stock quantity from an item.

    Supports common InvenTree models:
    - StockItem.quantity
    - Part.total_stock
    """
    for attr_name in ("quantity", "total_stock"):
        if not hasattr(item, attr_name):
            continue
        raw = getattr(item, attr_name)
        if raw is None:
            continue
        # Some Part APIs expose total_stock as a callable property/method.
        if callable(raw):
            raw = raw()
        try:
            return float(raw)
        except (TypeError, ValueError):
            continue
    return None
