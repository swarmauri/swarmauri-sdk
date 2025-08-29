```
                                   ┌────────────────────────────────────────────────────┐
                                   │                Client Front-Ends                  │
                                   │────────────────────────────────────────────────────│
                                   │  • CLI (single-node)                              │
                                   │  • TUI (WebSocket stream)                         │
                                   │  • Web-GUI (WS + Pub/Sub fan-out)                 │
                                   └──────────────┬─────────────────────────────▲──────┘
                                                  │ HTTP/JSON-RPC (CRUD)        │ WS
                                                  │                             │
┌──────────────────────────────────────────────────┴───────────────┐    Redis -- WS Bridge
│                       Pool-Manager Gateway(s)                   │<─────────────┘
│──────────────────────────────────────────────────────────────────│
│  /rpc  (HTTP/2 JSON-RPC)                                         │
│  • Task.submit / cancel / get                                    │
│  • Worker.register / heartbeat                                   │
│  • SCHEDULER                                                     │
│       BLPOP    ─┐   dispatch ← HTTP/2 JSON-RPC → /rpc            │
└─────────────────┼──────────────┬─────────────────────────────────┘
                  │              │
                  │              │
                  ▼              ▼
        Redis Task Queues      PostgreSQL Results DB
        ─────────────────      ─────────────────────
        queue:<pool>  (LIST)   task_runs (audit)  ◄── persist status
        task:update   (PubSub)                     (oids, metrics…)

                        ▲
                        │
       CloudEvents JSON │
                        │
                        ▼
                MinIO Artifact Store
                ───────────────────
                s3://artifacts/<task-id>/…

                                   ▲
                                   │  upload / download (S3 API)
                                   │
┌──────────────────────────────────┴────────────────────────────────┐
│                          Worker Nodes                            │
│───────────────────────────────────────────────────────────────────│
│  FastAPI + JSON-RPC  (/rpc)                                      │
│  • Work.start  → execute payload                                 │
│  • Work.finished → status + oids                                 │
│  • BLPOP or ZPOP work pull (optional future)                     │
│  • Heartbeats every 5 s  ────────────────────────────────────────┐│
└───────────────────────────────────────────────────────────────────┘│
                                                                    │
                               HTTP/2 JSON-RPC                      │
                                                                    │
┌────────────────────────────────────────────────────────────────────┘
│                      Local Workstation Mode
│  (User runs a single worker + CLI, all above replaced by localhost)
└────────────────────────────────────────────────────────────────────┘
```
