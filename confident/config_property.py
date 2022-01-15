from typing import Any

from config_source import ConfigSource
from pydantic.main import BaseModel


class ConfigProperty(BaseModel):
    """
    Holds details of a single configuration variable and its value.
    """
    name: str
    value: Any
    value_type: type
    source_name: str
    source_type: ConfigSource
    source_location: str

    def __init__(self, value: Any, **kwargs):
        value_type = type(value)
        super().__init__(value=value, value_type=value_type, **kwargs)
