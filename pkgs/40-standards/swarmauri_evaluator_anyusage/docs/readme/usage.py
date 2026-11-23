from pathlib import Path

from swarmauri_base.programs.ProgramBase import ProgramBase
from swarmauri_evaluator_anyusage import AnyTypeUsageEvaluator


workspace = Path("path/to/project")

program = ProgramBase()
program.name = workspace.name
program.path = str(
    workspace
)  # AnyTypeUsageEvaluator walks this directory on disk

evaluator = AnyTypeUsageEvaluator(penalty_per_occurrence=0.1, max_penalty=1.0)
score, metadata = evaluator.evaluate(program)

print(f"Score: {score:.2f}")
print("Files analyzed:", metadata["files_analyzed"])
print("Any usages:", metadata["total_any_occurrences"])

for report in metadata["detailed_occurrences"]:
    print("-", report["file"])
    for occurrence in report["occurrences"]:
        print(f"  line {occurrence['line']}: {occurrence['context']}")

# If you already depend on `swarmauri_standard`, import
# `from swarmauri_standard.programs.Program import Program` and replace the
# ProgramBase construction above with `Program.from_workspace(workspace)`
# before setting `program.path` to keep the on-disk directory in sync with
# your Program content.
