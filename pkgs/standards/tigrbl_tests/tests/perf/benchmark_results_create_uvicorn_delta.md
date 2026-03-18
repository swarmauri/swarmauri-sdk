# Tigrbl vs FastAPI create benchmark deltas

Baseline was captured from the previous benchmark snapshot in this session before the optimization patch.

## Scenario deltas (after - before)

| Scenario | Metric | Before | After | Delta | Delta % |
|---|---:|---:|---:|---:|---:|
| tigrbl | first_start_seconds | 0.502470 | 0.442450 | -0.060021 | -11.95% |
| tigrbl | execution_total_seconds | 2.143817 | 4.137470 | +1.993653 | +93.00% |
| tigrbl | ops_per_second | 11.661444 | 6.042339 | -5.619105 | -48.19% |
| fastapi | first_start_seconds | 0.330020 | 0.266014 | -0.064006 | -19.39% |
| fastapi | execution_total_seconds | 2.728186 | 4.981556 | +2.253370 | +82.60% |
| fastapi | ops_per_second | 9.163597 | 5.018512 | -4.145085 | -45.23% |

## Tigrbl - FastAPI diffs

- Throughput gap (ops_per_second):
  - Before: +2.497847
  - After: +1.023827
  - Delta: -1.474020
- Throughput ratio (tigrbl / fastapi):
  - Before: 1.2726x
  - After: 1.2040x

## Current benchmark gate check

- Required by test: `tigrbl_ops_per_second >= fastapi_ops_per_second * 1.10`
- Current run: `6.042339 >= 5.018512 * 1.10` → pass (1.2040x)
