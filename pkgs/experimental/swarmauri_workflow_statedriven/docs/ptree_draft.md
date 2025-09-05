swarmauri/
├── __init__.py                             # exports core API
├── workflows/
│   ├── __init__.py
│   ├── base.py                             # class WorkflowBase → methods: __init__, add_state, add_transition, run
│   ├── graph.py                            # class WorkflowGraph → methods: __init__, execute, visualize
│   ├── node.py                             # class Node → methods: __init__, execute, validate
│   ├── transition.py                       # class Transition → methods: __init__, is_triggered
│   ├── state_manager.py                    # class StateManager → methods: __init__, update_state, get_state, log
│   ├── validator.py                        # functions: always_valid, validate_requirements, validate_design
│   ├── exceptions.py                       # classes: InvalidTransitionError, ValidationError, WorkflowError
│   ├── join_strategies/
│   │   ├── __init__.py
│   │   ├── base.py                         # class JoinStrategy → methods: mark_complete, is_satisfied, reset
│   │   ├── all_join.py                     # class AllJoinStrategy → methods: mark_complete, is_satisfied
│   │   ├── first_join.py                   # class FirstJoinStrategy → methods: mark_complete, is_satisfied
│   │   ├── n_of_m_join.py                  # class NofMJoinStrategy → methods: __init__, mark_complete, is_satisfied
│   │   ├── conditional_join.py             # class ConditionalJoinStrategy → methods: __init__, mark_complete, is_satisfied
│   │   └── aggregator.py                   # class AggregatorStrategy → methods: __init__, mark_complete, is_satisfied, aggregate
│   │   └── per_arrival_join.py             # class PerArrivalJoinStrategy
│   ├── merge_strategies/
│   │   ├── __init__.py
│   │   ├── base.py                         # class MergeStrategy → method: merge
│   │   ├── concat_merge.py                 # class ConcatMergeStrategy → method: merge
│   │   ├── dict_merge.py                   # class DictMergeStrategy → method: merge
│   │   └── custom_merge.py                 # class CustomMergeStrategy → methods: __init__, merge
│   ├── input_modes/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── first.py
│   │   ├── last.py
│   │   ├── aggregate.py
│   │   └── split.py
│   └── conditions/
│       ├── __init__.py
│       ├── base.py                         # class Condition → method: evaluate
│       ├── function_condition.py           # class FunctionCondition → methods: __init__, evaluate
│       ├── composite_condition.py          # classes: AndCondition, OrCondition, NotCondition → method: evaluate
│       ├── time_condition.py               # class TimeWindowCondition → method: evaluate
│       ├── regex_condition.py              # class RegexCondition → method: evaluate
│       └── state_condition.py              # class StateValueCondition → method: evaluate

tests/
├── __init__.py
├── conftest.py
├── workflows/
│   ├── __init__.py
│   ├── test_base.py               # tests WorkflowBase → methods: __init__, add_state, add_transition, run, run_parallel
│   ├── test_graph.py              # tests WorkflowGraph → methods: execute, visualize
│   ├── test_node.py               # tests Node → methods: __init__, prepare_input, execute, batch, run, validate
│   ├── test_transition.py         # tests Transition → methods: __init__, is_triggered
│   ├── test_state_manager.py      # tests StateManager → methods: __init__, update_state, get_state, buffer_input, get_buffer, pop_buffer, log
│   ├── test_validator.py          # tests functions in validator.py: always_valid, validate_requirements, validate_design
│   ├── test_exceptions.py         # tests exceptions.py → classes: WorkflowError, InvalidTransitionError, ValidationError
│   ├── join_strategies/
│   │   ├── __init__.py
│   │   ├── test_all_join.py           # tests AllJoinStrategy → methods: __init__, is_satisfied, reset
│   │   ├── test_first_join.py         # tests FirstJoinStrategy → methods: __init__, mark_complete, is_satisfied, reset
│   │   ├── test_n_of_m_join.py        # tests NofMJoinStrategy → methods: __init__, is_satisfied, reset
│   │   ├── test_conditional_join.py   # tests ConditionalJoinStrategy → methods: __init__, is_satisfied, reset
│   │   └── test_aggregator.py         # tests AggregatorStrategy → methods: __init__, is_satisfied, aggregate, reset
│   ├── merge_strategies/
│   │   ├── __init__.py
│   │   ├── test_concat_merge.py       # tests ConcatMergeStrategy → method: merge
│   │   ├── test_dict_merge.py         # tests DictMergeStrategy → method: merge
│   │   ├── test_list_merge.py         # tests ListMergeStrategy → method: merge
│   │   ├── test_flatten_merge.py      # tests FlattenMergeStrategy → method: merge
│   │   └── test_custom_merge.py       # tests CustomMergeStrategy → methods: __init__, merge
│   ├── conditions/
│   │   ├── __init__.py
│   │   ├── test_base_condition.py     # tests Condition → method: evaluate
│   │   ├── test_function_condition.py # tests FunctionCondition → methods: __init__, evaluate
│   │   ├── test_composite_condition.py# tests AndCondition, OrCondition, NotCondition → evaluate
│   │   ├── test_time_condition.py     # tests TimeWindowCondition → methods: __init__, evaluate
│   │   ├── test_regex_condition.py    # tests RegexCondition → methods: __init__, evaluate
│   │   ├── test_state_condition.py    # tests StateValueCondition → methods: __init__, evaluate
│   └── input_modes/
│       ├── __init__.py
│       ├── test_first_input_mode.py   # tests FirstInputMode → method: prepare
│       ├── test_last_input_mode.py    # tests LastInputMode → method: prepare
│       ├── test_aggregate_input_mode.py# tests AggregateInputMode → method: prepare
│       └── test_split_input_mode.py   # tests SplitInputMode → method: prepare