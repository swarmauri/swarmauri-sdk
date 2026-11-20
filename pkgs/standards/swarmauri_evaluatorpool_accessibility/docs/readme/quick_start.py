from swarmauri_evaluatorpool_accessibility.AccessibilityEvaluatorPool import (
    AccessibilityEvaluatorPool,
)
from swarmauri_standard.programs.Program import Program

program = Program(
    content={"example.txt": "This is a simple sentence. Here is another one."}
)

pool = AccessibilityEvaluatorPool()
pool.initialize()  # spin up the thread pool once before evaluating

results = pool.evaluate([program])
result = results[0]

print(f"Aggregate accessibility score: {result.score:.2f}")
print("Per-evaluator scores:", result.metadata["evaluator_scores"])
flesch_meta = result.metadata["evaluator_metadata"].get(
    "FleschReadingEaseEvaluator", {}
)
print(
    "Flesch interpretation:",
    flesch_meta.get(
        "readability_interpretation", flesch_meta.get("error", "not available")
    ),
)

pool.shutdown()  # release resources when finished
