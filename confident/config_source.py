from enum import Enum


class ConfigSource(str, Enum):
    """
    Possible kinds of configuration sources.
    """
    env_var = 'env_var'
    file = 'file'
    explicit = 'explicit'
    class_default = 'class_default'
    deployment = 'deployment'
