import asyncio
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import ConfigDict, Field
from enum import Enum
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.swarms.ISwarm import ISwarm


class SwarmStatus(Enum):
    IDLE = "IDLE"
    WORKING = "WORKING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class SwarmBase(ISwarm, ComponentBase):
    """Base class for Swarm implementations"""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    resource: Optional[str] = Field(default=ResourceTypes.SWARM.value, frozen=True)
    type: Literal["SwarmBase"] = "SwarmBase"

    num_agents: int = Field(default=5, gt=0, le=100)
    agent_timeout: float = Field(default=1.0, gt=0)
    max_retries: int = Field(default=3, ge=0)
    max_queue_size: int = Field(default=10, gt=0)

    _agents: List[Any] = []
    _task_queue: Optional[asyncio.Queue] = None
    _status: Dict[int, SwarmStatus] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._task_queue = asyncio.Queue(maxsize=self.max_queue_size)
        self._initialize_agents()

    def _initialize_agents(self):
        self._agents = [self._create_agent() for _ in range(self.num_agents)]
        self._status = {i: SwarmStatus.IDLE for i in range(self.num_agents)}

    def _create_agent(self) -> Any:
        """create specific agent types"""
        raise NotImplementedError("Agent creation method not implemented")

    @property
    def agents(self) -> List[Any]:
        return self._agents

    @property
    def queue_size(self) -> int:
        return self._task_queue.qsize()

    def get_swarm_status(self) -> Dict[int, SwarmStatus]:
        return self._status

    async def _process_task(self, agent_id: int, task: Any, **kwargs) -> Any:
        self._status[agent_id] = SwarmStatus.WORKING
        try:
            for _ in range(self.max_retries):
                try:
                    result = await asyncio.wait_for(
                        self._execute_task(task, agent_id, **kwargs),
                        timeout=self.agent_timeout,
                    )
                    self._status[agent_id] = SwarmStatus.COMPLETED
                    return result
                except asyncio.TimeoutError:
                    continue
            self._status[agent_id] = SwarmStatus.FAILED
            return None
        except Exception as e:
            self._status[agent_id] = SwarmStatus.FAILED
            raise e

    async def _execute_task(self, task: Any, agent_id: int) -> Any:
        """Override this method to implement specific task execution logic"""
        raise NotImplementedError("Task execution method not implemented")

    async def exec(
        self, input_data: Union[List[str], Any] = [], **kwargs: Optional[Dict]
    ) -> List[Any]:
        tasks = input_data if isinstance(input_data, list) else [input_data]
        for task in tasks:
            await self._task_queue.put(task)

        results = []
        while not self._task_queue.empty():
            available_agents = [
                i for i, status in self._status.items() if status == SwarmStatus.IDLE
            ]
            if not available_agents:
                await asyncio.sleep(0.1)
                continue

            task = await self._task_queue.get()
            agent_id = available_agents[0]
            result = await self._process_task(agent_id, task, **kwargs)
            if result is not None:
                results.append(result)

        return results
