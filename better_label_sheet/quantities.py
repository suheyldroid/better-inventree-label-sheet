"""
Helpers for resolving how many labels to print for each selected item.
"""

from __future__ import annotations

import math
from typing import Mapping


def extract_stock_quantity(item: object) -> float | None:
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


def stock_quantity_as_label_count(item: object, fallback: int = 1) -> int:
    """Return ceil(stock quantity) for an item, or fallback when unavailable."""
    if fallback < 0:
        raise ValueError("fallback must be >= 0")

    quantity = extract_stock_quantity(item)
    if quantity is None:
        return fallback

    return max(0, int(math.ceil(quantity)))


def item_display_name(item: object) -> str:
    """Build a short human-readable label for a selected item."""
    part = getattr(item, "part", None)
    if part is not None:
        part_name = (
            getattr(part, "full_name", None)
            or getattr(part, "name", None)
            or str(part)
        )
        serial = getattr(item, "serial", None)
        batch = getattr(item, "batch", None)
        suffix = serial or batch or getattr(item, "pk", "")
        return f"{part_name} [{suffix}]"

    for attr_name in ("full_name", "name"):
        value = getattr(item, attr_name, None)
        if isinstance(value, str) and value.strip():
            return value

    return str(item)


def resolve_item_label_count(
    item: object,
    overrides: Mapping[str, int] | None,
    fallback: int,
) -> int:
    """Return how many labels to print for a single selected item.

    Prefers an explicit per-item override (editable UI values). Otherwise uses
    the item's stock quantity, falling back to ``fallback``.
    """
    if fallback < 0:
        raise ValueError("fallback must be >= 0")

    if overrides is not None:
        key = str(getattr(item, "pk", ""))
        if key in overrides:
            count = int(overrides[key])
            if count < 0:
                raise ValueError("override counts must be >= 0")
            return count

    return stock_quantity_as_label_count(item, fallback=fallback)


def expand_items_by_quantity(
    items: list[object],
    overrides: Mapping[str, int] | None,
    fallback: int,
) -> list[object]:
    """Expand selected items into a flat label list using per-item counts."""
    expanded: list[object] = []
    for item in items:
        count = resolve_item_label_count(item, overrides, fallback)
        expanded.extend([item] * count)
    return expanded


def normalize_item_quantity_overrides(raw: object) -> dict[str, int] | None:
    """Normalize serializer output for per-item quantities into ``{pk: count}``."""
    if raw is None or raw == "":
        return None

    if not isinstance(raw, Mapping):
        raise ValueError("item_quantities must be an object mapping item ID to count")

    overrides: dict[str, int] = {}
    for key, value in raw.items():
        overrides[str(key)] = int(value)
    return overrides
