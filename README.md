# Confident
Confident helps you create configuration objects from multiple sources such as files and environment variables.  
Confident configuration objects are data models that enforce validation and type hints by using [pydantic](https://pydantic-docs.helpmanual.io/) library.
For simple configuration loading from environment variables, you might want to check pydantic's [`BaseSettings`](https://pydantic-docs.helpmanual.io/usage/settings/) model.

With Confident you can manage multiple configurations depend on the environment your code is deployed.
While having lots of flexibility how to describe your config objects, Confident will provide visibility of the loading config 
process and help you expose mis-configuration as soon a possible.

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
title: my_yaml_ap
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
depends on a given key. 
This key is called `deployment_field` and it is one of the config object properties.  
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
    current_deployment: str = 'local'  # <-- This will be our `deployment_field`.
    host: str
    port: int = 5000
    log_level: str = 'error'
```
Now we can create the config object in several ways:
```python
# Using python dict:
config_a = MainConfig(deployment_field='current_deployment', deployments=multi_configs)
print(config_a)
#> current_deployment='local' host='localhost' port=5000 log_level='debug'

# Same, but from a file path:
config_b = MainConfig(deployment_field='current_deployment', deployments='app/configs.json')
print(config_b)
#> current_deployment='local' host='localhost' port=5000 log_level='debug'
```
Notice that the `deployment_field` as every other field, can be loaded from a source.
```python
os.environ['current_deployment'] = 'dev'  # Setting the field as an environment variable.
config_c = MainConfig(deployment_field='current_deployment', deployments='app/configs.json')
print(config_c)
#> current_deployment='dev' host='http://dev_server' port=5000 log_level='debug'
```
Selecting the `deployment_field` can be done in class definition using `DeploymentField`.  
`DeploymentField` has the same functionality as pydantic [`Field`](https://pydantic-docs.helpmanual.io/usage/schema/#field-customization).
```python
import os

from confident import Confident, DeploymentField

class MainConfig(Confident):
    deployment: str = DeploymentField('local')  # <-- This will be our `deployment_field`.
    host: str
    port: int = 5000
    log_level: str = 'error'

os.environ['deployment'] = 'prod'
config_d = MainConfig(deployments='app/configs.json')  # <-- No need to mention the `deployment_field`.
print(config_d)
#> deployment='prod' host='https://prod_server' port=5000 log_level='info'
```

## Contributing
To contribute to Confident, please make sure that any new features or changes to existing functionality include test coverage.

### Creating Distribution
Build the distribution:  
```python setup.py sdist bdist_wheel```

Upload to pypi:  
```twine upload dist/confident-<version>*```