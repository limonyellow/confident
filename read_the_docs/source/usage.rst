.. _usage:

Basic Usage
===========

.. _installation:

Installation
------------

Install using pip:

.. code-block:: console

   (.venv) $ pip install confident

Load Environment Variables
--------------------------
Simply create an object.
Confident will load the property value from environment variable with the same name if exists.

.. code-block:: python
    :linenos:

    import os

    from confident import Confident


    os.environ['port'] = 3000

    class MyConfig(Confident):
        port: int

    config = MyConfig()

    print(config)
    #> port=3000


Load Default Values
-------------------
Like in `dataclass` and `pydantic` classes, it is possible to declare default values of properties.

.. code-block:: python
    :linenos:

    from confident import Confident


    class MyConfig(Confident):
        port: int = 3333

    config = MyConfig()

    print(config)
    #> port=3333


Load Config Files
-----------------
Confident supports `json`, `yaml` and `.env` files.

**app_config/config1.json**

.. code-block:: console

    {
      "title": "my_app_1",
      "retry": true,
      "timeout": 10
    }


**app_config/config2.yaml**

.. code-block:: console

    title: my_yaml_app
    port: 3030


.. code-block:: python
    :linenos:

    from confident import Confident


    class MyConfig(Confident):
        title: str
        port: int = 5000
        retry: bool = False

    config = MyConfig(files=['app_config/config1.json', 'app_config/config2.yaml'])

    print(config)
    #> title='my_app_1' port=3030 retry=True
