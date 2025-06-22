# Evaluation Results Schema

Evaluators emit metrics as JSON Lines. Each line contains a single metric for a task.

```sql
CREATE TABLE evaluation_results (
    task_id UUID REFERENCES task_runs(id),
    evaluator_name TEXT NOT NULL,
    metric TEXT NOT NULL,
    unit TEXT NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (task_id, evaluator_name, metric)
);
```

Example JSON Line:

```json
{"task_id": "3d1...", "evaluator_name": "BleuEvaluator", "metric": "bleu", "unit": "score", "value": 0.87, "created_at": "2024-01-01T00:00:00Z"}
```

CLI stub:

```python
@eval_app.command("export")
def export_results(format: str = typer.Option("json", "--format", "-f")):
    """Stream evaluation results as JSON Lines or CSV."""
    pass
```
