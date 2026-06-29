"""
API views for the Better Label Printer plugin.

These views back the layout editor UI panel, exposing the editable sheet
layouts stored in the plugin's CUSTOM_LAYOUTS setting.
"""

from __future__ import annotations

import logging

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .layouts import SheetLayout, serialize_layouts

_log = logging.getLogger("better-inventree-label-sheet")


class LayoutsView(APIView):
    """GET/PUT the editable sheet layouts for the plugin.

    GET  -> returns the current layouts as a JSON object keyed by layout code.
    PUT  -> validates and persists a new set of layouts.
    """

    permission_classes = [permissions.IsAuthenticated]

    # Bound to the plugin instance when constructing the URL pattern (via
    # as_view(plugin=self)) so the view can read/write the plugin's settings.
    # Declared here so Django's View.as_view() accepts it as an init kwarg.
    plugin = None

    def get(self, request, *args, **kwargs):
        layouts = self.plugin.get_layouts()
        return Response({code: layout.to_dict() for code, layout in layouts.items()})

    def put(self, request, *args, **kwargs):
        # Only superusers may modify the global layout definitions.
        if not request.user.is_superuser:
            return Response(
                {"error": "Only administrators may edit layouts."},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data

        if not isinstance(data, dict):
            return Response(
                {"error": "Expected a JSON object mapping layout code -> layout."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(data) == 0:
            return Response(
                {"error": "At least one layout is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate every layout before persisting anything so a single bad
        # entry doesn't leave the stored layouts in a half-written state.
        validated: dict[str, SheetLayout] = {}
        errors: dict[str, str] = {}
        for code, layout_data in data.items():
            try:
                validated[str(code)] = SheetLayout.from_dict(layout_data)
            except ValueError as exc:
                errors[str(code)] = str(exc)

        if errors:
            return Response(
                {"error": "One or more layouts are invalid.", "details": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.plugin.set_setting("CUSTOM_LAYOUTS", serialize_layouts(validated))

        return Response({code: layout.to_dict() for code, layout in validated.items()})
