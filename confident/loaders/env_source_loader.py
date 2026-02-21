import os
from typing import Callable, List

from pydantic_settings import BaseSettings

from confident.config_field import ConfigField
from confident.config_source import ConfigSource
from confident.loaders.source_loader_base import SourceLoader
from confident.utils import convert_field_value


class EnvSourceLoader(SourceLoader):
    NAME = ConfigSource.env_var

    def __init__(self, env_settings_callable: Callable, **kwargs):
        super().__init__(**kwargs)
        self.env_settings_callable = env_settings_callable

    def load_fields(self, settings: BaseSettings) -> List[ConfigField]:
        """
        Finds and loads requested settings fields from environment variables into a dictionary.
        """
        fields = self.env_settings_callable()

        # pydantic-settings v2 may filter out env vars parsed to None (e.g. "null").
        # Supplement with direct os.environ lookups for any missing model fields.
        for field_name in type(settings).model_fields:
            if field_name not in fields:
                env_value = os.environ.get(field_name) or os.environ.get(
                    field_name.upper()
                )
                if env_value is not None:
                    fields[field_name] = env_value

        full_fields = [
            ConfigField(
                name=key,
                value=convert_field_value(
                    settings=settings, field_name=key, origin_value=value
                ),
                origin_value=value,
                source_name=key,
                source_type=ConfigSource.env_var,
                source_location=key,
            )
            for key, value in fields.items()
        ]
        return full_fields
