"""Event handlers using decorator pattern - showcases zero-boilerplate event registration."""

from __future__ import annotations

from fastapi import Request

from layout_engine_atoms.patterns import ui_event, returns_update

from .database import db
from .models import (
    CreateUserPayload,
    UpdateUserPayload,
    DeleteUserPayload,
    ToggleUserPayload,
    FilterUsersPayload,
)


def get_stats_for_badges(stats: dict) -> dict:
    """Transform stats dict into individual badge count fields.

    Args:
        stats: Dict with keys: total, active, inactive, by_role

    Returns:
        Dict with individual count fields for each badge (as strings for Vue components)
    """
    return {
        "stat_total_count": str(stats["total"]),
        "stat_active_count": str(stats["active"]),
        "stat_inactive_count": str(stats["inactive"]),
        "stat_admin_count": str(stats["by_role"]["admin"]),
        "stat_user_count": str(stats["by_role"]["user"]),
        "stat_guest_count": str(stats["by_role"]["guest"]),
    }


@ui_event
@returns_update("users_table", "total_users_badge", "users_count_badge", "admin_count_badge", "stat_total_badge", "stat_active_badge", "stat_inactive_badge", "stat_admin_badge", "stat_user_badge", "stat_guest_badge", "activity_log")
async def create_user(request: Request, payload: dict):
    """Create a new user."""
    import random
    import logging

    logger = logging.getLogger(__name__)
    logger.info(f"create_user called with payload: {payload}")

    # Handle missing fields with defaults
    name = payload.get("name", f"User_{random.randint(1000, 9999)}")
    email = payload.get("email", f"user{random.randint(1000, 9999)}@example.com")
    role = payload.get("role", "user")

    logger.info(f"Extracted role: {role}")

    # Ensure role is a string that Pydantic can validate
    if isinstance(role, str):
        role = role.lower()  # Normalize to lowercase

    logger.info(f"Normalized role: {role}")

    # Validate with Pydantic
    validated = CreateUserPayload(name=name, email=email, role=role)

    logger.info(f"Validated role: {validated.role}")

    user = db.create_user(
        name=validated.name,
        email=validated.email,
        role=validated.role,
    )

    logger.info(f"Created user with role: {user.role}")

    # Log activity
    db.log_activity("Created", f"User '{user.name}' ({user.email}) - Role: {user.role}")

    stats = db.get_stats()

    return {
        "users": [u.model_dump(mode='json') for u in db.get_all_users()],
        "total_count": str(stats["total"]),
        "user_count": str(stats["by_role"]["user"]),
        "admin_count": str(stats["by_role"]["admin"]),
        "guest_count": str(stats["by_role"]["guest"]),
        **get_stats_for_badges(stats),
        "items": [{"label": log, "actionLabel": ""} for log in db.get_activity_log()],
        "message": f"User '{user.name}' created successfully",
        "message_type": "success",
    }


@ui_event
@returns_update("users_table", "total_users_badge", "users_count_badge", "admin_count_badge", "stat_total_badge", "stat_active_badge", "stat_inactive_badge", "stat_admin_badge", "stat_user_badge", "stat_guest_badge", "activity_log")
async def update_user(request: Request, payload: UpdateUserPayload):
    """Update an existing user."""
    user = db.update_user(
        user_id=payload.user_id,
        name=payload.name,
        email=payload.email,
        role=payload.role,
        active=payload.active,
    )

    if not user:
        return {
            "error": "User not found",
            "message": f"User with ID {payload.user_id} not found",
            "message_type": "error",
        }

    # Log activity
    db.log_activity("Updated", f"User '{user.name}' (ID: {user.id})")

    stats = db.get_stats()

    return {
        "users": [u.model_dump(mode='json') for u in db.get_all_users()],
        "total_count": str(stats["total"]),
        "user_count": str(stats["by_role"]["user"]),
        "admin_count": str(stats["by_role"]["admin"]),
        "guest_count": str(stats["by_role"]["guest"]),
        **get_stats_for_badges(stats),
        "items": [{"label": log, "actionLabel": ""} for log in db.get_activity_log()],
        "message": f"User '{user.name}' updated successfully",
        "message_type": "success",
    }


