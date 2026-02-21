import json
import os
from pathlib import Path
from typing import Optional
from unittest.mock import patch, Mock, PropertyMock

import pytest

from confident import BaseConfig, ConfigSource
from confident.loaders.source_loader_base import SourceLoader
from confident.utils import get_class_file_path
from tests.conftest import validate_file_not_exists, SPECS_FILE_1_SOURCE_PRIORITY


def test__load_explicit_fields(create_config_class1, sample_1):
    # Act
    config = create_config_class1(**sample_1)

    # Assert
    assert config.model_dump() == sample_1


def test__load_env_fields(create_config_class1, sample_1):
    # Arrange
    os.environ.update({k: str(v) for k, v in sample_1.items()})

    # Act
    config = create_config_class1()

    # Assert
    assert config.model_dump() == sample_1

    # Clean
    for field in sample_1.keys():
        del os.environ[field]


def test__load_string_json_env_fields():
    """
    Tests that the right conversion is made if string env var is loaded and the matching field is declared as a
    non string type but json supported (array, object, null, int, boolean).
    """
    # Arrange
    fields = {
        "my_env_a": 1,
        "my_env_b": True,
        "my_env_c": None,
        "my_env_d": ["a", "b"],
        "my_env_e": {"a": 1},
    }
    os.environ.update({key: json.dumps(value) for key, value in fields.items()})

    class MyConfig(BaseConfig):
        my_env_a: int
        my_env_b: bool
        my_env_c: Optional[dict]
        my_env_d: list
        my_env_e: dict

    # Act
    config = MyConfig()

    # Assert
    assert config.model_dump() == fields

    # Clean
    for field in fields.keys():
        del os.environ[field]


def test__load_fields_from_json_file(
    json_config_file_path_1, create_config_class1, sample_1
):
    # Arrange
    file_name = json_config_file_path_1

    # Act
    config = create_config_class1(_files=file_name)

    # Assert
    assert config.model_dump() == sample_1


def test__load_fields_from_yaml_file(
    yaml_config_file_path_2, create_config_class3, sample_2
):
    # Arrange
    file_name = yaml_config_file_path_2

    # Act
    config = create_config_class3(_files=file_name)

    # Assert
    assert config.model_dump() == sample_2


def test__load_fields_from_yml_file(
    yml_config_file_path_6, create_config_class3, sample_2
):
    # Arrange
    file_name = yml_config_file_path_6

    # Act
    config = create_config_class3(_files=file_name)

    # Assert
    assert config.model_dump() == sample_2


def test__load_fields_from_json_file__not_dict_content(
    json_config_file_path_3, create_config_class1
):
    # Arrange
    file_name = json_config_file_path_3

    # Act
    with pytest.raises(ValueError) as error:
        create_config_class1(_files=file_name)

    # Assert
    assert "has to have a valid dict content." in str(error.value)


def test__load_fields_from_yaml_file__empty_content(empty_config_file_path_4):
    # Arrange
    file_name = empty_config_file_path_4

    # Act
    class MyConfig(BaseConfig):
        name: str = "my_name"

    config = MyConfig(_files=file_name)

    # Assert
    assert config.all_loaded_fields().get(ConfigSource.file) == {}


def test__load_default_fields(create_config_class1_with_default_fields, sample_1):
    # Act
    config = create_config_class1_with_default_fields()

    # Assert
    assert config.model_dump() == sample_1


def test__load_fields_from_not_existing_file__ignore_missing_files_False(
    create_config_class1, sample_1
):
    # Arrange
    not_exists_file_name = "not_exists.json"
    validate_file_not_exists(file_name=not_exists_file_name)

    # Act & Assert
    with pytest.raises(ValueError) as error:
        create_config_class1(_files=not_exists_file_name, _ignore_missing_files=False)
    assert "is not exists." in str(error.value)
    assert not_exists_file_name in str(error.value)


def test__load_fields_from_not_existing_file__ignore_missing_files_True(
    json_config_file_path_1, create_config_class1, sample_1
):
    # Arrange
    not_exists_file_name = "not_exists.json"
    validate_file_not_exists(file_name=not_exists_file_name)

    # Act
    config = create_config_class1(
        _files=[not_exists_file_name, json_config_file_path_1],
        _ignore_missing_files=True,
    )

    # Assert
    assert config.model_dump() == sample_1


def test__try_load_file_with_unsupported_suffix(
    no_suffix_config_file_path_5, create_config_class1
):
    # Act & Assert
    with pytest.raises(ValueError) as error:
        create_config_class1(_files=no_suffix_config_file_path_5)
    assert "is not a supported file." in str(error.value)
    assert no_suffix_config_file_path_5 in str(error.value)


def test__loader_base_has_to_be_implemented():
    class MyLoader(SourceLoader):
        pass

    with pytest.raises(TypeError) as error:
        loader = MyLoader()
        loader.load_fields(Mock())
    assert "Can't instantiate abstract class MyLoader" in str(error.value)


def test__load_specs_path(specs_file_path_1, create_config_class1, sample_1):
    # Act
    config = create_config_class1(**sample_1, _specs_path=specs_file_path_1)

    # Assert
    assert config.specs() == config.__specs__ == config._specs
    assert (
        config.source_priority()
        == config.specs().source_priority
        == SPECS_FILE_1_SOURCE_PRIORITY
    )
    assert config.specs().specs_path == Path(specs_file_path_1)
    assert config.model_dump() == sample_1


@patch("importlib.import_module")
@pytest.mark.parametrize("exception", [ImportError, AttributeError])  # type: ignore[list-item]
def test__get_class_file_path__no_module_file(import_module_patch, exception):
    # Arrange
    type(import_module_patch.return_value).__file__ = PropertyMock(
        side_effect=exception()
    )
    # Act
    cls_path = get_class_file_path(Mock())
    # Assert
    assert cls_path == Path.cwd()


def test__validate_file_not_exists(json_config_file_path_1):
    """
    Test that the tool to check the file is not exists before the test starts is working properly.
    """
    # Arrange
    exists_path = json_config_file_path_1

    # Act & Assert
    with pytest.raises(FileExistsError) as error:
        validate_file_not_exists(exists_path)
    assert f"File {exists_path} should not exists while tests run." in str(error.value)
