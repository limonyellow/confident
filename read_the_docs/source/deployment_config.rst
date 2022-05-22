.. _deployment_config:

Deployment config
=================

Deployment config in Confident is basically a dictionary of configurations values.
Only one configuration will be loaded in execution time depends on a given `deployment_name`.
Deployment configurations can be either python dict or a file (json or yaml).

.. code-block:: python
    :linenos:

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


**app/configs.json**

.. code-block:: console

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

The config class definition can be as follows:

.. code-block:: python
    :linenos:

    from confident import Confident

    class MainConfig(Confident):
        host: str
        port: int = 5000
        log_level: str = 'error'

Now we can create the config object in several ways:

.. code-block:: python
    :linenos:

    # Using python dict:
    config_a = MainConfig(deployment_name='local', deployments=multi_configs)
    print(config_a)
    #> host='localhost' port=5000 log_level='debug'

    # Same, but from a file path:
    config_b = MainConfig(deployment_name='local', deployments='app/configs.json')
    print(config_b)
    #> host='localhost' port=5000 log_level='debug'


Deployment Field
----------------
If we want more flexibility in selecting the deployment to load, we can use a property to do so.
`deployment_field` is a field declared in the `Confident` object that its value will define what will be the `deployment_name`.

.. code-block:: python
    :linenos:

    from confident import Confident

    class MainConfig(Confident):
        current_deployment: str = 'local'  # <-- This will be our `deployment_field`.
        host: str
        port: int = 5000
        log_level: str = 'error'


Now we can create the config object:

.. code-block:: python
    :linenos:

    config_a = MainConfig(deployment_field='current_deployment', deployments=multi_configs)
    print(config_a)
    #> current_deployment='local' host='localhost' port=5000 log_level='debug'


In the above example the `deployment_field` is `current_deployment`,
the `deployment_name` in run time is `local` so the matching properties are loaded from the `deployment_config`.
Notice that the `deployment_field` as every other field, can be loaded from a source:

.. code-block:: python
    :linenos:

    os.environ['current_deployment'] = 'dev'  # Setting the field as an environment variable.
    config_c = MainConfig(deployment_field='current_deployment', deployments='app/configs.json')
    print(config_c)
    #> current_deployment='dev' host='http://dev_server' port=5000 log_level='debug'


Selecting the `deployment_field` can be done in class definition using `DeploymentField`.
`DeploymentField` has the same functionality as pydantic `Field <https://pydantic-docs.helpmanual.io/usage/schema/#field-customization>`_.
Moreover, it is possible to declare the `deployment_field` inside a `ConfidentConfig` class (See below).

**Declaration with `DeploymentField`:**

.. code-block:: python
    :linenos:

    from confident import Confident, DeploymentField

    class MainConfig(Confident):
        deployment: str = DeploymentField('local')  # <-- This will be our `deployment_field`.
        host: str
        port: int = 5000
        log_level: str = 'error'


**Declaration with `ConfidentConfig` class:**

.. code-block:: python
    :linenos:

    from confident import Confident

    class MainConfig(Confident):
        deployment: str = 'local'
        host: str
        port: int = 5000
        log_level: str = 'error'

        class ConfidentConfig:
            deployment_field = 'deployment'  # <-- Marking `deployment` as our `deployment_field`.


Usage is the same in both ways:

.. code-block:: python
    :linenos:

    import os

    os.environ['deployment'] = 'prod'

    config = MainConfig(deployments='app/configs.json')  # <-- No need to mention the `deployment_field`.
    print(config)
    #> deployment='prod' host='https://prod_server' port=5000 log_level='info'
