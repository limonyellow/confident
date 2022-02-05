import json
import os
from typing import Optional

import pytest

from confident import Confident
from tests.conftest import validate_file_not_exists


def test__load_explicit_fields(create_config_class1, sample_1):
    # Act
    config = create_config_class1(fields=sample_1)

    # Assert
    assert config.dict() == sample_1


def test__load_env_fields(create_config_class1, sample_1):
    # Arrange
    os.environ.update(sample_1)

    # Act
    config = create_config_class1()

    # Assert
    assert config.dict() == sample_1

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
        'my_env_a': 1,
        'my_env_b': True,
        'my_env_c': None,
        'my_env_d': ['a', 'b'],
        'my_env_e': {'a': 1},
    }
    os.environ.update({key: json.dumps(value) for key, value in fields.items()})

    class Config(Confident):
        my_env_a: int
        my_env_b: bool
        my_env_c: Optional[dict]
        my_env_d: list
        my_env_e: dict

    # Act
    config = Config()

    # Assert
    assert config.dict() == fields

    # Clean
    for field in fields.keys():
        del os.environ[field]


def test__load_fields_from_json_file(json_config_file_path_1, create_config_class1, sample_1):
    # Arrange
    file_name = json_config_file_path_1

    # Act
    config = create_config_class1(files=file_name)

    # Assert
    assert config.dict() == sample_1


def test__load_fields_from_yaml_file(yaml_config_file_path_3, create_config_class3, sample_3):
    # Arrange
    file_name = yaml_config_file_path_3

    # Act
    config = create_config_class3(files=file_name)

    # Assert
    assert config.dict() == sample_3


def test__load_fields_from_env_file(env_config_file_path_1, create_config_class1, sample_1):
    # Arrange
    file_name = env_config_file_path_1

    # Act
    config = create_config_class1(env_files=file_name)

    # Assert
    assert config.dict() == sample_1

    # Clean the env vars from the environment
    for field in sample_1.keys():
        del os.environ[field]


def test__load_default_fields(create_config_class1_with_default_fields, sample_1):
    # Act
    config = create_config_class1_with_default_fields()

    # Assert
    assert config.dict() == sample_1


def test__load_fields_from_not_existing_file__ignore_missing_files_False(create_config_class1, sample_1):
    # Arrange
    not_exists_file_name = 'not_exists.json'
    validate_file_not_exists(file_name=not_exists_file_name)

    # Act & Assert
    with pytest.raises(ValueError):
        create_config_class1(files=not_exists_file_name, ignore_missing_files=False)


def test__load_fields_from_not_existing_file__ignore_missing_files_True(
        json_config_file_path_1, create_config_class1, sample_1
):
    # Arrange
    not_exists_file_name = 'not_exists.json'
    validate_file_not_exists(file_name=not_exists_file_name)

    # Act
    config = create_config_class1(files=[not_exists_file_name, json_config_file_path_1], ignore_missing_files=True)

    # Assert
    assert config.dict() == sample_1


def test__load_specs_path(specs_file_path_1, create_config_class1, sample_1):
    # Act
    config = create_config_class1(specs_path=specs_file_path_1)

    # Assert
    assert config.dict() == sample_1
