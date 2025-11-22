"""Manifest for CRUD dashboard - 30 interactive components with minimal wiring."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import Request

from layout_engine.structure import block, col, row, table

from layout_engine_atoms.manifest import create_registry, quick_manifest_from_table, tile


def build_manifest(_request: "Request"):
    """Build the CRUD dashboard manifest with 30 components.

    This manifest demonstrates how decorator-based event handling
    eliminates the need for manual UiEvent registration and binding declarations.
    """
    registry = create_registry(catalog="vue")

    tiles = [
        # === HEADER SECTION (1 tile) ===
        tile(
            "page_header",
            "swarmakit:vue:card-header",
            span="full",
            props={
                "title": "User Management Dashboard",
                "subtitle": "Demonstrating decorator-based event handling at scale",
            },
        ),

        # === STATS BADGES SECTION (4 tiles) ===
        tile(
            "total_users_badge",
            "swarmakit:vue:card-header",
            span="half",
            props={
                "title": "0",
                "subtitle": "Total Users",
            },
        ),
        tile(
            "users_count_badge",
            "swarmakit:vue:card-header",
            span="half",
            props={
                "title": "0",
                "subtitle": "Users",
            },
        ),
        tile(
            "admin_count_badge",
            "swarmakit:vue:card-header",
            span="half",
            props={
                "title": "0",
                "subtitle": "Admins",
            },
        ),
        tile(
            "guest_count_badge",
            "swarmakit:vue:card-header",
            span="half",
            props={
                "title": "0",
                "subtitle": "Guests",
            },
        ),

        # === ACTION BUTTONS ROW 1 (2 tiles) ===
        tile(
            "refresh_btn",
            "swarmakit:vue:button",
            span="half",
            props={
                "label": "Refresh",
                "variant": "secondary",
                "icon": "refresh-cw",
                "events": {
                    "primary": {
                        "id": "load_initial_data",
                    }
                },
            },
        ),
        tile(
            "refresh_stats_btn",
            "swarmakit:vue:button",
            span="half",
            props={
                "label": "Update Stats",
                "variant": "outline",
                "icon": "bar-chart",
                "events": {
                    "primary": {
                        "id": "refresh_stats",
                    }
                },
            },
        ),

        # === FILTER SECTION (6 tiles) ===
        tile(
            "filter_header",
            "swarmakit:vue:card-header",
            span="full",
            props={
                "title": "Filters",
                "subtitle": "Refine user list",
            },
        ),
        # Filter buttons - using reliable button component
        tile(
            "filter_all_btn",
            "swarmakit:vue:button",
            span="full",
            props={
                "label": "📊 All Users",
                "variant": "primary",
                "size": "medium",
                "events": {
                    "primary": {
                        "id": "filter_users",
                        "payload": {"role": "all"},
                    }
                },
            },
        ),
        tile(
            "filter_admin_btn",
            "swarmakit:vue:button",
            span="half",
            props={
                "label": "👑 Admins",
                "variant": "secondary",
                "size": "medium",
                "events": {
                    "primary": {
                        "id": "filter_users",
                        "payload": {"role": "admin"},
                    }
                },
            },
        ),
        tile(
            "filter_user_btn",
            "swarmakit:vue:button",
            span="half",
            props={
                "label": "👤 Users",
                "variant": "secondary",
                "size": "medium",
                "events": {
                    "primary": {
                        "id": "filter_users",
                        "payload": {"role": "user"},
                    }
                },
            },
        ),
        tile(
            "filter_guest_btn",
            "swarmakit:vue:button",
            span="half",
            props={
                "label": "🎫 Guests",
                "variant": "secondary",
                "size": "medium",
                "events": {
                    "primary": {
                        "id": "filter_users",
                        "payload": {"role": "guest"},
                    }
                },
            },
        ),
        tile(
            "filter_active_btn",
            "swarmakit:vue:button",
            span="half",
            props={
                "label": "✅ Active Only",
                "variant": "secondary",
                "size": "medium",
                "events": {
                    "primary": {
                        "id": "filter_users",
                        "payload": {"role": "active"},
                    }
                },
            },
        ),
        tile(
            "filter_inactive_btn",
            "swarmakit:vue:button",
            span="half",
            props={
                "label": "⏸️ Inactive Only",
                "variant": "secondary",
                "size": "medium",
                "events": {
                    "primary": {
                        "id": "filter_users",
                        "payload": {"active": False},
                    }
                },
            },
        ),
        tile(
            "search_bar",
            "swarmakit:vue:search-bar",
            span="full",
            props={
                "placeholder": "Search by name or email...",
                "events": {
                    "search": {
                        "id": "filter_users",
                        "payload": {"search": "{{query}}"},
                    }
                },
            },
        ),
        tile(
            "filter_reset_btn",
            "swarmakit:vue:button",
            span="full",
            props={
                "label": "Reset",
                "variant": "outline",
                "size": "small",
                "events": {
                    "primary": {
                        "id": "clear_filters",
                    }
                },
            },
        ),

        # === MAIN DATA TABLE (1 large tile) ===
        tile(
            "users_table",
            "swarmakit:vue:data-grid",
            span="full",
            props={
                "headers": ["ID", "Name", "Email", "Role", "Status", "Created"],
                "columns": [
                    {"field": "id", "header": "ID", "width": 60, "sortable": True},
                    {"field": "name", "header": "Name", "width": 200, "sortable": True},
                    {"field": "email", "header": "Email", "width": 250, "sortable": True},
                    {"field": "role", "header": "Role", "width": 100, "sortable": True},
                    {
                        "field": "active",
                        "header": "Status",
                        "width": 100,
                        "sortable": True,
                    },
                    {
                        "field": "created_at",
                        "header": "Created",
                        "width": 180,
                        "sortable": True,
                    },
                ],
                "data": [],
                "selectable": True,
                "paginator": True,
                "rows": 10,
                "events": {
                    "rowSelect": {
                        "id": "update_user",
                    },
                    "rowDelete": {
                        "id": "delete_user",
                    },
                },
            },
        ),

        # === QUICK ACTION BUTTONS (4 tiles) ===
        tile(
            "quick_actions_header",
            "swarmakit:vue:card-header",
            span="full",
            props={
                "title": "Quick Actions",
                "subtitle": "Create new users",
            },
        ),
        tile(
            "create_user_btn",
            "swarmakit:vue:button",
            span="full",
            props={
                "label": "Add User",
                "variant": "primary",
                "size": "small",
                "icon": "user-plus",
                "events": {
                    "primary": {
                        "id": "create_user",
                    }
                },
            },
        ),
        tile(
            "create_admin_btn",
            "swarmakit:vue:button",
            span="half",
            props={
                "label": "Add Admin",
                "variant": "secondary",
                "size": "small",
                "events": {
                    "primary": {
                        "id": "create_admin",
                    }
                },
            },
        ),
        tile(
            "create_guest_btn",
            "swarmakit:vue:button",
            span="half",
            props={
                "label": "Add Guest",
                "variant": "secondary",
                "size": "small",
                "events": {
                    "primary": {
                        "id": "create_guest",
                    }
                },
            },
        ),

        # === ACTIVITY LOG (3 tiles) ===
        tile(
            "activity_header",
            "swarmakit:vue:card-header",
            span="full",
            props={
                "title": "Recent Activity",
                "subtitle": "Last 10 operations",
            },
        ),
        tile(
            "activity_log",
            "swarmakit:vue:actionable-list",
            span="full",
            props={
                "items": [
                    {"label": "Welcome to the User Management Dashboard", "actionLabel": ""},
                    {"label": "Click 'Refresh' to load initial data", "actionLabel": ""},
                ],
            },
        ),
        tile(
            "clear_log_btn",
            "swarmakit:vue:button",
            span="full",
            props={
                "label": "Clear Activity Log",
                "variant": "outline",
                "size": "small",
                "events": {
                    "primary": {
                        "id": "clear_activity_log",
                    }
                },
            },
        ),
    ]

    # Create structured layout using table
    layout = table(
        # Header (full width)
        row(col(block("page_header")), height_rows=1),

        # Stats badges (4 columns)
        row(
            col(block("total_users_badge")),
            col(block("users_count_badge")),
            col(block("admin_count_badge")),
            col(block("guest_count_badge")),
            height_rows=1,
        ),

        # Action buttons
        row(
            col(block("refresh_btn")),
            col(block("refresh_stats_btn")),
            height_rows=1,
        ),

        # Filter section
        row(col(block("filter_header")), height_rows=1),
        row(col(block("filter_all_btn")), height_rows=1),
        row(
            col(block("filter_admin_btn")),
            col(block("filter_user_btn")),
            height_rows=1,
        ),
        row(
            col(block("filter_guest_btn")),
            col(block("filter_active_btn")),
            height_rows=1,
        ),
        row(col(block("filter_inactive_btn")), height_rows=1),
        row(col(block("search_bar")), height_rows=1),
        row(col(block("filter_reset_btn")), height_rows=1),

        # Main data table (full width, taller)
        row(col(block("users_table")), height_rows=3),

        # Quick actions section
        row(col(block("quick_actions_header")), height_rows=1),
        row(col(block("create_user_btn")), height_rows=1),
        row(
            col(block("create_admin_btn")),
            col(block("create_guest_btn")),
            height_rows=1,
        ),

        # Activity log section
        row(col(block("activity_header")), height_rows=1),
        row(col(block("activity_log")), height_rows=2),
        row(col(block("clear_log_btn")), height_rows=1),
    )

    # Build manifest with structured layout
    return quick_manifest_from_table(layout, tiles, registry=registry, row_height=80)
