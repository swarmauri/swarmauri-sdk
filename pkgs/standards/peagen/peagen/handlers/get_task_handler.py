"""
Gateway-side adapter for Task.get.

Keeps the gateway thin and re-uses core logic (CHI pattern).
"""

from typing import Any, Dict

# NOTE: importing get_task_result at module level introduces a circular import
# because `peagen.core.task_core` depends on `peagen.gateway` which imports this
# module. Import lazily within the handler instead.


async def task_get_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    *payload* comes straight from the JSON-RPC dispatcher:

        {"taskId": "uuid-str"}
    """
    task_id = payload["taskId"]
    from peagen.core.task_core import get_task_result

    return await get_task_result(task_id)
