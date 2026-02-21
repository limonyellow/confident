from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from pydantic._internal._config import config_keys
from pydantic_settings import SettingsConfigDict

from confident.config_source import ConfigSource


class ConfidentConfigDict(SettingsConfigDict, total=False):  # type: ignore[misc]
    files: str | Path | List[str | Path]
    ignore_missing_files: bool
    map_name: str
    map_field: str
    config_map: Path | Dict[str, Any]
    source_priority: List[ConfigSource]
    specs: Any
    specs_path: str | Path


# Register confident keys so pydantic recognizes them during model creation.
config_keys |= set(ConfidentConfigDict.__annotations__.keys())
