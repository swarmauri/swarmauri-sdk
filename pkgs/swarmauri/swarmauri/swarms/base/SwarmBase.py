import asyncio
from typing import Any, List, Tuple
from swarmauri_core.swarms.ISwarm import ISwarm


class SwarmBase(ISwarm):
    def __init__(
        self, num_agents: int = 5, agent_timeout: float = 1.0, retry_attempts: int = 3
    ):
        self._agents: List[Any] = []
        self._num_agents = num_agents
        self._agent_timeout = agent_timeout
        self._retry_attempts = retry_attempts
        self._task_queue: asyncio.Queue = asyncio.Queue()
        self._results_queue: asyncio.Queue = asyncio.Queue()

    @property
    def num_agents(self) -> int:
        return self._num_agents

    def add_agent(self, agent: SwarmBaseAgent) -> None:
        self._agents.append(agent)
        self._num_agents = len(self._agents)

    def remove_agent(self, agent_id: int) -> None:
        if 0 <= agent_id < len(self._agents):
            self._agents.pop(agent_id)
            self._num_agents = len(self._agents)

    def replace_agent(self, agent_id: int, new_agent: SwarmBaseAgent) -> None:
        if 0 <= agent_id < len(self._agents):
            self._agents[agent_id] = new_agent

    def get_agent_statuses(self) -> List[Tuple[int, Any]]:
        return [(i, agent.status) for i, agent in enumerate(self._agents)]

    def distribute_task(self, task: Any) -> None:
        self._task_queue.put_nowait(task)

    def collect_results(self) -> List[Any]:
        results = []
        while not self._results_queue.empty():
            results.append(self._results_queue.get_nowait())
        return results

    def run(self, tasks: List[Any]) -> List[Any]:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.arun(tasks))
        finally:
            loop.close()

    async def arun(self, tasks: List[Any]) -> List[Any]:
        for task in tasks:
            await self._task_queue.put(task)

        agent_tasks = [
            asyncio.create_task(self._process_worker(agent)) for agent in self._agents
        ]
        await asyncio.gather(*agent_tasks)
        return await self._collect_results_async()

    def process_task(self, task: Any) -> Any:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.aprocess_task(task))
        finally:
            loop.close()

    async def aprocess_task(self, task: Any) -> Any:
        if not self._agents:
            raise RuntimeError("No agents available to process task")
        return await self._agents[0].process(task)

    async def _process_worker(self, agent: SwarmBaseAgent) -> None:
        retry_count = 0
        while retry_count < self._retry_attempts:
            try:
                task = await asyncio.wait_for(
                    self._task_queue.get(), timeout=self._agent_timeout
                )
                result = await agent.process(task)
                await self._results_queue.put(result)
                self._task_queue.task_done()
                break
            except Exception:
                retry_count += 1

    async def _collect_results_async(self) -> List[Any]:
        results = []
        while not self._results_queue.empty():
            results.append(await self._results_queue.get())
        return results
