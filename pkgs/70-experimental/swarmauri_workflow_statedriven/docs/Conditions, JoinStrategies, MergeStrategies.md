# Conditions, Join Strategies, Merge Strategies

## Conditions

### What they are: 

Predicates that guard individual transitions, deciding whether a particular edge can fire.

### Where they live:

File: workflows/conditions/base.py → class Condition

Concrete: e.g. FunctionCondition, RegexCondition, TimeWindowCondition, etc.

### Where they belong:

Belong on Transitions — they guard the edge.

### Responsibility:

Evaluate the current accumulated state (outputs of completed nodes) and return True or False.

### Scope: 

Always applied per transition (source → target).

### Example:

Only transition from process → finalize if the process node’s output is valid JSON (RegexCondition or FunctionCondition wrapping an is_json check).


---

## Join Strategies
### What they are: 

Policies that determine when a converging state is ready to execute, in the presence of multiple incoming transitions.

### Where they live:

File: workflows/join_strategies/base.py → class JoinStrategy

Concrete: AllJoinStrategy, FirstJoinStrategy, NofMJoinStrategy, ConditionalJoinStrategy, etc.

### Where they belong:

Belong on States — they live in the state’s definition, telling the engine how to wait for multiple incoming transitions before firing that state.

### Responsibility:

Buffer each branch’s output invocation toward the same target.

Decide if the required set of branches has arrived (e.g. all, first, N‑of‑M, or a custom predicate).

### Example:

With AllJoinStrategy(expected_branches=["A","B"]), the converging node “C” only fires after both A→C and B→C transitions have evaluated True.


---

## Merge Strategies
### What they are: 
Policies that describe how to combine multiple branch outputs into a single input for the converged node.

### Where they live:
File: workflows/merge_strategies/base.py → class MergeStrategy

Concrete: DictMergeStrategy, ConcatMergeStrategy, or custom implementations.

### Where they belong:

Also belong on States — they’re part of the state’s configuration, dictating how to combine buffered inputs once the join condition is met.

### Responsibility:

Receive the list of buffered outputs for a converged state.

Produce one unified value (e.g. merge dicts by key, concatenate strings, batch into a list).

### Example:

DictMergeStrategy shallow‑merges two JSON objects into one.

ConcatMergeStrategy concatenates raw text outputs from parallel branches.

---

# How They Work Together
Transitions are evaluated one-by-one using their Condition.

When multiple transitions target the same state, each firing buffers its output via the Join Strategy, which checks if all required branches have arrived.

Once join_strategy.is_satisfied(...) returns True, the buffered outputs are passed into the Merge Strategy, yielding a single merged_input.

That merged_input becomes the input to the converged node’s agent/tool.