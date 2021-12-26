from enum import Enum


class ConfigSource(str, Enum):
    """
    Possible kinds of configuration sources.
    """
    environment = 'environment'
    file = 'file'
    explicit = 'explicit'
    class_default = 'class_default'
