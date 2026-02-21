import json
import os
from typing import Any, Dict, Generator, Type

import yaml
from confident import BaseConfig, ConfigSource
from pydantic import create_model
from pytest import fixture

# Clear the environment variables:
os.environ.clear()

# Test files names:
# Config files:
SAMPLE_1_FILE_NAME = "temp_conf1.json"
SAMPLE_2_FILE_NAME = "temp_conf2.yaml"
SAMPLE_3_FILE_NAME = "temp_conf3.json"
SAMPLE_4_FILE_NAME = "temp_conf4.yaml"
SAMPLE_6_FILE_NAME = "temp_conf6.yml"
# Env files:
SAMPLE_1_ENV_FILE_NAME = "temp_conf1.env"
# Spec files:
SPECS_1_FILE_NAME = "temp_specs1.json"
# Map config files:
CONFIG_MAP_SAMPLE_1_FILE_NAME = "temp_config_map.json"

# Test field names:
SAMPLE_1_FIELD_1 = "title"
SAMPLE_1_FIELD_2 = "host"
SAMPLE_1_FIELD_3 = "port"

SAMPLE_2_FIELD_1 = "db_title"
SAMPLE_2_FIELD_2 = "db_host"
SAMPLE_2_FIELD_3 = "db_port"

SAMPLE_3_FIELD_1 = "user_name"
SAMPLE_3_FIELD_2 = "secret_id"

SAMPLE_4_FIELD_1 = "host"
SAMPLE_4_FIELD_2 = "port"


def validate_file_not_exists(file_name: str) -> None:
    if os.path.exists(file_name):
        raise FileExistsError(f"File {file_name} should not exists while tests run.")


def generate_temporary_file(
    file_name: str, data: Any, file_format: str = "json"
) -> Generator[str, None, None]:
    validate_file_not_exists(file_name=file_name)

    with open(file_name, "w") as file:
        if file_format == "yaml":
            yaml.safe_dump(data, file)
        elif file_format == "text":
            file.write(data)
        else:
            json.dump(data, file)

    yield file_name

    os.remove(file_name)


# Test fields and values:
@fixture
def sample_1():
    return {
        SAMPLE_1_FIELD_1: "my_app_1",
        SAMPLE_1_FIELD_2: "127.0.0.1",
        SAMPLE_1_FIELD_3: 5001,
    }


@fixture
def sample_2():
    return {
        SAMPLE_3_FIELD_1: "lemonade",
        SAMPLE_3_FIELD_2: "6",
    }


@fixture
def sample_4():
    return {
        SAMPLE_4_FIELD_1: "1.1.1.1",
        SAMPLE_4_FIELD_2: "8080",
    }


@fixture
def sample_5():
    return {
        SAMPLE_4_FIELD_1: "127.0.0.1",
        SAMPLE_4_FIELD_2: "5000",
    }


# Temporary test files:
@fixture
def json_config_file_path_1(sample_1) -> Generator[str, None, None]:
    yield from generate_temporary_file(data=sample_1, file_name=SAMPLE_1_FILE_NAME)


@fixture
def yaml_config_file_path_2(sample_2) -> Generator[str, None, None]:
    yield from generate_temporary_file(
        file_name=SAMPLE_2_FILE_NAME, data=sample_2, file_format="yaml"
    )


@fixture
def json_config_file_path_3() -> Generator[str, None, None]:
    yield from generate_temporary_file(data="some_string", file_name=SAMPLE_3_FILE_NAME)


@fixture
def empty_config_file_path_4() -> Generator[str, None, None]:
    yield from generate_temporary_file(
        file_name=SAMPLE_4_FILE_NAME, data="", file_format="text"
    )


@fixture
def yml_config_file_path_6(sample_2) -> Generator[str, None, None]:
    yield from generate_temporary_file(
        file_name=SAMPLE_6_FILE_NAME, data=sample_2, file_format="yaml"
    )


@fixture
def no_suffix_config_file_path_5(sample_1) -> Generator[str, None, None]:
    yield from generate_temporary_file(data=sample_1, file_name="no_suffix_file")


SPECS_FILE_1_SOURCE_PRIORITY = [ConfigSource.init]


@fixture
def specs_file_path_1(sample_1) -> Generator[str, None, None]:
    yield from generate_temporary_file(
        file_name=SPECS_1_FILE_NAME,
        data={"source_priority": SPECS_FILE_1_SOURCE_PRIORITY},
    )


# Test config maps:
CONFIG_SAMPLE_1_FIELD_1 = "prod"
CONFIG_SAMPLE_1_FIELD_2 = "dev"

MAP_FIELD_1 = "environment"


@fixture
def config_map_samples_4_5(sample_4, sample_5) -> Dict[str, Any]:
    return {
        CONFIG_SAMPLE_1_FIELD_1: sample_4,
        CONFIG_SAMPLE_1_FIELD_2: sample_5,
    }


@fixture
def sample_4_with_map_field(sample_4) -> Dict[str, Any]:
    return {MAP_FIELD_1: CONFIG_SAMPLE_1_FIELD_1, **sample_4}


@fixture
def json_config_map_file_path_4_5(config_map_samples_4_5) -> Generator[str, None, None]:
    yield from generate_temporary_file(
        file_name=CONFIG_MAP_SAMPLE_1_FILE_NAME, data=config_map_samples_4_5
    )


# Test input BaseModels:
@fixture
def create_config_class1(sample_1) -> Type[BaseConfig]:
    return create_model(  # type: ignore[call-overload, no-any-return]
        "ConfigClass1",
        __base__=BaseConfig,
        **{key: (type(value), ...) for key, value in sample_1.items()},
    )


@fixture
def create_config_class1_with_default_fields(sample_1) -> Type[BaseConfig]:
    return create_model(  # type: ignore[call-overload, no-any-return]
        "ConfigClassWithDefaults1",
        __base__=BaseConfig,
        **{key: (type(value), value) for key, value in sample_1.items()},
    )


@fixture
def create_config_class3(sample_2) -> Type[BaseConfig]:
    return create_model(  # type: ignore[call-overload, no-any-return]
        "ConfigClass3",
        __base__=BaseConfig,
        **{key: (type(value), ...) for key, value in sample_2.items()},
    )


@fixture
def create_config_class4(sample_4) -> Type[BaseConfig]:
    return create_model(  # type: ignore[call-overload, no-any-return]
        "ConfigClass4",
        __base__=BaseConfig,
        **{key: (type(value), ...) for key, value in sample_4.items()},
    )


@fixture
def create_config_class4_with_map_field(sample_4_with_map_field) -> Type[BaseConfig]:
    return create_model(  # type: ignore[call-overload, no-any-return]
        "ConfigClass4",
        __base__=BaseConfig,
        **{key: (type(value), ...) for key, value in sample_4_with_map_field.items()},
    )
