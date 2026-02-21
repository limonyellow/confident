# Visibility

Confident provides built-in functions to show details about the object after creation.
The details can be logged/printed and provide clarity about the source of every value in the object.

## Multiple Sources Recognition

In order to monitor which fields were loaded from what source, `full_fields()` can be used.
Notice the difference between the source types:

```python
import os
from typing import List

from confident import BaseConfig
from confident.config_dict import ConfidentConfigDict

class AppConfig(BaseConfig):
    model_config = ConfidentConfigDict(
        files=['config.yaml'],
    )

    title: str = 'my_application'
    timeout: int
    input_paths: List[str]

os.environ['input_paths'] = '["/tmp/input_a", "/tmp/input_b"]'

config = AppConfig()

print(config.full_fields())
#> {
# 'title': ConfigField(name='title', value='my_application', origin_value='my_application', source_name='AppConfig', source_type='class_default', source_location=WindowsPath('example.py')),
# 'timeout': ConfigField(name='timeout', value=60, origin_value=60, source_name='config.yaml', source_type='file', source_location=WindowsPath('config.yaml')),
# 'input_paths': ConfigField(name='input_paths', value=['/tmp/input_a', '/tmp/input_b'], origin_value='["/tmp/input_a", "/tmp/input_b"]', source_name='input_paths', source_type='env_var', source_location='input_paths'),
# }
```

## BaseConfig Object Source Priority
The list of sources to load into the object, from the highest priority to the lowest:
```python
config.__source_priority__

#> ['init', 'env_var', 'map', 'file', 'class_default']
```

## BaseConfig Object Creation Location

The position of the `BaseConfig` class declaration:
```python
config.__specs__.class_path

#> PosixPath('~/MyProject/project_config.py')
```

The position of the `BaseConfig` object instance creation:
```python
config.__specs__.creation_path

#> PosixPath('~/MyProject/main.py')
```
