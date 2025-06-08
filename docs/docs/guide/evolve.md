# Using Peagen Evolution Components

The evolution workflow relies on several plug-in layers:

- **Parent selectors** choose a champion from `EvoDB`.
- **Mutators** build prompts and apply patches via the LLM ensemble.
- **LLM back‑ends** are weighted in `.peagen.toml` under `[llm.backend_weights]`.

Example configuration:

```toml
[evolve]
selector = "epsilon"

[llm.backend_weights]
openai = 3
local  = 1
```

Run `peagen evolve step` to generate a new candidate. After evaluation the
fitness gain is reported back to the selector to adapt exploration rate.
