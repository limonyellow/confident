from abc import ABC, abstractmethod
from typing import ClassVar, List

from pydantic_settings import BaseSettings

from confident.config_source import ConfigSource
from confident.specs import ConfigSpecs
from confident.config_field import ConfigField


class SourceLoader(ABC):
    NAME: ClassVar[ConfigSource]

    def __init__(self, specs: ConfigSpecs | None = None):
        self.specs = specs or ConfigSpecs()

    @abstractmethod
    def load_fields(self, settings: BaseSettings) -> List[ConfigField]: ...
