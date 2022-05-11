from typing import List, Callable

from pydantic import BaseSettings

from confident.config_property import ConfigProperty
from confident.config_source import ConfigSource
from confident.loaders.source_loader_base import SourceLoader


class InitSourceLoader(SourceLoader):
    NAME = ConfigSource.init

    def __init__(self, init_settings_callable: Callable, **kwargs):
        super().__init__(**kwargs)
        self.init_settings_callable = init_settings_callable

    def load_fields(self, settings: BaseSettings) -> List[ConfigProperty]:
        fields = self.init_settings_callable(settings=settings)
        full_fields = [
            ConfigProperty(
                name=key, value=value, source_name=ConfigSource.init, source_type=ConfigSource.init,
                source_location=self.specs.creation_path
            ) for key, value in fields.items()
        ]
        return full_fields
