# Confident
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/confident?style=plastic)
![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/limonyellow/confident/Python%20package/main?style=plastic)
![GitHub](https://img.shields.io/github/license/limonyellow/confident?style=plastic)

Confident helps you create configuration objects from multiple sources such as files and environment variables.  
Confident config objects are data models that enforce validation and type hints by using [pydantic](https://pydantic-docs.helpmanual.io/) library.

With Confident you can manage multiple configurations depend on the environment your code is deployed.
While having lots of flexibility how to describe your config objects, Confident will provide visibility of the process 
and help you expose misconfiguration as soon as possible.

For simple configuration loading from environment variables, you might want to check pydantic's [`BaseSettings`](https://pydantic-docs.helpmanual.io/usage/settings/) model.

## Example
```python
import os

from confident import Confident


# Creating your own config class by inheriting from `Confident`.
class MyAppConfig(Confident):
    port: int = 5000
    host: str = 'localhost'
    labels: list


# Illustrates some environment variables.
os.environ['host'] = '127.0.0.1'
os.environ['labels'] = '["FOO", "BAR"]'  # JSON strings can be used for more types.


# Creating the config object. `Confident` will load the values of the properties.
config = MyAppConfig()

print(config.host)
#> 127.0.0.1
print(config.json())
#> {"port": 5000, "host": "127.0.0.1", "labels": ["FOO", "BAR"]}
print(config)
#> port=5000 host='127.0.0.1' labels=['FOO', 'BAR']
print(config.full_details())
#> {
# 'port': ConfigProperty(name='port', value=5000, origin_value=5000, source_name='MyAppConfig', source_type='class_default', source_location=PosixPath('~/confident/readme_example.py')),
# 'host': ConfigProperty(name='host', value='127.0.0.1', origin_value='127.0.0.1', source_name='host', source_type='env_var', source_location='host'),
# 'labels': ConfigProperty(name='labels', value=['FOO', 'BAR'], origin_value='["FOO", "BAR"]', source_name='labels', source_type='env_var', source_location='labels')
# }

```

## Installation
```pip install confident```

## Capabilities
Confident object can load config fields from multiple sources:
- Environment variables.
- Config files such as 'json' and 'yaml'.
- '.env' files.
- Explicitly given fields.
- Default values.
- Deployment configs. (See below)

Confident object core functionality is based on [pydantic](https://pydantic-docs.helpmanual.io/) library. 
That means the Confident config object has all the benefits of pydantic's [`BaseModel`](https://pydantic-docs.helpmanual.io/usage/models/) including
Type validation, [object transformation](https://pydantic-docs.helpmanual.io/usage/exporting_models/) and many more features.

## Usage
### Load Config files
Confident supports `json`, `yaml` and `.env` files.  
#### `app_config/config1.json`
```json
{
  "title": "my_app_1",
  "retry": true,
  "timeout": 10
}
``` 

#### `app_config/config2.yaml`
```yaml
title: my_yaml_app
port: 3030
``` 

```python
from confident import Confident


class MyConfig(Confident):
    title: str
    port: int = 5000
    retry: bool = False

config = MyConfig(files=['app_config/config1.json', 'app_config/config2.yaml'])

print(config)
#> title='my_app_1' port=3030 retry=True
```

### Load deployment configs
Deployment config in Confident is basically a dictionary of configurations values that only one will be loaded in execution time
depends on a given `deployment_name`. 
`deployment_name` can be determent explicitly or according to the value of `deployment_field` which is one of the config object properties.  
For having the following deployment configurations (can also specified in a `json` or `yaml` file):
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
#### `app/configs.json`
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
The config class definition can be as follows:
```python
from confident import Confident

class MainConfig(Confident):
    host: str
    port: int = 5000
    log_level: str = 'error'
```
Now we can create the config object in several ways:
```python
# Using python dict:
config_a = MainConfig(deployment_name='local', deployments=multi_configs)
print(config_a)
#> host='localhost' port=5000 log_level='debug'

# Same, but from a file path:
config_b = MainConfig(deployment_name='local', deployments='app/configs.json')
print(config_b)
#> host='localhost' port=5000 log_level='debug'
```



### deployment_field
If we want more flexibility in selecting the deployment to load, we can use a property to do so.  
`deployment_field` is a field declared in the `Confident` object that its value will define what will be the `deployment_name`.
```python
from confident import Confident

class MainConfig(Confident):
    current_deployment: str = 'local'  # <-- This will be our `deployment_field`.
    host: str
    port: int = 5000
    log_level: str = 'error'
```
Now we can create the config object:
```python
config_a = MainConfig(deployment_field='current_deployment', deployments=multi_configs)
print(config_a)
#> current_deployment='local' host='localhost' port=5000 log_level='debug'
```
In the above example the `deployment_field` is `current_deployment`, the `deployment_name` in run time is `local` so the matching properties are loaded from the `deployment_config`.  
Notice that the `deployment_field` as every other field, can be loaded from a source:
```python
os.environ['current_deployment'] = 'dev'  # Setting the field as an environment variable.
config_c = MainConfig(deployment_field='current_deployment', deployments='app/configs.json')
print(config_c)
#> current_deployment='dev' host='http://dev_server' port=5000 log_level='debug'
```
Selecting the `deployment_field` can be done in class definition using `DeploymentField`.  
`DeploymentField` has the same functionality as pydantic [`Field`](https://pydantic-docs.helpmanual.io/usage/schema/#field-customization).  
Moreover, it is possible to declare the `deployment_field` inside a `ConfidentConfig` class (See below).
#### Declaration with `DeploymentField`:
```python
from confident import Confident, DeploymentField

class MainConfig(Confident):
    deployment: str = DeploymentField('local')  # <-- This will be our `deployment_field`.
    host: str
    port: int = 5000
    log_level: str = 'error'
```
#### Declaration with `ConfidentConfig` class:
```python
from confident import Confident

class MainConfig(Confident):
    deployment: str = 'local'  
    host: str
    port: int = 5000
    log_level: str = 'error'
    
    class ConfidentConfig:
        deployment_field = 'deployment'  # <-- Marking `deployment` as our `deployment_field`.
```
#### Usage is the same in both methods:
```python
import os

os.environ['deployment'] = 'prod'

config = MainConfig(deployments='app/configs.json')  # <-- No need to mention the `deployment_field`.
print(config)
#> deployment='prod' host='https://prod_server' port=5000 log_level='info'
```

## `ConfidentConfig` class
In addition to defining the object's behaviour by inserting key-value arguments, 
it is possible to define several specifications in the class declaration:
```python
from confident import Confident

class MyConfig(Confident):
    title: str
    port: int = 5000
    retry: bool = False

    class ConfidentConfig:  # In this class the specifications of `MyConfig` will be defined.
        deployment_config = 'deploy.json'
        files = ['app_config/config1.json', 'app_config/config2.yaml']
        ignore_missing_files = True
```
This is equivalent to:
```python
from confident import Confident

class MyConfig(Confident):
    title: str
    port: int = 5000
    retry: bool = False

config = MyConfig(
    deployment_config='deploy.json',
    files=['app_config/config1.json', 'app_config/config2.yaml'],
    ignore_missing_files = True
)
```
This configuration method is similar to `pydantic` [`Config`](https://pydantic-docs.helpmanual.io/usage/model_config/) model.

## Changing the loading priority
It is possible to change the order that fields from different sources are loaded.
If a field value is present in multiple sources, the value from the highest priority source will be chosen and override the others.  
`source_priority` is an attribute that holds a list of `ConfigSource` enums - The first will have the highest priority and the last will have the lowest.  
**Sources that their enum will not appear in the `source_priority` list, will not be loaded to the created object.**
```python
from confident import Confident, ConfigSource

class MyConfig(Confident):
    host: str
    port: int = 5000

    class ConfidentConfig:
        # Here we define that environment vars will have the highest priority (even before explicit values)
        # Values from files and deployments will have lower priority than default values.
        source_priority = [
            ConfigSource.env_var, ConfigSource.explicit, ConfigSource.class_default, ConfigSource.deployment, ConfigSource.file
        ]
```

## Visibility and Validation
### Errors
In order to avoid misconfigurations, `Confident` will supply indicative errors in case of wrong values or wrong sequence of arguments. 
For instance:
- Wrong or missing files provided.
- Inserting both `deployment_name` and `deployment_field` (causing ambiguous deployment selection)
- Wrong types or missing values (by `pydantic` validation mechanism)

### Multiple sources recognition
Loading fields to `Confident` object from multiple sources can be complicated and should be reduced to minimum. Nevertheless, in some cases it can be required.  
In order to monitor which fields were loaded from what source, `full_details()` can be used.  
Notice the difference between the `source_type`s:

```python
import os
from typing import List

from confident import Confident

class AppConfig(Confident):
    title: str = 'my_application'
    timeout: int
    input_paths: List[str]

os.environ['input_paths'] = '["/tmp/input_a", "/tmp/input_b"]'

config = AppConfig(files='config.yaml')

print(config.full_details())
#> {
# 'title': ConfigProperty(name='title', value='my_application', origin_value='my_application', source_name='AppConfig', source_type='class_default', source_location=WindowsPath('example.py')), 
# 'timeout': ConfigProperty(name='timeout', value=60, origin_value=60, source_name='config.yaml', source_type='file', source_location=WindowsPath('config.yaml')), 
# 'input_paths': ConfigProperty(name='input_paths', value=['/tmp/input_a', '/tmp/input_b'], origin_value='["/tmp/input_a", "/tmp/input_b"]', source_name='input_paths', source_type='env_var', source_location='input_paths'), 
# }
```

### Confident Object Creation location
The position of the the `Confident` object declaration:
```python
config.specs().class_path
```
The position of the the `Confident` object instance creation:
```python
config.specs().creation_path
```


## Examples
More examples can be found in the project's [repository](https://github.com/limonyellow/confident).

## Contributing
To contribute to Confident, please make sure any new features or changes to existing functionality include test coverage.

### Creating Distribution
Build the distribution:  
```python setup.py sdist bdist_wheel```

Upload to pypi:  
```twine upload dist/confident-<version>*```
