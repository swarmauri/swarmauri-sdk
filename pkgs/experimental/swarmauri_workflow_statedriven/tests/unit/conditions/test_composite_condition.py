# File: tests/workflows/conditions/test_composite_condition.py

import pytest
from swarmauri_workflow_statedriven.conditions.composite_condition import (
    AndCondition,
    OrCondition,
    NotCondition,
)
from swarmauri_workflow_statedriven.conditions.function_condition import (
    FunctionCondition,
)


@pytest.mark.unit
def test_and_condition_all_true():
    """
    File: workflows/conditions/composite_condition.py
    Class: AndCondition
    Method: evaluate

    Returns True when all sub‑conditions are True.
    """
    conds = [
        FunctionCondition(lambda s: True),
        FunctionCondition(lambda s: s.get("x", 0) > 0),
    ]
    and_cond = AndCondition(conds)
    assert and_cond.evaluate({"x": 5}) is True


@pytest.mark.unit
def test_and_condition_one_false():
    """
    File: workflows/conditions/composite_condition.py
    Class: AndCondition
    Method: evaluate

    Returns False if any sub‑condition is False.
    """
    conds = [FunctionCondition(lambda s: True), FunctionCondition(lambda s: False)]
    and_cond = AndCondition(conds)
    assert and_cond.evaluate({}) is False


@pytest.mark.unit
def test_and_condition_empty_list_yields_true():
    """
    File: workflows/conditions/composite_condition.py
    Class: AndCondition
    Method: evaluate

    `all([])` is True by definition.
    """
    and_cond = AndCondition([])
    assert and_cond.evaluate({}) is True


@pytest.mark.unit
def test_or_condition_all_false():
    """
    File: workflows/conditions/composite_condition.py
    Class: OrCondition
    Method: evaluate

    Returns False when all sub‑conditions are False.
    """
    conds = [FunctionCondition(lambda s: False), FunctionCondition(lambda s: 0)]
    or_cond = OrCondition(conds)
    assert or_cond.evaluate({}) is False


@pytest.mark.unit
def test_or_condition_one_true():
    """
    File: workflows/conditions/composite_condition.py
    Class: OrCondition
    Method: evaluate

    Returns True if any sub‑condition is True.
    """
    conds = [FunctionCondition(lambda s: False), FunctionCondition(lambda s: True)]
    or_cond = OrCondition(conds)
    assert or_cond.evaluate({}) is True


@pytest.mark.unit
def test_or_condition_empty_list_yields_false():
    """
    File: workflows/conditions/composite_condition.py
    Class: OrCondition
    Method: evaluate

    `any([])` is False by definition.
    """
    or_cond = OrCondition([])
    assert or_cond.evaluate({}) is False


@pytest.mark.unit
def test_not_condition_inverts_true_to_false():
    """
    File: workflows/conditions/composite_condition.py
    Class: NotCondition
    Method: evaluate

    Inverts a True sub‑condition to False.
    """
    cond = FunctionCondition(lambda s: True)
    not_cond = NotCondition(cond)
    assert not_cond.evaluate({}) is False


@pytest.mark.unit
def test_not_condition_inverts_false_to_true():
    """
    File: workflows/conditions/composite_condition.py
    Class: NotCondition
    Method: evaluate

    Inverts a False sub‑condition to True.
    """
    cond = FunctionCondition(lambda s: False)
    not_cond = NotCondition(cond)
    assert not_cond.evaluate({}) is True
