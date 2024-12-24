from typing import Any, Dict, List, Literal, Optional, Type, Union
from pydantic import Field

from swarmauri_base.swarms.SwarmBase import SwarmBase


class Swarm(SwarmBase):
    """Concrete implementation of SwarmBase for task processing"""

    type: Literal["Swarm"] = "Swarm"
    agent_class: Type[Any] = Field(description="Agent class to use for swarm")
    task_batch_size: int = Field(default=1, gt=0)

    def _create_agent(self) -> Any:
        """Create new agent instance"""
        return self.agent_class()

    async def _execute_task(self, task: Any, agent_id: int, **kwargs) -> Dict[str, Any]:
        """Execute task using specified agent"""
        agent = self._agents[agent_id]
        try:
            result = await agent.process(task, **kwargs)
            return {
                "agent_id": agent_id,
                "status": SwarmStatus.COMPLETED,
                "result": result,
            }
        except Exception as e:
            return {"agent_id": agent_id, "status": SwarmStatus.FAILED, "error": str(e)}

    async def exec(
        self, input_data: Union[List[str], Any] = [], **kwargs: Optional[Dict]
    ) -> List[Dict[str, Any]]:
        """Execute tasks in parallel using available agents"""
        results = await super().exec(input_data, **kwargs)
        return results
