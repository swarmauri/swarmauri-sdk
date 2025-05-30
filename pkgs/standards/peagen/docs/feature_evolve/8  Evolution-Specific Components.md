## 8 · Evolution-Specific Components

This section documents the **domain logic** that turns Peagen’s generic task
fabric into a full genetic-improvement engine: selectors that choose parents,
mutators that propose children, LLM back-ends, prompt templates, and the
MAP-Elites archive (**EvoDB**).

---

### 8.1 Parent Selector Layer

| Artifact                 | Location                   | Interface                                                                                                           |
| ------------------------ | -------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **`ParentSelector` ABC** | `peagen/selectors/base.py` | `python\nselect(db:EvoDB) -> Program\nsample_inspirations(db,k:int)->list[str]\nfeedback(fitness_gain:float)->None` |

*Entry-point group:* `peagen.parent_selectors`

#### 8.1.1 Adaptive-ε Selector (default)

```python
class AdaptiveEpsilonSelector(ParentSelector):
    def __init__(self, eps_init=0.15, decay=0.96, floor=0.02): ...
    def select(self, db):
        if random.random() < self.eps:          # explore
            return random.choice(list(db.grid.values())).champ
        return min((i.champ for i in db.grid.values()),
                   key=lambda p: p.speed_ms)    # exploit
    def sample_inspirations(self, db, k):
        return random.sample([i.champ.src for i in db.grid.values()], k)
    def feedback(self, fitness_gain):
        self.eps = max(self.floor, self.eps* self.decay) if fitness_gain>0 \
                   else min(0.5, self.eps*1.05)
```

Tunable via:

```toml
[evolve]
selector     = "epsilon"
[selector.epsilon]
eps_init = 0.2
decay    = 0.95
```

---

### 8.2 Mutator Layer

| Interface                                                         | Module                    |
| ----------------------------------------------------------------- | ------------------------- |
| **`Mutator` Protocol** (`mutate()` optional) + TaskHandler mix-in | `peagen/mutators/base.py` |

#### 8.2.1 PatchMutator (built-in)

*PROVIDES* `{"llm","cpu"}`
Algorithm:

1. Build prompt with `PromptSampler.build_mutate_prompt(parent_src, inspirations, entry_sig)`.
2. Call `LLMEnsemble.generate()` → unified diff.
3. Apply diff (`apply_patch()`).
4. On success emit **ExecuteTask** (`requires={"docker","cpu"}`).

`PatchMutator` is registered under entry-point `patch`.

---

### 8.3 LLM Ensemble

```python
child = LLMEnsemble.generate(prompt,
                             backend="auto",
                             temperature=0.7,
                             max_tokens=4096)
```

*Back-end adapters* (entry-point `peagen.llm_backends`)

| Name     | Provider   | Provides                     |
| -------- | ---------- | ---------------------------- |
| `openai` | OpenAI API | `gpt-4o`, `gpt-3.5-turbo`    |
| `groq`   | GroqCloud  | `mixtral-8x22b`, `llama-70b` |
| `local`  | llama.cpp  | GGUF on local GPU/CPU        |

Routing probability configured in TOML:

```toml
[llm.backend_weights]
openai = 3
groq   = 1
```

*Metrics:* `llm_tokens_total{backend}`, `llm_latency_seconds`.

---

### 8.4 Prompt Templates

| File                        | Used by         | Placeholders                                                       |
| --------------------------- | --------------- | ------------------------------------------------------------------ |
| `templates/agent_mutate.j2` | `peagen mutate` | `{{parent_src}}`, `{{entry_sig}}`                                  |
| `templates/agent_evolve.j2` | `PatchMutator`  | `{{parent_src}}`, `{{inspirations}}`, `{{entry_sig}}`, `{{rules}}` |

Guidelines inside template:

* “Return **unified diff** only.”
* “Keep stdlib, maintain signature.”
* Inspiration blocks inserted like:

````markdown
# inspiration 1
```python
<champion src>
````

````

---

### 8.5 EvoDB  (MAP-Elites Archive)

```python
Bucket = tuple[int,int,int,int]  # speed,mem,size,age
class Program:
    src:str; gen:int; speed_ms:float; peak_kb:float; bucket:Bucket
class Island:
    champ:Program; hist:list[Program]
class EvoDB:
    grid:dict[Bucket,Island]
    def insert(self,p:Program): ...
    def sample(self)->Island: ...   # used by Selector
    def save_checkpoint(pth): ...   # msgpack
````

*Bin granularity* (configurable):

```toml
[evolve.archive]
speed_bin_ms = 5
mem_bin_kb   = 32
size_bin_ch  = 40
```

*Program.bucket* formula:

```python
(speed_ms//speed_bin,
 peak_kb //mem_bin,
 len(src)//size_bin,
 gen % 6)                       # age dimension keeps search moving
```

*Checkpoint file* `evo_checkpoint.msgpack` lets runs resume or merge archives.

---

### 8.6 Generation Feedback Loop

```
selector.select  → parent
PromptSampler → LLMEnsemble → PatchMutator → ExecuteHandler → EvaluateHandler
 ^                                          |
 |----------- selector.feedback  <-----------|
           (fitness_gain)
```

Selector adapts ε each generation; EvoDB diversity keeps multiple buckets improving.

---

**Deliverable Summary**

| Component                           | File              | Done in 0.2.0 |
| ----------------------------------- | ----------------- | ------------ |
| `ParentSelector` ABC + epsilon impl | `selectors/`      | ✅            |
| `Mutator` ABC + `PatchMutator`      | `mutators/`       | ✅            |
| LLM Ensemble with 2 back-ends       | `llm/ensemble.py` | ✅            |
| Prompt templates                    | `templates/`      | ✅            |
| EvoDB classes & checkpoint          | `evo_db.py`       | ✅            |

These evolution-specific modules sit cleanly on top of the task fabric,
providing the research flexibility and reproducible diversity search that the
product goals require.