@ui_event
@returns_update("users_table", "total_users_badge", "users_count_badge", "admin_count_badge", "stat_total_badge", "stat_active_badge", "stat_inactive_badge", "stat_admin_badge", "stat_user_badge", "stat_guest_badge", "activity_log")
async def delete_user(request: Request, payload: DeleteUserPayload):
    """Delete a user."""
    # Get user info before deletion for message
    user = db.get_user(payload.user_id)
    user_name = user.name if user else f"ID {payload.user_id}"

    success = db.delete_user(payload.user_id)

    if not success:
        return {
            "error": "User not found",
            "message": f"User with ID {payload.user_id} not found",
            "message_type": "error",
        }

    # Log activity
    db.log_activity("Deleted", f"User '{user_name}' (ID: {payload.user_id})")

    stats = db.get_stats()

    return {
        "users": [u.model_dump(mode='json') for u in db.get_all_users()],
        "total_count": str(stats["total"]),
        "user_count": str(stats["by_role"]["user"]),
        "admin_count": str(stats["by_role"]["admin"]),
        "guest_count": str(stats["by_role"]["guest"]),
        **get_stats_for_badges(stats),
        "items": [{"label": log, "actionLabel": ""} for log in db.get_activity_log()],
        "message": f"User '{user_name}' deleted successfully",
        "message_type": "success",
    }


@ui_event
@returns_update("users_table", "users_count_badge", "stat_total_badge", "stat_active_badge", "stat_inactive_badge", "stat_admin_badge", "stat_user_badge", "stat_guest_badge")
async def toggle_user_active(request: Request, payload: ToggleUserPayload):
    """Toggle user active status."""
    user = db.get_user(payload.user_id)

    if not user:
        return {
            "error": "User not found",
            "message": f"User with ID {payload.user_id} not found",
            "message_type": "error",
        }

    user.active = not user.active
    stats = db.get_stats()

    return {
        "users": [u.model_dump(mode='json') for u in db.get_all_users()],
        "total_count": str(stats["total"]),
        "user_count": str(stats["by_role"]["user"]),
        "admin_count": str(stats["by_role"]["admin"]),
        "guest_count": str(stats["by_role"]["guest"]),
        **get_stats_for_badges(stats),
        "message": f"User '{user.name}' is now {'active' if user.active else 'inactive'}",
        "message_type": "success",
    }


@ui_event
@returns_update("users_table", "guest_count_badge")
async def filter_users(request: Request, payload: FilterUsersPayload):
    """Filter users by criteria."""
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"filter_users called with role={payload.role}, active={payload.active}, search={payload.search}")

    # Handle special filter values
    if payload.role == "active":
        # "Active Users Only" filter
        role = None
        active = True
    elif payload.role == "all":
        # "All Roles" filter
        role = None
        active = payload.active
    else:
        # Specific role filter
        role = payload.role
        active = payload.active

    logger.info(f"Filtering with role={role}, active={active}, search={payload.search}")

    users = db.get_all_users(
        role=role,
        active=active,
        search=payload.search,
    )

    logger.info(f"Found {len(users)} users after filtering")

    # Build filter description
    filters_applied = []
    if role:
        filters_applied.append(f"role={role}")
    if active is not None:
        filters_applied.append(f"active={active}")
    if payload.search:
        filters_applied.append(f"search='{payload.search}'")

    filter_desc = ", ".join(filters_applied) if filters_applied else "none"

    return {
        "users": [u.model_dump(mode='json') for u in users],
        "total_count": str(len(db.users)),
        "message": f"Showing {len(users)} users (filters: {filter_desc})",
        "message_type": "info",
    }


@ui_event
@returns_update("users_table", "total_users_badge", "users_count_badge", "admin_count_badge", "guest_count_badge", "stat_total_badge", "stat_active_badge", "stat_inactive_badge", "stat_admin_badge", "stat_user_badge", "stat_guest_badge")
async def clear_filters(request: Request, payload: dict | None = None):
    """Clear all filters and show all users."""
    users = db.get_all_users()
    stats = db.get_stats()

    return {
        "users": [u.model_dump(mode='json') for u in users],
        "total_count": str(stats["total"]),
        "user_count": str(stats["by_role"]["user"]),
        "admin_count": str(stats["by_role"]["admin"]),
        "guest_count": str(stats["by_role"]["guest"]),
        **get_stats_for_badges(stats),
        "message": "Filters cleared - showing all users",
        "message_type": "info",
    }


