# Docs

## Deploy via Docker Compose

### Build

```bash
docker compose -f docker-compose.docs.yml build
docker compose -f docker-compose.docs.yml up -d
```

### NPM proxy

1. Add proxy host in Nginx Proxy Manager.
2. Domain → docs service hostname/port from compose (e.g. `docs:80`).
3. Scheme: `http` to the container; NPM terminates TLS.

### SSL

1. In NPM, open the docs proxy host → SSL.
2. Request Let's Encrypt cert (or upload custom).
3. Enable Force SSL and HTTP/2.
