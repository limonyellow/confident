.. _config_class:

Object Settings
===============

`ConfidentConfig` class
-----------------------

In addition to defining the object's behaviour by inserting key-value arguments,
it is possible to change class behaviour using `ConfidentConfig` class.
This configuration method is similar to `pydantic` `Config <https://pydantic-docs.helpmanual.io/usage/model_config/>`_ model.

.. code-block:: python
    :linenos:

    from confident import Confident

    class MyConfig(Confident):
        title: str
        port: int = 5000
        retry: bool = False

        class ConfidentConfig:  # In this class the specifications of `MyConfig` will be defined.
            deployment_config = 'deploy.json'
            files = ['app_config/config1.json', 'app_config/config2.yaml']
            ignore_missing_files = True


This is equivalent to:

.. code-block:: python
    :linenos:

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


Changing The Loading Priority
-----------------------------

It is possible to change the loading order of fields from different sources.
If a field value is present in multiple sources, the value from the highest priority source will be chosen and override the others.
`source_priority` is an attribute that holds a list of `ConfigSource` enums - The first will have the highest priority and the last will have the lowest.
**Sources that their enum will not appear in the `source_priority` list, will not be loaded to the created object.**

.. code-block:: python
    :linenos:

    from confident import Confident, ConfigSource

        class MyConfig(Confident):
            host: str
            port: int = 5000

            class ConfidentConfig:
                # Here we define that environment vars will have the highest priority (even before explicit values).
                # Values from files and deployments will have lower priority than default values.
                source_priority = [
                    ConfigSource.env_var, ConfigSource.explicit, ConfigSource.class_default, ConfigSource.deployment, ConfigSource.file
                ]
