"""
ELEKTRON (c) 2024 - now
Written by melektron
www.elektron.work
18.07.24 22:42

List of sheet label paper layouts
"""

import dataclasses
import json
import logging
from typing import Optional

_log = logging.getLogger("better-inventree-label-sheet")


@dataclasses.dataclass
class PaperSize:
    display_name: str  # paper size display name (e.g. "A4")
    width: float  # mm
    height: float  # mm


@dataclasses.dataclass
class SheetLayout:
    display_name: str
    page_size: PaperSize
    label_width: float  # mm
    label_height: float  # mm
    columns: int
    rows: int
    column_spacing: float  # mm
    row_spacing: float  # mm
    corner_radius: float  # mm, 0 means sharp corners
    spacing_top: Optional[float] = None  # None means automatic centering
    spacing_left: Optional[float] = None  # None means automatic centering

    @property
    def cells(self) -> int:
        return self.rows * self.columns

    @property
    def spacing_top_computed(self) -> float:
        if self.spacing_top is not None:
            return self.spacing_top
        else:
            return (
                self.page_size.height
                - (self.label_height * self.rows + self.row_spacing * (self.rows - 1))
            ) / 2

    def row_position_top(self, row: int) -> float:
        """
        returns the distance from the top of the page
        to the top of the specified row (starting with 0)
        """
        return self.spacing_top_computed + row * (self.label_height + self.row_spacing)

    @property
    def spacing_left_computed(self) -> float:
        if self.spacing_left is not None:
            return self.spacing_left
        else:
            return (
                self.page_size.width
                - (
                    self.label_width * self.columns
                    + self.column_spacing * (self.columns - 1)
                )
            ) / 2

    def column_position_left(self, column: int) -> float:
        """
        returns the distance from the left edge of the page
        to the left edge of the specified column (starting with 0)
        """
        return self.spacing_left_computed + column * (
            self.label_width + self.column_spacing
        )

    def __str__(self) -> str:
        return f"{self.display_name} ({self.page_size.display_name}, {self.label_width}mm x {self.label_height}mm, {self.columns} columns x {self.rows} rows, {'round corners' if self.corner_radius != 0 else 'sharp corners'})"

    def to_dict(self) -> dict:
        """Serialize this layout to a plain JSON-compatible dict."""
        return {
            "display_name": self.display_name,
            "page_size": {
                "display_name": self.page_size.display_name,
                "width": self.page_size.width,
                "height": self.page_size.height,
            },
            "label_width": self.label_width,
            "label_height": self.label_height,
            "columns": self.columns,
            "rows": self.rows,
            "column_spacing": self.column_spacing,
            "row_spacing": self.row_spacing,
            "corner_radius": self.corner_radius,
            "spacing_top": self.spacing_top,
            "spacing_left": self.spacing_left,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SheetLayout":
        """Build a SheetLayout from a plain dict (e.g. parsed from JSON).

        Raises ValueError if the data is structurally invalid.
        """
        try:
            page_size_data = data["page_size"]
            page_size = PaperSize(
                display_name=str(page_size_data["display_name"]),
                width=float(page_size_data["width"]),
                height=float(page_size_data["height"]),
            )
            spacing_top = data.get("spacing_top", None)
            spacing_left = data.get("spacing_left", None)
            return cls(
                display_name=str(data["display_name"]),
                page_size=page_size,
                label_width=float(data["label_width"]),
                label_height=float(data["label_height"]),
                columns=int(data["columns"]),
                rows=int(data["rows"]),
                column_spacing=float(data["column_spacing"]),
                row_spacing=float(data["row_spacing"]),
                corner_radius=float(data["corner_radius"]),
                spacing_top=None if spacing_top is None else float(spacing_top),
                spacing_left=None if spacing_left is None else float(spacing_left),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid sheet layout data: {exc}") from exc


PAPER_SIZES = {
    "A4": PaperSize("A4", 210, 297),
    "Letter": PaperSize("Letter", 215.9, 279.4),
}

LAYOUTS = {
    "8160": SheetLayout(
        display_name="8160",
        page_size=PAPER_SIZES["Letter"],
        label_width=66.7,
        label_height=25.4,
        columns=3,
        rows=10,
        column_spacing=3.18,
        row_spacing=0,
        corner_radius=3,
        spacing_top=12.7,
        spacing_left=4.6,
    ),
    "22805": SheetLayout(
        display_name="Avery 22805",
        page_size=PAPER_SIZES["Letter"],
        label_width=37,
        label_height=37,
        columns=4,
        rows=6,
        column_spacing=8.8,  # space between two columns, not margins
        row_spacing=6.1,  # space between two rows, not margins
        corner_radius=0,  # radius of label corners
        spacing_top=12,  # Spacing of top margin
        spacing_left=20.1,  # Spacing of left margin
    ),
    "4780": SheetLayout(
        display_name="4780",
        page_size=PAPER_SIZES["A4"],
        label_width=48.5,
        label_height=25.4,
        columns=4,
        rows=10,
        column_spacing=0,
        row_spacing=0,
        corner_radius=0,
    ),
    "4737": SheetLayout(
        display_name="4737",
        page_size=PAPER_SIZES["A4"],
        label_width=63.5,
        label_height=29.6,
        columns=3,
        rows=9,
        column_spacing=2.54,
        row_spacing=0,
        corner_radius=3,
    ),
    "4201": SheetLayout(
        display_name="4201",
        page_size=PAPER_SIZES["A4"],
        label_width=45.7,
        label_height=16.9,
        columns=4,
        rows=16,
        column_spacing=2.6,
        row_spacing=0,
        corner_radius=2,
    ),
    "7120-25": SheetLayout(
        display_name="7120-25",
        page_size=PAPER_SIZES["A4"],
        label_width=35,
        label_height=35,
        columns=5,
        rows=7,
        column_spacing=5,
        row_spacing=5,
        corner_radius=0,
    ),
    "7160-10": SheetLayout(
        display_name="7160-10",
        page_size=PAPER_SIZES["A4"],
        label_width=63.5,
        label_height=38.1,
        columns=3,
        rows=7,
        column_spacing=2.54,
        row_spacing=0,
        corner_radius=2.54,
    ),
    "4360": SheetLayout(
        display_name="4360",
        page_size=PAPER_SIZES["A4"],
        label_width=70.0,
        label_height=36.0,
        columns=3,
        rows=8,
        column_spacing=0,
        row_spacing=0,
        corner_radius=0,
    ),
    "1367853": SheetLayout(
        display_name="1367853",
        page_size=PAPER_SIZES["A4"],
        label_width=48.5,
        label_height=16.9,
        columns=4,
        rows=16,
        column_spacing=0,
        row_spacing=0,
        corner_radius=0,
    ),
    "4210": SheetLayout(
        display_name="4210",
        page_size=PAPER_SIZES["A4"],
        label_width=38.1,
        label_height=12.7,
        columns=5,
        rows=22,
        column_spacing=0,
        row_spacing=0,
        corner_radius=0,
    ),
    "1367586": SheetLayout(
        display_name="1367586",
        page_size=PAPER_SIZES["A4"],
        label_width=70,
        label_height=36,
        columns=3,
        rows=8,
        column_spacing=0,
        row_spacing=0,
        corner_radius=0,
    ),
    "8724": SheetLayout(
        display_name="8724",
        page_size=PAPER_SIZES["A4"],
        label_width=46,
        label_height=11.1,
        columns=4,
        rows=21,
        column_spacing=4.8,
        row_spacing=1.6,
        corner_radius=1,
    ),
    "50x25-R": SheetLayout(
        display_name="Avery 50x25-R",
        page_size=PAPER_SIZES["A4"],
        label_width=50.0,
        label_height=25.0,
        columns=3,
        rows=8,
        column_spacing=10.0,
        row_spacing=10.0,
        corner_radius=2.0,
    ),
    "105x42-R": SheetLayout(
        display_name="Avery 105x42-R",
        page_size=PAPER_SIZES["A4"],
        label_width=105.0,
        label_height=42.0,
        columns=2,
        rows=7,
        column_spacing=0,
        row_spacing=0,
        corner_radius=0,
    ),
    "40x12-R": SheetLayout(
        display_name="Avery 40x12-R",
        page_size=PAPER_SIZES["A4"],
        label_width=40.0,
        label_height=12.0,
        columns=4,
        rows=17,
        column_spacing=5.0,
        row_spacing=5.0,
        corner_radius=2.0,
    ),
    "8698": SheetLayout(
        display_name="8698",
        page_size=PAPER_SIZES["A4"],
        label_width=52.5,
        label_height=29.7,
        columns=4,
        rows=10,
        column_spacing=0,
        row_spacing=0,
        corner_radius=0,
    ),
    "A4-2x6-full": SheetLayout(
        display_name="A4 2x6 Full Bleed",
        page_size=PAPER_SIZES["A4"],
        label_width=105.0,
        label_height=49.5,
        columns=2,
        rows=6,
        column_spacing=0,
        row_spacing=0,
        corner_radius=0,
        spacing_top=0,
        spacing_left=0,
    ),
}

# The hardcoded LAYOUTS above act as the default seed which is written to the
# database on first run. After that, the editable layouts live in the plugin's
# CUSTOM_LAYOUTS setting and are loaded via the helper functions below.
DEFAULT_LAYOUTS = LAYOUTS

# Codes for the automatic layout detection options. These are not real layouts
# but special selections handled separately during printing.
AUTO_OPTIONS = [
    (
        "auto_round",
        "Auto (round) - Automatically detect correct layout for label template according to metadata or size (prefer round-corner labels)",
    ),
    (
        "auto_sharp",
        "Auto (sharp) - Automatically detect correct layout for label template according to metadata or size (prefer sharp-corner labels)",
    ),
]


def default_layouts_json() -> str:
    """Return the default seed layouts serialized as a JSON string."""
    return serialize_layouts(DEFAULT_LAYOUTS)


def serialize_layouts(layouts: dict[str, SheetLayout]) -> str:
    """Serialize a mapping of layout code -> SheetLayout to a JSON string."""
    return json.dumps(
        {code: layout.to_dict() for code, layout in layouts.items()},
        indent=2,
    )


def parse_layouts_json(raw: str) -> dict[str, SheetLayout]:
    """Parse a JSON string into a mapping of layout code -> SheetLayout.

    Invalid individual layouts are skipped with a logged warning so a single
    bad entry doesn't break printing entirely. If the whole string is invalid
    or empty, the default seed layouts are returned instead.
    """
    if not raw or not raw.strip():
        return dict(DEFAULT_LAYOUTS)

    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        _log.warning(
            "Could not parse custom layouts JSON, falling back to defaults: %s", exc
        )
        return dict(DEFAULT_LAYOUTS)

    if not isinstance(data, dict):
        _log.warning("Custom layouts JSON is not an object, falling back to defaults.")
        return dict(DEFAULT_LAYOUTS)

    result: dict[str, SheetLayout] = {}
    for code, layout_data in data.items():
        try:
            result[str(code)] = SheetLayout.from_dict(layout_data)
        except ValueError as exc:
            _log.warning("Skipping invalid layout '%s': %s", code, exc)

    if not result:
        _log.warning("No valid custom layouts found, falling back to defaults.")
        return dict(DEFAULT_LAYOUTS)

    return result


def build_select_options(layouts: dict[str, SheetLayout]) -> list[tuple[str, str]]:
    """Build the choice options list (incl. auto options) for a set of layouts."""
    return AUTO_OPTIONS + [(code, str(layout)) for code, layout in layouts.items()]


# Backwards-compatible static options built from the default seed layouts.
# Runtime code should prefer build_select_options() with the live layouts.
LAYOUT_SELECT_OPTIONS = build_select_options(DEFAULT_LAYOUTS)
