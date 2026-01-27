"""In-memory database simulation for CRUD operations."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from .models import User, UserRole


class Database:
    """Simple in-memory database for demonstration purposes."""

    def __init__(self) -> None:
        """Initialize database with seed data."""
        self.users: list[User] = []
        self.activity_log: list[dict] = []
        self._next_id = 1
        self._seed_data()

    def _seed_data(self) -> None:
        """Create initial test data."""
        # Start with empty users list
        self.users = []
        self._next_id = 1

    def create_user(self, name: str, email: str, role: UserRole) -> User:
        """Create a new user.

        Args:
            name: User's full name
            email: User's email address
            role: User's role

        Returns:
            The created User object
        """
        user = User(id=self._next_id, name=name, email=email, role=role)
        self.users.append(user)
        self._next_id += 1
        return user

    def get_user(self, user_id: int) -> Optional[User]:
        """Get a user by ID.

        Args:
            user_id: The user's ID

        Returns:
            User object if found, None otherwise
        """
        return next((u for u in self.users if u.id == user_id), None)

    def update_user(self, user_id: int, **updates) -> Optional[User]:
        """Update a user's attributes.

        Args:
            user_id: The user's ID
            **updates: Attributes to update

        Returns:
            Updated User object if found, None otherwise
        """
        user = self.get_user(user_id)
        if user:
            for key, value in updates.items():
                if value is not None and hasattr(user, key):
                    setattr(user, key, value)
        return user

    def delete_user(self, user_id: int) -> bool:
        """Delete a user.

        Args:
            user_id: The user's ID

        Returns:
            True if user was deleted, False if not found
        """
        user = self.get_user(user_id)
        if user:
            self.users.remove(user)
            return True
        return False

    def get_all_users(
        self,
        role: Optional[UserRole] = None,
        active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> list[User]:
        """Get all users with optional filters.

        Args:
            role: Filter by user role
            active: Filter by active status
            search: Search in name or email

        Returns:
            List of User objects matching the filters
        """
        users = self.users

        if role:
            users = [u for u in users if u.role == role]

        if active is not None:
            users = [u for u in users if u.active == active]

        if search:
            search_lower = search.lower()
            users = [
                u
                for u in users
                if search_lower in u.name.lower() or search_lower in u.email.lower()
            ]

        return users

    def get_stats(self) -> dict:
        """Get user statistics.

        Returns:
            Dictionary with user statistics
        """
        return {
            "total": len(self.users),
            "active": len([u for u in self.users if u.active]),
            "inactive": len([u for u in self.users if not u.active]),
            "by_role": {
                "admin": len([u for u in self.users if u.role == UserRole.ADMIN]),
                "user": len([u for u in self.users if u.role == UserRole.USER]),
                "guest": len([u for u in self.users if u.role == UserRole.GUEST]),
            },
        }

    def log_activity(self, action: str, details: str) -> None:
        """Log an activity to the activity log.

        Args:
            action: The action performed (e.g., "Created", "Updated", "Deleted")
            details: Additional details about the action
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        # Format as a readable string for display
        formatted_entry = f"[{timestamp}] {action}: {details}"
        self.activity_log.insert(0, formatted_entry)
        # Keep only last 10 activities
        self.activity_log = self.activity_log[:10]

    def get_activity_log(self) -> list[str]:
        """Get the recent activity log.

        Returns:
            List of recent activities (up to 10) as formatted strings
        """
        return self.activity_log

    def clear_activity_log(self) -> None:
        """Clear the activity log."""
        self.activity_log = []


# Global database instance
db = Database()
