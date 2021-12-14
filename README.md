# Confident
Confident helps you create configuration objects from multiple sources of variables such as files and environment variables.  
Confident configuration objects are data models that enforce validation and type hints by using [pydantic](https://pydantic-docs.helpmanual.io/) library.

## Example
```py
import os

from confident import Confident


# Creating your own config class by inheriting from `Confident`.
class MyAppConfig(Confident):
    name: str
    port: int = 5000
    host: str = 'localhost'


# Illustrates some environment variables.
os.environ['name'] = 'my_name' 
os.environ['host'] = '127.0.0.1'

# Creating the config object. `Confident` will insert the values of the properties.
config = MyAppConfig()

print(config.name)
#> my_name
print(config.json())
#> {"name": "my_name", "port": 5000, "host": "127.0.0.1"}
print(config)
#> name='my_name' port=5000 host='127.0.0.1'

```
## Installation
```pip install confident```

## Capabilities
Confident object can load config fields from multiple sources:
1. Environment variables.
1. Config files such as 'json' and 'yaml'.
1. '.env' files.
1. Explicitly given fields in the constructor level.
1. Default values.

Confident object core functionality is based on [pydantic](https://pydantic-docs.helpmanual.io/) library. 
That means the Confident config object has all the benefits of pydantic's [BaseModel](https://pydantic-docs.helpmanual.io/usage/models/) including
Type validation, [object transformation](https://pydantic-docs.helpmanual.io/usage/exporting_models/) and many more features.

## Usage
# Load Config files  


## Contributing
To contribute to Confident, please make sure that any new features or changes to existing functionality include test coverage.

### Creating Distribution
Build the distribution:  
```python3 setup.py sdist```

Upload to pypi:  
```twine upload dist/*```