from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from pydantic import BaseModel, Field, ConfigDict
import tomllib


class WorkspaceConfig(BaseModel):
    org: str
    template_set: str | None = None
    workers: int | None = None


class LLMConfig(BaseModel):
    default_provider: str
    default_model_name: str
    default_temperature: float | None = None
    default_max_tokens: int | None = None
    providers: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")


class StorageConfig(BaseModel):
    default_storage_adapter: str
    adapters: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class PublishersConfig(BaseModel):
    default_publisher: str
    adapters: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class PluginsConfig(BaseModel):
    mode: str
    switch: Dict[str, str] | None = None


class EvaluatorConfig(BaseModel):
    cls: str
    model_config = ConfigDict(extra="allow")


class EvaluationConfig(BaseModel):
    pool: str | None = None
    max_workers: int | None = None
    async_: bool | None = Field(default=None, alias="async")
    strict: bool | None = None
    evaluators: Dict[str, EvaluatorConfig] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)


class PeagenConfig(BaseModel):
    workspace: WorkspaceConfig
    llm: LLMConfig
    storage: StorageConfig
    publishers: PublishersConfig
    plugins: PluginsConfig | None = None
    evaluation: EvaluationConfig | None = None
    model_config = ConfigDict(extra="allow")


class ConfigLoader:
    """Load and provide access to ``.peagen.toml`` configuration."""

    _instance: ConfigLoader | None = None

    def __new__(cls, start_dir: Path | None = None, path: Path | None = None) -> "ConfigLoader":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load(start_dir or Path.cwd(), path)
        return cls._instance

    # ------------------------------------------------------------------ private
    def _load(self, start_dir: Path, path: Path | None) -> None:
        cfg_path = self._find_config(start_dir, path)
        data: Dict[str, Any] = {}
        if cfg_path is not None:
            text = Path(cfg_path).read_text("utf-8")
            data = tomllib.loads(text)
        self._config = self._parse(data)

    @staticmethod
    def _find_config(start_dir: Path, path: Path | None) -> Path | None:
        if path:
            p = path.expanduser().resolve()
            return p if p.is_file() else None
        for folder in [start_dir, *start_dir.parents]:
            cfg = folder / ".peagen.toml"
            if cfg.is_file():
                return cfg
        return None

    @staticmethod
    def _parse(data: Dict[str, Any]) -> PeagenConfig:
        llm = data.get("llm", {})
        providers = {k: v for k, v in llm.items() if isinstance(v, dict)}
        llm_cfg = {
            **{k: v for k, v in llm.items() if not isinstance(v, dict)},
            "providers": providers,
        }

        storage = data.get("storage", {})
        storage_cfg = {
            "default_storage_adapter": storage.get("default_storage_adapter"),
            "adapters": storage.get("adapters", {**{k: v for k, v in storage.items() if k != "default_storage_adapter"}}),
        }

        publishers = data.get("publishers", {})
        publishers_cfg = {
            "default_publisher": publishers.get("default_publisher"),
            "adapters": publishers.get("adapters", {**{k: v for k, v in publishers.items() if k != "default_publisher"}}),
        }

        parsed = PeagenConfig(
            workspace=data.get("workspace", {}),
            llm=llm_cfg,
            storage=storage_cfg,
            publishers=publishers_cfg,
            plugins=data.get("plugins"),
            evaluation=data.get("evaluation"),
            **{k: v for k, v in data.items() if k not in {"workspace", "llm", "storage", "publishers", "plugins", "evaluation"}},
        )
        return parsed

    # ------------------------------------------------------------------ public
    @property
    def config(self) -> PeagenConfig:
        return self._config

    def reload(self, start_dir: Path | None = None, path: Path | None = None) -> None:
        self._load(start_dir or Path.cwd(), path)
