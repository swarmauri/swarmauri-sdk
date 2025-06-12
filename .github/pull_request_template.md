## Summary
- provide a short summary of the changes

## Checklist
- [ ] `ruff check`
- [ ] `pytest`
- [ ] Deploy gateway and worker for **remote** with Redis queue, Redis pubsub, MinIO storage and Postgres backend
- [ ] Deploy gateway and worker for **local** with in-memory queue, no pubsub, local FS storage and results backend
- [ ] Submit a task in each mode using `peagen -q` and wait for completion
- [ ] Show `task get` output for each mode proving success

