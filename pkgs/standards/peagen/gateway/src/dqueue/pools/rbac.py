from ..models import User, Role


def check_role(user: User, allowed: set[Role]):
    if user.role not in allowed:
        raise PermissionError("Not authorized")
