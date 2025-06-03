#!/usr/bin/env bash
# Quick check that worker containers run as non-root
kubectl exec deploy/peagen-worker-gpu -- id -u
