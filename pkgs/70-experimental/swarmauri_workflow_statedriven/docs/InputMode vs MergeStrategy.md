# InputMode vs MergeStrategy

## When it runs
Input Mode is applied before any transition or join—right when you dequeue a (state_name, data) pair.

Merge Strategy is applied after you’ve waited on multiple incoming transitions (i.e. after your JoinStrategy fires) and you’ve collected all branch outputs into a buffer.

## What they do


| Aspect           | Input Mode                                                     | Merge Strategy                                                                                |
| ---------------- | -------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **File / Class** | `workflows/node.py` → **class** `Node` → **attr** `input_mode` | `workflows/merge_strategies/base.py` → **class** `MergeStrategy` → **method** `merge(inputs)` |
| **Engine use**   | `workflows/base.py` → **method** `run`<br>\`\`\`python         |                                                                                               |



## Details

1. **Merge Strategy** (“How do I turn N branch outputs into one payload?”)

   * **When:** After you’ve waited on multiple incoming transitions.
   * **Where:** On the **target** state’s `merge_strategy` (in **`workflows/merge_strategies/*.py`**, class `MergeStrategy` → method `merge`).
   * **Output:** A single **`merged_input`** value (could be a scalar, a flat `List[...]`, a dict, etc.).

2. **Input Mode** (“Given the merged\_input or raw data, what shape does my node actually see?”)

   * **When:** Just before you call the node’s `execute()` or `batch()` (in **`workflows/base.py`**, method `run`).
   * **Where:** On the state’s `input_mode` attribute (in **`workflows/node.py`**, class `Node` → attribute `input_mode`).
   * **Output:** The final **`input_data`** that you pass into `Node.execute(input_data)` or `Node.batch(input_data)`.

---

## Example Workflow

```text
States: A, B → C
Transitions: A→C, B→C (always true)
```

* **A.exec()** returns `"foo"`
* **B.exec()** returns `"bar"`

### Merge Strategies on C

| MergeStrategy            | merge(\[“foo”,”bar”]) | merged\_input     |
| ------------------------ | --------------------- | ----------------- |
| **ListMergeStrategy**    | → `["foo","bar"]`     | list of scalars   |
| **FlattenMergeStrategy** | → `["foo","bar"]`     | same as ListMerge |
| **ConcatMergeStrategy**  | → `"foobar"`          | scalar (str)      |
| **DictMergeStrategy**    | → `{}`                | scalar (dict)     |

### Input Modes on C

| `input_mode`    | What the node sees for `input_data`    |
| --------------- | -------------------------------------- |
| **`previous`**  | Pass **only** the merged\_input above. |
| **`aggregate`** | Pass the **entire** `results` dict:    |

```python
{
  "A": "foo",
  "B": "bar",
  "C": merged_input
}
```

\| **`split`**       | If `merged_input` is a **list**, create one queue item per element before execution. E.g.

```text
merged_input = ["foo","bar"]  
→ queue ("C","foo") and ("C","bar")
```

---

### Putting it all together

#### 1. ListMerge + previous

* **merge** → `["foo","bar"]`
* **input\_data** → `["foo","bar"]`
* **dispatch** → `Node.batch(["foo","bar"])`

#### 2. ListMerge + aggregate

* **merge** → `["foo","bar"]`
* **input\_data** → `{"A":"foo","B":"bar"}`
* **dispatch** → `Node.execute({...})` or `batch` if you treat lists specially inside your node

#### 3. ConcatMerge + previous

* **merge** → `"foobar"`
* **input\_data** → `"foobar"`
* **dispatch** → `Node.execute("foobar")`

#### 4. ConcatMerge + split

* **merge** → `"foobar"` (scalar)
* **split** sees a non‑list → no split, just
* **dispatch** → `Node.execute("foobar")`

#### 5. FlattenMerge + split

* **merge** → `["foo","bar"]`
* **split** → split into two items
* **dispatch** →

  ```python
  Node.execute("foo")
  Node.execute("bar")
  ```

---

### Key Takeaways

* **Merge Strategy** only cares about ***combining*** multiple branch outputs into one payload.
* **Input Mode** only cares about ***shaping*** that payload (or raw data) into the exact form(s) your node’s `execute()`/`batch()` method expects.
* You can mix‑and‑match freely. E.g. flatten two lists into one, then split that flat list into individual calls, or aggregate everything into a context dict and run once.
