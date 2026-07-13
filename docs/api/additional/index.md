# Additional Classes

Composition, evaluation, and factory patterns beyond core LLM components (agents, conversations, embeddings).

## Categories

### [Factories](factories/index.md)

Factory patterns for constructing and configuring SDK components.

### [Ensembles](ensembles/index.md)

Ensemble composition patterns for combining multiple components.

### [Evaluators](evaluators/index.md)

Evaluation and scoring components for measuring output quality.

## Shared Patterns

- **ComponentBase inheritance** — all classes extend `ComponentBase` for uniform lifecycle and interface contracts
- **Resource typing** — typed resource identifiers enable registration, serialization, and discovery
