"""Enforce README Standards while existing package manifests are migrated."""

import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[2]
baseline_file = root / ".github/readme-standards-baseline.txt"
baseline = set(baseline_file.read_text(encoding="utf-8").splitlines())

result = subprocess.run(
    ["readme-standards", "check", "--root", str(root), "--all", "--format", "json"],
    stdout=subprocess.PIPE,
    encoding="utf-8",
    check=False,
)
if result.returncode not in (0, 1):
    raise SystemExit(result.returncode)

report = json.loads(result.stdout)
deferred = set()
errors = []
for issue in report["diagnostics"]:
    path = Path(issue["path"]).relative_to(root).as_posix()
    rule = issue["rule"]
    message = issue["message"]
    if rule == "config" and message == "missing [tool.readme_standards]" and path in baseline:
        deferred.add(path)
    else:
        errors.append(f"{path}:{issue['line']}: [{rule}] {message}")

for path in sorted(baseline - deferred):
    errors.append(f"{path}: remove this stale entry from {baseline_file.name}")
for error in errors:
    print(error)
print(f"Checked {report['packages']} manifests. Deferred {len(deferred)} existing configurations.")
raise SystemExit(1 if errors else 0)
