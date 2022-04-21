.. _usage:

Basic Usage
===========

.. _installation:

Installation
------------

Install using pip:

.. code-block:: console

   (.venv) $ pip install confident

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

.. note::
    The docs are still under construction.



