# Config Maps

Config maps in Confident is basically a dictionary of configuration values.
Only one configuration will be loaded at execution time depending on a given `map_name`.
Config maps can be either a Python dict or a file (json or yaml).

```python
multi_configs = {
                    'prod': {
                        'host': 'https://prod_server',
                        'log_level': 'info'
                    },
                    'dev': {
                        'host': 'http://dev_server',
                        'log_level': 'debug'
                    },
                    'local': {
                        'host': 'localhost',
                        'log_level': 'debug'
                    },
}
```

**app/configs.json**

```json
{
    "prod": {
        "host": "https://prod_server",
        "log_level": "info"
    },
    "dev": {
        "host": "http://dev_server",
        "log_level": "debug"
    },
    "local": {
        "host": "localhost",
        "log_level": "debug"
    }
}
```

The BaseConfig class definition can be as follows:

```python
from confident import BaseConfig

class MainConfig(BaseConfig):
    host: str
    port: int = 5000
    log_level: str = 'error'
```

Now we can create the config object in several ways:

```python
# Using python dict:
config_a = MainConfig.from_map(config_map=multi_configs, map_name='local')
print(config_a)

#> host='localhost' port=5000 log_level='debug'

# Same, but from a file path:
config_b = MainConfig.from_map(config_map='app/configs.json', map_name='local')
print(config_b)

#> host='localhost' port=5000 log_level='debug'
```

You can also use `from_sources` to combine a config map with other sources:

```python
config_c = MainConfig.from_sources(
    config_map='app/configs.json',
    map_name='local',
    files='app/overrides.yaml',
)
print(config_c)

#> host='localhost' port=5000 log_level='debug'
```

## Map Field

If we want more flexibility in selecting the map to load, we can use a property to do so.
`map_field` is a field declared in the config object whose value will define what the `map_name` is.

### Declaration with `MapField`

The simplest way to declare a map field is to use `MapField` as the field's default value:

```python
from confident import BaseConfig, MapField

class MainConfig(BaseConfig):
    my_map: str = MapField('local')  # <-- This will be our `map_field`.
    host: str
    port: int = 5000
    log_level: str = 'error'
```

### Declaration with `model_config`

Alternatively, you can use `model_config` to specify which field is the map field:

```python
from confident import BaseConfig
from confident.config_dict import ConfidentConfigDict

class MainConfig(BaseConfig):
    model_config = ConfidentConfigDict(
        map_field='my_map',
    )

    my_map: str = 'local'
    host: str
    port: int = 5000
    log_level: str = 'error'
```

### Usage

Usage is the same in both ways:

```python
config_a = MainConfig.from_map(config_map=multi_configs)
print(config_a)

#> my_map='local' host='localhost' port=5000 log_level='debug'
```

Notice that the `map_field`, like every other field, can be loaded from any source:

```python
import os

os.environ['my_map'] = 'dev'  # Setting the field as an environment variable.
config_b = MainConfig.from_map(config_map='app/configs.json')
print(config_b)

#> my_map='dev' host='http://dev_server' port=5000 log_level='debug'
```

By setting `my_map` via an environment variable, the matching configuration (`dev`) is loaded from the config map.
