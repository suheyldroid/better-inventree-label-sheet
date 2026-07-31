"""Unit tests for per-item label quantity helpers (stdlib only)."""

from __future__ import annotations

import unittest
from decimal import Decimal
from types import SimpleNamespace

from .quantities import (
    expand_items_by_quantity,
    item_display_name,
    normalize_item_quantity_overrides,
    resolve_item_label_count,
    stock_quantity_as_label_count,
)


class StockQuantityTests(unittest.TestCase):
    def test_uses_item_quantity(self) -> None:
        item = SimpleNamespace(quantity=Decimal("5.2"))
        self.assertEqual(stock_quantity_as_label_count(item, fallback=1), 6)

    def test_falls_back_without_quantity(self) -> None:
        item = SimpleNamespace(name="no-qty")
        self.assertEqual(stock_quantity_as_label_count(item, fallback=2), 2)

    def test_supports_part_total_stock(self) -> None:
        item = SimpleNamespace(total_stock=Decimal("4"))
        self.assertEqual(stock_quantity_as_label_count(item, fallback=1), 4)

    def test_supports_callable_total_stock(self) -> None:
        item = SimpleNamespace(total_stock=lambda: 7)
        self.assertEqual(stock_quantity_as_label_count(item, fallback=1), 7)


class ResolveItemLabelCountTests(unittest.TestCase):
    def test_override_wins_over_stock_quantity(self) -> None:
        item = SimpleNamespace(pk=12, quantity=Decimal("9"))
        self.assertEqual(
            resolve_item_label_count(item, {"12": 3}, fallback=1),
            3,
        )

    def test_stock_quantity_used_without_override(self) -> None:
        item = SimpleNamespace(pk=12, quantity=Decimal("4"))
        self.assertEqual(resolve_item_label_count(item, None, fallback=1), 4)

    def test_fallback_when_no_stock_or_override(self) -> None:
        item = SimpleNamespace(pk=12)
        self.assertEqual(resolve_item_label_count(item, {}, fallback=2), 2)


class ExpandItemsByQuantityTests(unittest.TestCase):
    def test_expand_with_editable_overrides(self) -> None:
        items = [
            SimpleNamespace(pk=1, quantity=3),
            SimpleNamespace(pk=2, quantity=8),
            SimpleNamespace(pk=3, quantity=2),
        ]
        expanded = expand_items_by_quantity(items, {"1": 2, "2": 1}, fallback=1)
        self.assertEqual([item.pk for item in expanded], [1, 1, 2, 3, 3])

    def test_expand_defaults_to_stock_quantity(self) -> None:
        items = [SimpleNamespace(pk=1, quantity=2), SimpleNamespace(pk=2, quantity=1)]
        expanded = expand_items_by_quantity(items, None, fallback=1)
        self.assertEqual([item.pk for item in expanded], [1, 1, 2])


class NormalizeOverridesTests(unittest.TestCase):
    def test_normalize_mapping(self) -> None:
        self.assertEqual(
            normalize_item_quantity_overrides({"12": 3, 45: 1}),
            {"12": 3, "45": 1},
        )

    def test_normalize_empty(self) -> None:
        self.assertIsNone(normalize_item_quantity_overrides(None))
        self.assertIsNone(normalize_item_quantity_overrides(""))


class ItemDisplayNameTests(unittest.TestCase):
    def test_stock_item_style_name(self) -> None:
        item = SimpleNamespace(
            pk=9,
            part=SimpleNamespace(name="Resistor"),
            serial="SN-1",
            batch=None,
        )
        self.assertEqual(item_display_name(item), "Resistor [SN-1]")


if __name__ == "__main__":
    unittest.main()
