# Tigrbl Examples Maintainers Guide

This guide defines how maintainers should shape pedagogical examples in
`tigrbl_tests/examples`.

## Purpose

- Keep examples instructional and implementation-focused.
- Preserve clear lessons for implementers learning Tigrbl patterns.
- Keep setup explicit so readers can trace behavior from model to API call.

## Required demonstration layers

Relationship walkthroughs should explicitly include:

1. **Storage layer**
   - Use storage declarations (`S(...)`) with explicit constraints.
   - Show foreign keys and cardinality constraints for relationship shape.
2. **Field layer**
   - Use `F(py_type=...)` to document Python-facing types.
3. **IO layer**
   - Use `IO(in_verbs=..., out_verbs=...)` to explain API contract.
4. **Client experience layer**
   - Start a uvicorn server in the lesson.
   - Demonstrate both **REST** and **JSON-RPC** interactions.

## Relationship coverage expectations

Include and maintain explicit examples for:

- one-to-one,
- one-to-many,
- many-to-many.

Use concrete tables and relationship names so ownership is obvious.

## Writing guidance for lesson files

- Module docstrings should state what the lesson teaches.
- Class docstrings should describe each model's role.
- Callable docstrings should summarize the demonstrated workflow.
- Inline comments should explain important steps and checks.
- Use plain, direct language and small, readable progression.
- Keep teaching tone for implementers; avoid maintainers-only narration in
  lesson source files.

## Abstraction policy

- Avoid extra helper abstractions in pedagogical relationship lessons.
- Keep runtime setup and request flow visible in each test module.
- Use explicit assertions that show expected outcomes.
