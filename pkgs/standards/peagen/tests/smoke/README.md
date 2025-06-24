# Smoke Tests

**Purpose**: provide quick assurance that the main CLI commands and RPC flows are operational.

**Description**: these tests run small tasks against a reachable gateway and exercise commands like `process`, `eval`, and `mutate`. They expect minimal configuration and should finish fast.

**Goals**
- Confirm that the CLI can talk to the gateway
- Verify that common workflows succeed without errors

**Non-goals**
- Deep integration coverage
- Benchmarking or resource measurement
