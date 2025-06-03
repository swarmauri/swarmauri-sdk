#!/usr/bin/env python3
"""Example autoscaler for Docker Compose deployments."""
import os
import subprocess
import time
import requests

PROM_URL = os.getenv("PROM_URL", "http://localhost:9090/api/v1/query?query=queue_pending_total")
MAX_REPLICAS = int(os.getenv("MAX_REPLICAS", "32"))
MIN_REPLICAS = int(os.getenv("MIN_REPLICAS", "1"))
SCALE_SERVICE = os.getenv("SCALE_SERVICE", "worker")

idle_since = None

while True:
    try:
        resp = requests.get(PROM_URL, timeout=5)
        data = resp.json()["data"]["result"][0]["value"][1]
        pending = int(float(data))
    except Exception:
        pending = 0

    desired = max(MIN_REPLICAS, min(MAX_REPLICAS, pending // 2 or 1))
    subprocess.run(["docker", "compose", "up", "--scale", f"{SCALE_SERVICE}={desired}", "-d"], check=False)

    if pending == 0:
        if idle_since is None:
            idle_since = time.time()
        elif time.time() - idle_since > 300:
            subprocess.run(["docker", "compose", "up", "--scale", f"{SCALE_SERVICE}=0", "-d"], check=False)
    else:
        idle_since = None

    time.sleep(30)
