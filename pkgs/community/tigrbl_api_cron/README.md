![Tigrbl Logo](https://github.com/swarmauri/swarmauri-sdk/blob/a170683ecda8ca1c4f912c966d4499649ffb8224/assets/tigrbl.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/tigrbl_api_cron/">
        <img src="https://img.shields.io/pypi/dm/tigrbl_api_cron" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/tigrbl_api_cron/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/tigrbl_api_cron.svg"/></a>
    <a href="https://pypi.org/project/tigrbl_api_cron/">
        <img src="https://img.shields.io/pypi/pyversions/tigrbl_api_cron" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/tigrbl_api_cron/">
        <img src="https://img.shields.io/pypi/l/tigrbl_api_cron" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/tigrbl_api_cron/">
        <img src="https://img.shields.io/pypi/v/tigrbl_api_cron?label=tigrbl_api_cron&color=green" alt="PyPI - tigrbl_api_cron"/></a>
</p>

---

# Tigrbl API Cron ⏰

> A lightweight Tigrbl application that stores cron schedules, exposes CRUD APIs, and runs registered jobs while capturing their execution results.

## ✨ Features

- 🗄️ Persists cron jobs as first-class `CronJob` rows with default CRUD verbs.
- 🪪 Tracks validity windows, timestamps, and last execution metadata for each schedule.
- 📜 Records every execution in the `CronJobResult` table for full observability.
- ⚙️ Provides a simple registry and executor to run due jobs and persist their outputs or failures.
- 🚀 Ships with a `FastAPI` application constructor for rapid deployment.

## 📦 Installation

### Using `uv`

```bash
uv add tigrbl_api_cron
```

### Using `pip`

```bash
pip install tigrbl_api_cron
```

## 🚀 Quick Start

```python
import asyncio
from datetime import datetime, timezone

from tigrbl_api_cron import (
    CronJob,
    build_app,
    execute_due_jobs,
    register_cron_job,
)

# 1. Build and initialize the API (SQLite in-memory by default)
app = build_app()
asyncio.run(app.initialize())

# 2. Register a callable that will be invoked when its cron job is due
@register_cron_job("demo.pkg")
async def demo_job(*, job: CronJob, session, scheduled_for, now):
    return {"ran_at": now.isoformat()}

# 3. Create a cron job entry (via ORM, REST, or RPC)
async def seed_job():
    async with app.engine.asession() as session:
        job = CronJob(pkg_uid="demo.pkg", cron_expression="*/5 * * * *")
        session.add(job)
        await session.commit()

asyncio.run(seed_job())

# 4. Run due jobs and capture their results
asyncio.run(execute_due_jobs(app, now=datetime.now(timezone.utc)))
```

## 🧪 Executing Jobs

- Register handlers with `register_cron_job(pkg_uid)`.
- Call `execute_due_jobs(app, now=...)` from a scheduler or worker process.
- Results are written to the `CronJobResult` table and surfaced via the REST API.

## 📄 License

This project is licensed under the terms of the [Apache 2.0](LICENSE) license.
