"""
Gateway-side adapter for Task.get.

Keeps the gateway thin and re-uses core logic (CHI pattern).
"""

from typing import Any, Dict

from peagen.core.task_core import get_task_result


async def task_get_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    *payload* comes straight from the JSON-RPC dispatcher:

        {"taskId": "uuid-str"}
    """
    task_id = payload["taskId"]
    return await get_task_result(task_id)
