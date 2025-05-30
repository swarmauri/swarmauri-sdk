#!/usr/bin/env python3
"""Benchmark harness for Peagen workloads."""
from __future__ import annotations

import argparse
import csv
import os
import pathlib
import subprocess
import sys
import tempfile
from typing import Dict

from prometheus_client.parser import text_string_to_metric_families

from peagen.cli_common import load_peagen_toml

WORKLOADS = {
    "bad_sort": "benchmarks/artifacts/bad_sort.py",
    "bench_hatchery": "benchmarks/artifacts/bench_hatchery.py",
    "bench_queue_rate": "benchmarks/artifacts/bench_queue_rate.py",
}


def _fetch_metrics(file_path: pathlib.Path) -> Dict[str, float]:
    """Return Prometheus metrics from a ``.prom`` file."""
    metrics: Dict[str, float] = {}
    if not file_path.is_file():
        return metrics
    text = file_path.read_text(encoding="utf-8")
    for fam in text_string_to_metric_families(text):
        for sample in fam.samples:
            metrics[sample.name] = sample.value
    return metrics


def _run_workload(name: str, prom_port: int) -> Dict[str, float]:
    """Execute a workload and gather its metrics."""
    script = WORKLOADS[name]
    metrics_path = pathlib.Path(tempfile.mkstemp(suffix=".prom")[1])
    env = os.environ.copy()
    env["PROM_PORT"] = str(prom_port)
    env["METRICS_FILE"] = str(metrics_path)
    subprocess.run([sys.executable, script], check=True, env=env)
    return _fetch_metrics(metrics_path)


def _compare(baseline: pathlib.Path, current: Dict[str, float]) -> Dict[str, tuple[float, float, float]]:
    """Compare current metrics against baseline CSV."""
    data: Dict[str, tuple[float, float, float]] = {}
    with open(baseline, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            metric = row["metric"]
            base = float(row["value"])
            val = current.get(metric)
            if val is None:
                continue
            ratio = val / base if base else 0.0
            data[metric] = (val, base, ratio)
    return data


def main() -> None:
    """Run all workloads and check for regressions."""
    parser = argparse.ArgumentParser(description="Run benchmark workloads")
    parser.add_argument(
        "--baseline",
        type=pathlib.Path,
        default=pathlib.Path("benchmarks/baseline.csv"),
    )
    parser.add_argument("--prom-port", type=int, default=8000)
    args = parser.parse_args()

    # load config so bench_runner mirrors CLI behaviour
    load_peagen_toml()

    metrics: Dict[str, float] = {}
    for name in WORKLOADS:
        metrics.update(_run_workload(name, args.prom_port))

    comparisons = _compare(args.baseline, metrics)

    results_path = pathlib.Path("benchmarks/results.csv")
    with open(results_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["metric", "value", "baseline", "ratio"])
        for metric, (val, base, ratio) in comparisons.items():
            writer.writerow([metric, f"{val:.6f}", f"{base:.6f}", f"{ratio:.6f}"])

    regress = [m for m, (_, _, r) in comparisons.items() if r > 1.05]
    if regress:
        metrics_str = ", ".join(regress)
        print(f"Regression detected in: {metrics_str}")
        sys.exit(1)


if __name__ == "__main__":
    main()
