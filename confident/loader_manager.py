from typing import Any, Callable, Dict, List

from confident.config_field import ConfigField
from confident.config_source import ConfigSource
from confident.loaders.source_loader_base import SourceLoader


class _SimpleSettingsSource:
    """A simple callable settings source wrapping a dict of values."""

    def __init__(self, values: dict[str, Any]) -> None:
        self._values = values

    def __call__(self) -> dict[str, Any]:
        return self._values


class LoaderManager:
    def __init__(
        self,
        settings_obj: object,
        source_priority: List[ConfigSource],
        init_settings_callable: Callable[..., Any] | None = None,
        env_settings_callable: Callable[..., Any] | None = None,
        file_secret_settings_callable: Callable[..., Any] | None = None,
        loaders: List[SourceLoader] | None = None,
    ) -> None:
        self.settings_obj = settings_obj
        self.init_settings_callable = init_settings_callable
        self.env_settings_callable = env_settings_callable
        self.file_secret_settings_callable = file_secret_settings_callable
        self.loaders = loaders or []
        self.source_priority = source_priority
        self.all_loaded_fields: Dict[ConfigSource, Dict[str, ConfigField]] = {}
        self.full_fields: Dict[str, ConfigField] = {}

    def load_all(self):
        loaders_dict = {loader.NAME: loader for loader in self.loaders}
        for source in self.source_priority:
            if source is ConfigSource.map:
                continue
            self.all_loaded_fields[source] = {
                field.name: field
                for field in loaders_dict[source].load_fields(
                    settings=self.settings_obj
                )
            }

        # Load the map config last.
        if ConfigSource.map in self.source_priority:
            self.all_loaded_fields[ConfigSource.map] = {
                field.name: field
                for field in loaders_dict[ConfigSource.map].load_fields(
                    settings=self.settings_obj
                )
            }

        # Build full_fields: highest priority source wins per field.
        self.full_fields = {}
        for source in reversed(self.source_priority):
            for name, field in self.all_loaded_fields.get(source, {}).items():
                self.full_fields[name] = field

        # Return source callables that return plain value dicts.
        # The first callable has the highest priority and so on.
        source_callables = []
        for source in self.source_priority:
            fields = self.all_loaded_fields.get(source, {})
            values = {name: cf.value for name, cf in fields.items()}
            source_callables.append(_SimpleSettingsSource(values))

        return tuple(source_callables)
