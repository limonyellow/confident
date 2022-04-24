Confident
=========
.. image:: https://img.shields.io/pypi/pyversions/confident?style=plastic   :alt: PyPI - Python Version
    :target: https://github.com/limonyellow/confident
.. image:: https://img.shields.io/pypi/v/confident?style=plastic&color=%2334D058   :alt: PyPI
    :target: https://pypi.org/project/confident/
.. image:: https://img.shields.io/github/workflow/status/limonyellow/confident/Python%20package/main?style=plastic   :alt: GitHub Workflow Status (branch)
    :target: https://github.com/limonyellow/confident/actions
.. image:: https://img.shields.io/github/license/limonyellow/confident?style=plastic   :alt: GitHub License
    :target: https://github.com/limonyellow/confident

**Confident** helps you create configuration objects from multiple sources such as files and environment variables.
Confident config objects are data models that enforce validation and type hints by using `pydantic <https://pydantic-docs.helpmanual.io/>`_ library.

With Confident you can manage multiple configurations depend on the environment your code is deployed.
While having lots of flexibility how to describe your config objects, Confident will provide visibility of the process
and help you expose misconfiguration as soon as possible.

Example
-------
.. code-block:: python
    :linenos:

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

Capabilities
------------
Confident object can load config fields from multiple sources:

- Environment variables.
- Config files such as 'json' and 'yaml'.
- '.env' files.
- Explicitly given fields.
- Default values.
- Deployment configs. (See below)

Loading capabilities can be customized easily.
Confident handles the loading and then provides ways to understand which value was loaded from what source.

Confident object core functionality is based on `pydantic <https://pydantic-docs.helpmanual.io/>`_ library.
That means the Confident config object has all the benefits of pydantic's `BaseModel  <https://pydantic-docs.helpmanual.io/usage/models/>`_ including
Type validation, `object transformation <https://pydantic-docs.helpmanual.io/usage/exporting_models/>`_ and many more features.

Contents
--------

.. toctree::
    :maxdepth: 3

    usage
    deployment_config
    config_class
    visibility
    validation
