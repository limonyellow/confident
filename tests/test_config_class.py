from confident import BaseConfig, ConfidentConfigDict
from confident.config_source import ConfigSource
from tests.conftest import CONFIG_MAP_SAMPLE_1_FILE_NAME, CONFIG_SAMPLE_1_FIELD_1


def test__config_class_loading__files():
    """
    Checks if file specs properties are inserted correctly from a `ConfidentConfig` class declaration.
    Doesn't check the logic - this is done in `test_confident.py`.
    """

    # Arrange:
    class MyConfig(BaseConfig):
        model_config = ConfidentConfigDict(
            files="temp.json",
            ignore_missing_files=True,
            source_priority=[ConfigSource.init],
        )
        property_a: str = "nothing"

    # Act
    config = MyConfig()

    # Assert
    specs = config.specs()
    # `env_files` and `files` are inserted into a list as Path objects.
    assert str(specs.files.pop()) == "temp.json"
    assert specs.ignore_missing_files is True
    assert specs.source_priority == [ConfigSource.init]


def test__config_class_loading__map_name(json_config_map_file_path_4_5):
    """
    Checks if file specs properties are inserted correctly from a `ConfidentConfig` class declaration.
    Doesn't check the logic - this is done in `test_confident.py`.
    """

    # Arrange:
    class MyConfig(BaseConfig):
        model_config = ConfidentConfigDict(
            config_map="temp_config_map.json",
            map_name="prod",
        )
        property_a: str = "nothing"
        host: str
        port: str

    # Act
    config = MyConfig()

    # Assert
    specs = config.specs()
    # Also check that the values matches the test input from conftest.py.
    assert (
        str(specs.config_map) == "temp_config_map.json" == CONFIG_MAP_SAMPLE_1_FILE_NAME
    )
    assert specs.map_name == "prod" == CONFIG_SAMPLE_1_FIELD_1


def test__config_class_loading__map_field(json_config_map_file_path_4_5):
    """
    Checks if file specs properties are inserted correctly from a `ConfidentConfig` class declaration.
    Doesn't check the logic - this is done in `test_confident.py`.
    """

    # Arrange:
    class MyConfig(BaseConfig):
        model_config = ConfidentConfigDict(
            config_map="temp_config_map.json",
            map_field="property_a",
        )
        property_a: str = "prod"
        host: str
        port: str

    # Act
    config = MyConfig()

    # Assert
    specs = config.specs()
    # Also check that the values matches the test input from conftest.py.
    assert (
        str(specs.config_map) == "temp_config_map.json" == CONFIG_MAP_SAMPLE_1_FILE_NAME
    )
    assert specs.map_field == "property_a"


def test__config_source_string_representation():
    assert ConfigSource.init.__repr__() == "'" + str(ConfigSource.init) + "'"
