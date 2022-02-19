from confident import Confident
from confident.config_source import ConfigSource
from tests.conftest import DEPLOYMENT_CONFIG_SAMPLE_1_FILE_NAME, DEPLOY_CONFIG_SAMPLE_1_FIELD_1


def test__config_class_loading__files():
    """
    Checks if file specs properties are inserted correctly from a `ConfidentConfig` class declaration.
    Doesn't check the logic - this is done in `test_confident.py`.
    """
    # Arrange:
    class MyConfig(Confident):
        property_a: str = 'nothing'

        class ConfidentConfig:
            env_files = 'temp.env'
            files = 'temp.json'
            prefer_files = True
            ignore_missing_files = True
            source_priority = [ConfigSource.explicit]

    # Act
    config = MyConfig()

    # Assert
    specs = config.specs()
    # `env_files` and `files` are inserted into a list as Path objects.
    assert str(specs.env_files.pop()) == 'temp.env'
    assert str(specs.files.pop()) == 'temp.json'
    assert specs.prefer_files is True
    assert specs.ignore_missing_files is True
    assert specs.source_priority == [ConfigSource.explicit]


def test__config_class_loading__deployment_name(json_deployment_config_file_path_4_5):
    """
    Checks if file specs properties are inserted correctly from a `ConfidentConfig` class declaration.
    Doesn't check the logic - this is done in `test_confident.py`.
    """
    # Arrange:
    class MyConfig(Confident):
        property_a: str = 'nothing'

        class ConfidentConfig:
            deployment_config = 'temp_deployment_config.json'
            deployment_name = 'prod'

    # Act
    config = MyConfig()

    # Assert
    specs = config.specs()
    # Also check that the values matches the test input from conftest.py.
    assert str(specs.deployment_config) == 'temp_deployment_config.json' == DEPLOYMENT_CONFIG_SAMPLE_1_FILE_NAME
    assert specs.deployment_name == 'prod' == DEPLOY_CONFIG_SAMPLE_1_FIELD_1


def test__config_class_loading__deployment_field(json_deployment_config_file_path_4_5):
    """
    Checks if file specs properties are inserted correctly from a `ConfidentConfig` class declaration.
    Doesn't check the logic - this is done in `test_confident.py`.
    """
    # Arrange:
    class MyConfig(Confident):
        property_a: str = 'prod'

        class ConfidentConfig:
            deployment_config = 'temp_deployment_config.json'
            deployment_field = 'property_a'

    # Act
    config = MyConfig()

    # Assert
    specs = config.specs()
    # Also check that the values matches the test input from conftest.py.
    assert str(specs.deployment_config) == 'temp_deployment_config.json' == DEPLOYMENT_CONFIG_SAMPLE_1_FILE_NAME
    assert specs.deployment_field == 'property_a'
