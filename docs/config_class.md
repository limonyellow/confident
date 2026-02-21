# BaseConfig Settings


## Model Config

In addition to defining the object's behaviour by inserting key-value arguments,
it is possible to change class behaviour using the `model_config` dictionary with `ConfidentConfigDict`.
This configuration method is similar to pydantic's [`model_config`](https://docs.pydantic.dev/latest/concepts/config/).

```python
from confident import BaseConfig
from confident.config_dict import ConfidentConfigDict

class MyConfig(BaseConfig):
    model_config = ConfidentConfigDict(
        files=['app_config/config1.json', 'app_config/config2.yaml'],
        ignore_missing_files=True,
    )

    title: str
    port: int = 5000
    retry: bool = False
```


This is equivalent to using the `from_sources` classmethod:

```python
from confident import BaseConfig

class MyConfig(BaseConfig):
    title: str
    port: int = 5000
    retry: bool = False

config = MyConfig.from_sources(
    files=['app_config/config1.json', 'app_config/config2.yaml'],
    ignore_missing_files=True,
)
```


## Changing The Loading Priority

It is possible to change the loading order of fields from different sources.
If a field value is present in multiple sources, the value from the highest priority source will be chosen and override the others.
`source_priority` is an attribute that holds a list of `ConfigSource` - The first will have the highest priority and the last will have the lowest.
**Sources whose enum does not appear in the `source_priority` list will not be loaded to the created object.**

```python
from confident import BaseConfig, ConfigSource
from confident.config_dict import ConfidentConfigDict

class MyConfig(BaseConfig):
    model_config = ConfidentConfigDict(
        # Here we define that environment vars will have the highest priority (even before explicit values).
        # Values from files and config maps will have lower priority than default values.
        source_priority=[
            ConfigSource.env_var, ConfigSource.init, ConfigSource.class_default, ConfigSource.map, ConfigSource.file
        ],
    )

    host: str
    port: int = 5000
```
