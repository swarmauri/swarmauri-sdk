from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Literal, Mapping


@dataclass(frozen=True)
class ProcessRequest:
    """Describe a command and its execution context."""

    argv: tuple[str, ...]
    cwd: str | None = None
    env: Mapping[str, str] | None = None
    timeout: float | None = None
    workspace: str | None = None

    def __post_init__(self):
        if not self.argv or not self.argv[0]:
            raise ValueError("A command is required")
        if self.timeout is not None and self.timeout <= 0:
            raise ValueError("Timeout must be positive")


@dataclass(frozen=True)
class ProcessHandle:
    """Identify a process owned by one backend instance."""

    id: str


@dataclass(frozen=True)
class ProcessEvent:
    """Report output bytes or the final process outcome."""

    sequence: int
    kind: Literal["stdout", "stderr", "exit"]
    data: bytes = b""
    exit_code: int | None = None
    outcome: Literal["exited", "cancelled", "timed_out"] | None = None


@dataclass(frozen=True)
class ProcessOutput:
    """Return a bounded page of output and its continuation cursor."""

    events: tuple[ProcessEvent, ...] = field(default_factory=tuple)
    cursor: int = 0
    truncated: bool = False


class IProcessBackend(ABC):
    """Run a process and interact with it by handle."""

    @abstractmethod
    def start(self, request: ProcessRequest) -> ProcessHandle:
        pass

    @abstractmethod
    def read(
        self, handle: ProcessHandle, *, after: int = 0, wait: float = 0
    ) -> ProcessOutput:
        pass

    @abstractmethod
    def write_stdin(
        self, handle: ProcessHandle, data: bytes, *, close: bool = False
    ) -> None:
        pass

    @abstractmethod
    def cancel(self, handle: ProcessHandle) -> bool:
        pass

    @abstractmethod
    def release(self, handle: ProcessHandle) -> None:
        pass
