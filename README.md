# Confident
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/confident?style=plastic)](https://github.com/limonyellow/confident)
[![PyPI](https://img.shields.io/pypi/v/confident?style=plastic&color=%2334D058)](https://pypi.org/project/confident/)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/limonyellow/confident/ci.yml?branch=main&style=plastic)](https://github.com/limonyellow/confident/actions)
[![GitHub](https://img.shields.io/github/license/limonyellow/confident?style=plastic)](https://github.com/limonyellow/confident)
[![Coverage](https://codecov.io/gh/limonyellow/confident/branch/main/graph/badge.svg)](https://codecov.io/gh/limonyellow/confident)
---

[**Documentation**](https://limonyellow.github.io/confident/)

---

Confident helps you create configuration objects from multiple sources such as files, environment variables and maps.
Confident's `BaseConfig` class is a data model that enforces validation and type hints by using [pydantic](https://docs.pydantic.dev/) library.

With Confident you can manage multiple configurations depending on the environment your code is deployed in.
While having lots of flexibility in how to describe your config objects, Confident will provide visibility of the process
and help you expose misconfiguration as soon as possible.


## Example

```python
import os

from confident import BaseConfig


# Creating your own config class by inheriting from `BaseConfig`.
class MyAppConfig(BaseConfig):
    port: int = 5000
    host: str = 'localhost'
    labels: list


# Illustrates some environment variables.
os.environ['host'] = '127.0.0.1'
os.environ['labels'] = '["FOO", "BAR"]'  # JSON strings can be used for more types.

# Creating the config object. `BaseConfig` will load the values of the properties.
config = MyAppConfig()

print(config.host)
# > 127.0.0.1
print(config.model_dump_json())
# > {"port":5000,"host":"127.0.0.1","labels":["FOO","BAR"]}
print(config)
# > port=5000 host='127.0.0.1' labels=['FOO', 'BAR']
print(config.full_fields())
# > {
# 'port': ConfigField(name='port', value=5000, origin_value=5000, source_name='MyAppConfig', source_type='class_default', source_location=PosixPath('~/confident/readme_example.py')),
# 'host': ConfigField(name='host', value='127.0.0.1', origin_value='127.0.0.1', source_name='host', source_type='env_var', source_location='host'),
# 'labels': ConfigField(name='labels', value=['FOO', 'BAR'], origin_value='["FOO", "BAR"]', source_name='labels', source_type='env_var', source_location='labels')
# }

```

## Installation
```shell
pip install confident
```

## Capabilities
### Customized Fields Loaders
Built-in loaders:

- Environment variables.
- Config files such as 'json' and 'yaml'.
- Config maps to load fields depending on the environment. (See documentation)

It is possible to configure the loading priority and add your own loader classes.

### Full Support of Pydantic BaseSettings
Confident core functionality is based on [pydantic](https://docs.pydantic.dev/) library.
That means `BaseConfig` object has all the benefits of pydantic's [`BaseModel`](https://docs.pydantic.dev/latest/concepts/models/)
and [`BaseSettings`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
including type validation, [object serialization](https://docs.pydantic.dev/latest/concepts/serialization/) and many more features.

### Config Loading Visibility
`BaseConfig` object stores details about the fields loading process and offers ways to understand the source of each loaded field.
Details about the origin value (before conversion), the location of the source and the type of loader, can all be accessed from the object.

## Examples
More examples can be found in the project's [repository](https://github.com/limonyellow/confident).

## Contributing
To contribute to Confident, please make sure any new features or changes to existing functionality include test coverage.
