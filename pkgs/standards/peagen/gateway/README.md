# DQueue – Distributed Task Queue

* **HTTP API** – push commands / query status  
* **WebSocket** – live streams from pools & workers  
* **Redis Pub/Sub** – event bus for heart-beats, logs, triggers  

Run a local dev network:

```bash
uvicorn scripts.dev_server:app --reload
Redis must be reachable at redis://localhost:6379/0 (configurable via env or .env).
```

### `src/dqueue/__init__.py`
```python
from .config import settings          # noqa: F401
from .models import Pool, Task, Status  # noqa: F401
```