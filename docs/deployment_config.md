# Config Maps

Config maps in Confident is basically a dictionary of configurations values.
Only one configuration will be loaded in execution time depends on a given `map_name`.
Config maps can be either python dict or a file (json or yaml).

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
config_a = MainConfig(_map_name='local', _config_map=multi_configs)
print(config_a)

#> host='localhost' port=5000 log_level='debug'

# Same, but from a file path:
config_b = MainConfig(_map_name='local', _config_map='app/configs.json')
print(config_b)

#> host='localhost' port=5000 log_level='debug'
```


## Map Field

If we want more flexibility in selecting the map to load, we can use a property to do so.
`map_field` is a field declared in the `Config` object that its value will define what will be the `map_name`.

```python
from confident import BaseConfig

class MainConfig(BaseConfig):
    current_map: str = 'local'  # <-- This will be our `map_field`.
    host: str
    port: int = 5000
    log_level: str = 'error'

    class Config:
        map_field = 'current_map'
```


Now we can create the config object:
```python
config_a = MainConfig(_config_map=multi_configs)
print(config_a)

#> current_map='local' host='localhost' port=5000 log_level='debug'
```

In the above example the `map_field` is `current_map`,
the `map_name` in run time is `local` so the matching properties are loaded from the `config_map`.
Notice that the `map_field` as every other field, can be loaded from a source:

```python
os.environ['current_map'] = 'dev'  # Setting the field as an environment variable.
config_c = MainConfig(_config_map='app/configs.json')
print(config_c)

#> current_deployment='dev' host='http://dev_server' port=5000 log_level='debug'
```

Selecting the `map_field` can be done in class definition using `MapField`.
`MapField` has the same functionality as pydantic [`Field`](https://pydantic-docs.helpmanual.io/usage/schema/#field-customization).

**Declaration with `MapField`:**

```python
from confident import BaseConfig, MapField

class MainConfig(BaseConfig):
    my_map: str = MapField('local')  # <-- This will be our `map_field`.
    host: str
    port: int = 5000
    log_level: str = 'error'
```

**Declaration with `Config` class:**
```python
from confident import Confident

class MainConfig(Confident):
    my_map: str = 'local'
    host: str
    port: int = 5000
    log_level: str = 'error'

    class ConfidentConfig:
        map_field = 'my_map'  # <-- Marking `my_map` as our `map_field`.
```

Usage is the same in both ways:

```python
import os

os.environ['my_map'] = 'prod'

config = MainConfig(_config_map='app/configs.json')
print(config)

#> my_map='prod' host='https://prod_server' port=5000 log_level='info'
```