@ui_event
@returns_update("users_table", "total_users_badge", "users_count_badge", "admin_count_badge", "guest_count_badge", "stat_total_badge", "stat_active_badge", "stat_inactive_badge", "stat_admin_badge", "stat_user_badge", "stat_guest_badge", "activity_log")
async def load_initial_data(request: Request, payload: dict | None = None):
    """Load initial data for the dashboard."""
    users = db.get_all_users()
    stats = db.get_stats()

    # Log activity
    db.log_activity("Loaded", f"Dashboard initialized with {len(users)} users")

    return {
        "users": [u.model_dump(mode='json') for u in users],
        "total_count": str(stats["total"]),
        "user_count": str(stats["by_role"]["user"]),
        "admin_count": str(stats["by_role"]["admin"]),
        "guest_count": str(stats["by_role"]["guest"]),
        **get_stats_for_badges(stats),
        "items": [{"label": log, "actionLabel": ""} for log in db.get_activity_log()],
        "message": f"Loaded {len(users)} users",
        "message_type": "success",
    }


@ui_event
@returns_update("activity_log")
async def clear_activity_log(request: Request, payload: dict | None = None):
    """Clear the activity log."""
    db.clear_activity_log()

    return {
        "items": [],
        "message": "Activity log cleared",
        "message_type": "success",
    }


@ui_event
@returns_update("users_table", "total_users_badge", "users_count_badge", "admin_count_badge", "stat_total_badge", "stat_active_badge", "stat_inactive_badge", "stat_admin_badge", "stat_user_badge", "stat_guest_badge", "activity_log")
async def create_admin(request: Request, payload: dict | None = None):
    """Create a new admin user."""
    import random

    name = f"Admin_{random.randint(1000, 9999)}"
    email = f"admin{random.randint(1000, 9999)}@example.com"

    user = db.create_user(name=name, email=email, role="admin")

    # Log activity
    db.log_activity("Created", f"Admin '{user.name}' ({user.email})")

    stats = db.get_stats()

    return {
        "users": [u.model_dump(mode='json') for u in db.get_all_users()],
        "total_count": str(stats["total"]),
        "user_count": str(stats["by_role"]["user"]),
        "admin_count": str(stats["by_role"]["admin"]),
        "guest_count": str(stats["by_role"]["guest"]),
        **get_stats_for_badges(stats),
        "items": [{"label": log, "actionLabel": ""} for log in db.get_activity_log()],
        "message": f"Admin '{user.name}' created successfully",
        "message_type": "success",
    }


@ui_event
@returns_update("users_table", "total_users_badge", "users_count_badge", "admin_count_badge", "stat_total_badge", "stat_active_badge", "stat_inactive_badge", "stat_admin_badge", "stat_user_badge", "stat_guest_badge", "activity_log")
async def create_guest(request: Request, payload: dict | None = None):
    """Create a new guest user."""
    import random

    name = f"Guest_{random.randint(1000, 9999)}"
    email = f"guest{random.randint(1000, 9999)}@example.com"

    user = db.create_user(name=name, email=email, role="guest")

    # Log activity
    db.log_activity("Created", f"Guest '{user.name}' ({user.email})")

    stats = db.get_stats()

    return {
        "users": [u.model_dump(mode='json') for u in db.get_all_users()],
        "total_count": str(stats["total"]),
        "user_count": str(stats["by_role"]["user"]),
        "admin_count": str(stats["by_role"]["admin"]),
        "guest_count": str(stats["by_role"]["guest"]),
        **get_stats_for_badges(stats),
        "items": [{"label": log, "actionLabel": ""} for log in db.get_activity_log()],
        "message": f"Guest '{user.name}' created successfully",
        "message_type": "success",
    }
