"""Persistent asyncio runtime used by synchronous live sessions."""

import asyncio
import threading
from collections.abc import Awaitable, Callable
from concurrent.futures import Future
from typing import Any


class LiveSessionRuntime:
    def __init__(self) -> None:
        self._loop = asyncio.new_event_loop()
        self._started = threading.Event()
        self._thread = threading.Thread(
            target=self._run,
            name="swarmauri-live-session",
            daemon=True,
        )
        self._thread.start()
        self._started.wait()

    def _run(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._started.set()
        try:
            self._loop.run_forever()
        finally:
            pending = asyncio.all_tasks(self._loop)
            for task in pending:
                task.cancel()
            if pending:
                self._loop.run_until_complete(
                    asyncio.gather(*pending, return_exceptions=True)
                )
            self._loop.run_until_complete(self._loop.shutdown_asyncgens())
            self._loop.close()

    def submit(self, awaitable: Awaitable[Any]) -> Future[Any]:
        if not self._thread.is_alive():
            raise RuntimeError("Live session runtime is closed")
        return asyncio.run_coroutine_threadsafe(awaitable, self._loop)

    def create(self, factory: Callable[[], Awaitable[Any]]) -> Any:
        return self.submit(factory()).result()

    def close(self) -> None:
        if not self._thread.is_alive():
            return
        self._loop.call_soon_threadsafe(self._loop.stop)
        if threading.current_thread() is not self._thread:
            self._thread.join()

    @property
    def is_alive(self) -> bool:
        return self._thread.is_alive()
