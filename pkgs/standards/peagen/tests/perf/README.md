# Performance Tests

**Purpose**: benchmark key components such as queues, result backends, and the gateway.

**Description**: these tests run with pytest-benchmark and other tools to measure throughput, latency, and resource usage. They help track performance regressions over time.

**Goals**
- Provide baseline metrics for core components
- Detect slowdowns introduced by code changes

**Non-goals**
- Functional correctness checks
- Comprehensive integration coverage
