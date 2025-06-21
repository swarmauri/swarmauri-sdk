# Using `PostgresSelector`

The `PostgresSelector` picks the top *k* parents directly from a PostgreSQL table.
This keeps the gateway lightweight when the results table grows large.

```yaml
operators:
  selection:
    kind: postgres
    params:
      dsn: "postgresql://peagen:peagen@pg-svc:5432/peagen"
      table: "task_results"
      fitness_col: "fitness"
      sha_col: "commit_sha"
      extra_where: "task_name = 'mutate'"
      k: 10
```

**Security note:** `extra_where` is inserted verbatim into the SQL query.
Only use trusted values to avoid SQL injection.
