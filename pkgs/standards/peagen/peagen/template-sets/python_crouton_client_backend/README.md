# Python Crouton Client Backend

This template scaffolds a backend service that pairs with a Crouton client. It follows the router/service/repository pattern and uses SQLAlchemy models with Pydantic schemas generated from your `projects_payload.yaml` file.

## Expected Layout

```
{{ PROJ.ROOT }}/
    {{ PKG.NAME }}/
        Dockerfile
        pyproject.toml
        {{ MOD.NAME }}.py
```

Running `peagen process projects_payload.yaml` creates the package above using the modules defined in the YAML configuration.

## Usage Example

Create a minimal `projects_payload.yaml`:

```yaml
PROJECTS:
  - NAME: "MyBackend"
    ROOT: "pkgs"
    TEMPLATE_SET: "python_crouton_client_backend"
    PACKAGES:
      - NAME: "my_backend"
        MODULES:
          - NAME: "user"
```

Then run:

```bash
peagen process projects_payload.yaml
```

A generated service might look like this:

```python
class UserService:
    """Manage user records."""

    def __init__(self, session):
        """Initialize with an active database session."""
        self.session = session

    def get_user(self, user_id: int):
        """Return a user by ID."""
        ...
```
