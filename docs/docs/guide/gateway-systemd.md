# Running the Peagen Gateway via systemd

```ini
[Unit]
Description=Peagen Gateway service
After=network.target

[Service]
Type=simple
WorkingDirectory=/srv/peagen
Environment=REDIS_URL=redis://localhost:6379/0
Environment=PG_DSN=postgresql+asyncpg://user:pass@localhost:5432/peagen
ExecStart=/usr/bin/uvicorn peagen.gateway:app --host 0.0.0.0 --port 8000
ExecReload=/bin/kill -s SIGTERM $MAINPID
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target
```
