# Python Crouton Server

This template produces a lightweight API service that exposes CRUD routes for your models. The generator consumes a `projects_payload.yaml` file and renders a Docker‑ready project.

## Project Structure

```
{{ PROJ.ROOT }}/
    docker-compose.yaml
    {{ PKG.NAME }}/
        Dockerfile
        pyproject.toml
        {{ MOD.NAME }}/
            __init__.py
            api/
                __init__.py
                v1/
                    main.py
                    utils.py
```

`projects_payload.yaml` must define at least a project name, project root, packages and modules. Peagen fills the template using those values to create the files above.

## Example `projects_payload.yaml`

```yaml
PROJECTS:
  - NAME: "ExampleService"
    ROOT: "example_service"
    TEMPLATE_SET: "python_crouton_server"
    PACKAGES:
      - NAME: "example_pkg"
        MODULES:
          - NAME: "items"
```

Generate the project:

```bash
peagen process projects_payload.yaml
```

A generated entry point might resemble:

```python
"""Entry point for the API service."""

from fastapi import FastAPI
from .api.v1.main import router as v1_router

app = FastAPI()
app.include_router(v1_router)
```
