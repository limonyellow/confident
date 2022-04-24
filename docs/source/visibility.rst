.. _visibility:

Visibility
==========
Confident provides built-in functions to show details about the object after creation.
The details can be logged/printed and provide clarity about the source of every value in the object.

Multiple Sources Recognition
----------------------------

In order to monitor which fields were loaded from what source, `full_details()` can be used.
Notice the difference between the source types:

.. code-block:: python
    :linenos:

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


Confident Object Creation location
----------------------------------
The position of the the `Confident` object declaration:

.. code-block:: python

    config.specs().class_path
    #> PosixPath('~/MyProject/project_config.py')


The position of the the `Confident` object instance creation:

.. code-block:: python

    config.specs().creation_path
    #> PosixPath('~/MyProject/main.py')
