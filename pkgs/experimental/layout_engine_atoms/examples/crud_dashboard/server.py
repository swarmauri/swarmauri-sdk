"""FastAPI server for CRUD dashboard demo.

This demonstrates how decorator-based event handling eliminates
manual UiEvent registration - handlers are auto-discovered from decorators.
"""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI

from layout_engine_atoms import LayoutOptions, RealtimeOptions, RealtimeChannel, RealtimeBinding
from layout_engine_atoms.patterns import mount_with_auto_events

from layout_engine_atoms.examples.crud_dashboard.manifest import build_manifest

# Import handlers to trigger @ui_event decorator registration
from  layout_engine_atoms.examples.crud_dashboard import handlers


app = FastAPI(
    title="CRUD Dashboard Demo",
    description="Demonstrating decorator-based event handling at scale",
    version="1.0.0",
)


# Mount with auto-registered events from decorators
# No need to manually list events - they're discovered automatically!
mount_with_auto_events(
    app,
    manifest_builder=build_manifest,
    base_path="/",
    title="User Management Dashboard",
    layout_options=LayoutOptions(
        enable_rate_limiting=True,
        rate_limit_requests=100,
        rate_limit_window=60,
    ),
    realtime=RealtimeOptions(
        path="/ws/events",
        channels=[
            # Auto-generated channels from handler names
            RealtimeChannel(
                id="events.create_user",
                description="User creation updates",
            ),
            RealtimeChannel(
                id="events.update_user",
                description="User update notifications",
            ),
            RealtimeChannel(
                id="events.delete_user",
                description="User deletion notifications",
            ),
            RealtimeChannel(
                id="events.toggle_user_active",
                description="User status toggle notifications",
            ),
            RealtimeChannel(
                id="events.filter_users",
                description="User filter updates",
            ),
            RealtimeChannel(
                id="events.clear_filters",
                description="Clear filters notification",
            ),
            RealtimeChannel(
                id="events.load_initial_data",
                description="Initial data load",
            ),
            RealtimeChannel(
                id="events.clear_activity_log",
                description="Clear activity log",
            ),
            RealtimeChannel(
                id="events.create_admin",
                description="Create admin user",
            ),
            RealtimeChannel(
                id="events.create_guest",
                description="Create guest user",
            ),
        ],
        bindings=[
            # Bind channels to specific tiles
            RealtimeBinding(
                channel="events.create_user",
                tile_id="users_table",
                fields={"data": "users"},
            ),
            RealtimeBinding(
                channel="events.create_user",
                tile_id="total_users_badge",
                fields={"title": "total_count"},
            ),
            RealtimeBinding(
                channel="events.create_user",
                tile_id="users_count_badge",
                fields={"title": "user_count"},
            ),
            RealtimeBinding(
                channel="events.create_user",
                tile_id="admin_count_badge",
                fields={"title": "admin_count"},
            ),
            RealtimeBinding(
                channel="events.create_user",
                tile_id="stats_panel",
                fields={"items": "stats"},
            ),
            # Create admin bindings
            RealtimeBinding(
                channel="events.create_admin",
                tile_id="users_table",
                fields={"data": "users"},
            ),
            RealtimeBinding(
                channel="events.create_admin",
                tile_id="total_users_badge",
                fields={"title": "total_count"},
            ),
            RealtimeBinding(
                channel="events.create_admin",
                tile_id="users_count_badge",
                fields={"title": "user_count"},
            ),
            RealtimeBinding(
                channel="events.create_admin",
                tile_id="admin_count_badge",
                fields={"title": "admin_count"},
            ),
            RealtimeBinding(
                channel="events.create_admin",
                tile_id="stats_panel",
                fields={"items": "stats"},
            ),
            RealtimeBinding(
                channel="events.create_admin",
                tile_id="activity_log",
                fields={"items": "items"},
            ),
            # Create guest bindings
            RealtimeBinding(
                channel="events.create_guest",
                tile_id="users_table",
                fields={"data": "users"},
            ),
            RealtimeBinding(
                channel="events.create_guest",
                tile_id="total_users_badge",
                fields={"title": "total_count"},
            ),
            RealtimeBinding(
                channel="events.create_guest",
                tile_id="users_count_badge",
                fields={"title": "user_count"},
            ),
            RealtimeBinding(
                channel="events.create_guest",
                tile_id="admin_count_badge",
                fields={"title": "admin_count"},
            ),
            RealtimeBinding(
                channel="events.create_guest",
                tile_id="guest_count_badge",
                fields={"title": "guest_count"},
            ),
            RealtimeBinding(
                channel="events.create_guest",
                tile_id="stats_panel",
                fields={"items": "stats"},
            ),
            RealtimeBinding(
                channel="events.create_guest",
                tile_id="activity_log",
                fields={"items": "items"},
            ),
            RealtimeBinding(
                channel="events.update_user",
                tile_id="users_table",
                fields={"data": "users"},
            ),
            RealtimeBinding(
                channel="events.update_user",
                tile_id="total_users_badge",
                fields={"title": "total_count"},
            ),
            RealtimeBinding(
                channel="events.update_user",
                tile_id="users_count_badge",
                fields={"title": "user_count"},
            ),
            RealtimeBinding(
                channel="events.update_user",
                tile_id="admin_count_badge",
                fields={"title": "admin_count"},
            ),
            RealtimeBinding(
                channel="events.update_user",
                tile_id="stats_panel",
                fields={"items": "stats"},
            ),
            RealtimeBinding(
                channel="events.delete_user",
                tile_id="users_table",
                fields={"data": "users"},
            ),
            RealtimeBinding(
                channel="events.delete_user",
                tile_id="total_users_badge",
                fields={"title": "total_count"},
            ),
            RealtimeBinding(
                channel="events.delete_user",
                tile_id="users_count_badge",
                fields={"title": "user_count"},
            ),
            RealtimeBinding(
                channel="events.delete_user",
                tile_id="admin_count_badge",
                fields={"title": "admin_count"},
            ),
            RealtimeBinding(
                channel="events.delete_user",
                tile_id="stats_panel",
                fields={"items": "stats"},
            ),
            RealtimeBinding(
                channel="events.toggle_user_active",
                tile_id="users_table",
                fields={"data": "users"},
            ),
            RealtimeBinding(
                channel="events.toggle_user_active",
                tile_id="users_count_badge",
                fields={"title": "user_count"},
            ),
            RealtimeBinding(
                channel="events.toggle_user_active",
                tile_id="admin_count_badge",
                fields={"title": "admin_count"},
            ),
            RealtimeBinding(
                channel="events.toggle_user_active",
                tile_id="stats_panel",
                fields={"items": "stats"},
            ),
            RealtimeBinding(
                channel="events.filter_users",
                tile_id="users_table",
                fields={"data": "users"},
            ),
            RealtimeBinding(
                channel="events.filter_users",
                tile_id="guest_count_badge",
                fields={"title": "guest_count"},
            ),
            RealtimeBinding(
                channel="events.clear_filters",
                tile_id="users_table",
                fields={"data": "users"},
            ),
            RealtimeBinding(
                channel="events.clear_filters",
                tile_id="total_users_badge",
                fields={"title": "total_count"},
            ),
            RealtimeBinding(
                channel="events.clear_filters",
                tile_id="users_count_badge",
                fields={"title": "user_count"},
            ),
            RealtimeBinding(
                channel="events.clear_filters",
                tile_id="admin_count_badge",
                fields={"title": "admin_count"},
            ),
            RealtimeBinding(
                channel="events.clear_filters",
                tile_id="guest_count_badge",
                fields={"title": "guest_count"},
            ),
            RealtimeBinding(
                channel="events.clear_filters",
                tile_id="stats_panel",
                fields={"items": "stats"},
            ),
            RealtimeBinding(
                channel="events.load_initial_data",
                tile_id="users_table",
                fields={"data": "users"},
            ),
            RealtimeBinding(
                channel="events.load_initial_data",
                tile_id="total_users_badge",
                fields={"title": "total_count"},
            ),
            RealtimeBinding(
                channel="events.load_initial_data",
                tile_id="users_count_badge",
                fields={"title": "user_count"},
            ),
            RealtimeBinding(
                channel="events.load_initial_data",
                tile_id="admin_count_badge",
                fields={"title": "admin_count"},
            ),
            RealtimeBinding(
                channel="events.load_initial_data",
                tile_id="guest_count_badge",
                fields={"title": "guest_count"},
            ),
            RealtimeBinding(
                channel="events.load_initial_data",
                tile_id="stats_panel",
                fields={"items": "stats"},
            ),
            # Activity log bindings
            RealtimeBinding(
                channel="events.create_user",
                tile_id="activity_log",
                fields={"items": "items"},
            ),
            RealtimeBinding(
                channel="events.update_user",
                tile_id="activity_log",
                fields={"items": "items"},
            ),
            RealtimeBinding(
                channel="events.delete_user",
                tile_id="activity_log",
                fields={"items": "items"},
            ),
            RealtimeBinding(
                channel="events.load_initial_data",
                tile_id="activity_log",
                fields={"items": "items"},
            ),
            RealtimeBinding(
                channel="events.clear_activity_log",
                tile_id="activity_log",
                fields={"items": "items"},
            ),
        ],
        auto_subscribe=True,
    ),
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "CRUD Dashboard"}


if __name__ == "__main__":
    print("=" * 60)
    print("CRUD Dashboard Demo")
    print("=" * 60)
    print("Demonstrating decorator-based event handling:")
    print("  - 30 interactive components")
    print("  - 8 event handlers with @ui_event decorator")
    print("  - Zero manual UiEvent registration")
    print("  - Type-safe Pydantic payloads")
    print("  - Auto-generated channels")
    print("=" * 60)
    print("\nStarting server at http://localhost:8000")
    print("Open your browser to see the dashboard")
    print("=" * 60)

    uvicorn.run(
        "layout_engine_atoms.examples.crud_dashboard.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
