# Infrastructure Tests

**Purpose**: verify that a basic gateway and worker setup can run tasks end-to-end.

**Description**: these tests spin up a local gateway and use the sample `simple_evolve_demo` specification to ensure remote execution works.

**Goals**
- Validate remote task submission against a running gateway
- Ensure the evolve workflow completes successfully

**Non-goals**
- Exhaustive functional coverage of all features
- Performance measurement or stress testing
