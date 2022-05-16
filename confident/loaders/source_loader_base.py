from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseSettings

from confident.specs import SettingsSpecs
from confident.config_field import ConfigField


class SourceLoader(ABC):
    NAME = ...

    def __init__(self, specs: SettingsSpecs = None):
        self.specs = specs or SettingsSpecs()

    @abstractmethod
    def load_fields(self, settings: BaseSettings) -> List[ConfigField]:
        ...
