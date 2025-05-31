# Using Peagen Evolution Components

The evolution workflow relies on several plug-in layers:

- **Parent selectors** choose a champion from `EvoDB`.
- **Mutators** build prompts and apply patches via the LLM ensemble.

Example configuration:

```toml
[evolve]
selector = "epsilon"
```

Run `peagen evolve step` to generate a new candidate. After evaluation the
fitness gain is reported back to the selector to adapt exploration rate.
