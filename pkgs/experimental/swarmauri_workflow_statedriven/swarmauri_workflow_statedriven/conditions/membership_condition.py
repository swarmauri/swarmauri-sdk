# File: swarmauri/workflows/conditions/membership_condition.py

from typing import Any, Dict
from swarmauri_workflow_statedriven.conditions.base import Condition


class MembershipCondition(Condition):
    """
    File: membership_condition.py
    Class: MembershipCondition
    Methods: __init__, evaluate

    Checks whether a given value is (or is not) a member of a state's output.
    """

    def __init__(self, node_name: str, member: Any, should_be_member: bool = True):
        """
        File: membership_condition.py
        Class: MembershipCondition
        Method: __init__

        Args:
            node_name: name of the state whose output is tested
            member: the value to check for membership
            should_be_member: True ⇒ require `member in output`
                               False ⇒ require `member not in output`
        """
        self.node_name = node_name
        self.member = member
        self.should_be_member = should_be_member

    def evaluate(self, state: Dict[str, Any]) -> bool:
        """
        File: membership_condition.py
        Class: MembershipCondition
        Method: evaluate

        Returns True if membership test matches should_be_member.
        """
        try:
            container = state[self.node_name]
            result = self.member in container
        except Exception:
            # Missing node or non‑iterable: treat as False membership
            return not self.should_be_member

        # If member is found and should_be_member=True → True,
        # if not found and should_be_member=False → True
        return result if self.should_be_member else not result
