"""Unit tests for per-item label quantity helpers (stdlib only)."""

from __future__ import annotations

import unittest
from decimal import Decimal
from types import SimpleNamespace

from .quantities import expand_items_by_quantity, resolve_item_label_count


class ResolveItemLabelCountTests(unittest.TestCase):
    def test_uniform_uses_default_count(self) -> None:
        item = SimpleNamespace(quantity=Decimal("12"))
        self.assertEqual(resolve_item_label_count(item, "uniform", 3), 3)

    def test_stock_quantity_uses_item_quantity(self) -> None:
        item = SimpleNamespace(quantity=Decimal("5.2"))
        self.assertEqual(resolve_item_label_count(item, "stock_quantity", 1), 6)

    def test_stock_quantity_falls_back_without_quantity(self) -> None:
        item = SimpleNamespace(name="no-qty")
        self.assertEqual(resolve_item_label_count(item, "stock_quantity", 2), 2)

    def test_stock_quantity_supports_part_total_stock(self) -> None:
        item = SimpleNamespace(total_stock=Decimal("4"))
        self.assertEqual(resolve_item_label_count(item, "stock_quantity", 1), 4)

    def test_stock_quantity_supports_callable_total_stock(self) -> None:
        item = SimpleNamespace(total_stock=lambda: 7)
        self.assertEqual(resolve_item_label_count(item, "stock_quantity", 1), 7)

    def test_zero_stock_quantity_prints_nothing_for_item(self) -> None:
        item = SimpleNamespace(quantity=0)
        self.assertEqual(resolve_item_label_count(item, "stock_quantity", 5), 0)


class ExpandItemsByQuantityTests(unittest.TestCase):
    def test_expand_mixed_stock_quantities(self) -> None:
        items = [
            SimpleNamespace(pk=1, quantity=3),
            SimpleNamespace(pk=2, quantity=1),
            SimpleNamespace(pk=3, quantity=2),
        ]
        expanded = expand_items_by_quantity(items, "stock_quantity", 1)
        self.assertEqual([item.pk for item in expanded], [1, 1, 1, 2, 3, 3])

    def test_expand_uniform(self) -> None:
        items = [SimpleNamespace(pk=1), SimpleNamespace(pk=2)]
        expanded = expand_items_by_quantity(items, "uniform", 2)
        self.assertEqual([item.pk for item in expanded], [1, 1, 2, 2])


if __name__ == "__main__":
    unittest.main()
