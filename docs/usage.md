# Basic Usage

## Load Environment Variables

Simply create an object.
Confident will load the property value from an environment variable with the same name if it exists.


```python
import os

from confident import BaseConfig


os.environ['port'] = '3000'

class MyConfig(BaseConfig):
    port: int

config = MyConfig()

print(config)

#> port=3000
```

## Load Default Values

Like in `dataclass` and `pydantic` classes, it is possible to declare default values of properties.


```python
from confident import BaseConfig


class MyConfig(BaseConfig):
    port: int = 3333

config = MyConfig()

print(config)

#> port=3333
```

## Load Config Files

Confident supports `json`, `yaml` and `.env` files.

**app_config/config1.json**

```json
{
  "title": "my_app_1",
  "retry": true,
  "timeout": 10
}
```

**app_config/config2.yaml**

```yaml
title: my_yaml_app
port: 3030
```

```python
from confident import BaseConfig


class MyConfig(BaseConfig):
    title: str
    port: int = 5000
    retry: bool = False

config = MyConfig.from_files(['app_config/config1.json', 'app_config/config2.yaml'])

print(config)

#> title='my_app_1' port=3030 retry=True
```

You can also use `from_sources` to combine files with other sources in a single call:

```python
config = MyConfig.from_sources(
    files=['app_config/config1.json', 'app_config/config2.yaml'],
    config_map='app/configs.json',
)
```
