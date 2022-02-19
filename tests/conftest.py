import json
import os
from typing import Any, Dict, Type

import yaml
from confident import Confident
from pydantic import create_model
from pytest import fixture

# Clear the environment variables:
os.environ = {}

# Test files names:
# Config files:
SAMPLE_1_FILE_NAME = 'temp_conf1.json'
SAMPLE_2_FILE_NAME = 'temp_conf2.json'
SAMPLE_3_FILE_NAME = 'temp_conf3.yaml'
# Env files:
SAMPLE_1_ENV_FILE_NAME = 'temp_conf1.env'
# Spec files:
SPECS_1_FILE_NAME = 'temp_specs1.json'
# Deployment config files:
DEPLOYMENT_CONFIG_SAMPLE_1_FILE_NAME = 'temp_deployment_config.json'

# Test field names:
SAMPLE_1_FIELD_1 = 'title'
SAMPLE_1_FIELD_2 = 'host'
SAMPLE_1_FIELD_3 = 'port'

SAMPLE_2_FIELD_1 = 'db_title'
SAMPLE_2_FIELD_2 = 'db_host'
SAMPLE_2_FIELD_3 = 'db_port'

SAMPLE_3_FIELD_1 = 'user_name'
SAMPLE_3_FIELD_2 = 'secret_id'

SAMPLE_4_FIELD_1 = 'host'
SAMPLE_4_FIELD_2 = 'port'


def validate_file_not_exists(file_name: str) -> None:
    if os.path.exists(file_name):
        raise FileExistsError(f'File {file_name} should not exists while tests run.')


def generate_temporary_file(file_name: str, data: dict, file_format: str = 'json') -> str:
    validate_file_not_exists(file_name=file_name)

    with open(file_name, 'w') as file:
        if file_format == 'yaml':
            yaml.safe_dump(data, file)
        else:
            json.dump(data, file)

    yield file_name

    os.remove(file_name)


# Test fields and values:
@fixture
def sample_1():
    return {
        SAMPLE_1_FIELD_1: 'my_app_1',
        SAMPLE_1_FIELD_2: '127.0.0.1',
        SAMPLE_1_FIELD_3: 5001,
    }


@fixture
def sample_2():
    return {
        SAMPLE_2_FIELD_1: 'db_sample_2',
        SAMPLE_2_FIELD_2: '127.0.0.1',
        SAMPLE_2_FIELD_3: 5002,
    }


@fixture
def sample_3():
    return {
        SAMPLE_3_FIELD_1: 'lemonade',
        SAMPLE_3_FIELD_2: '6',
    }


@fixture
def sample_4():
    return {
        SAMPLE_4_FIELD_1: '1.1.1.1',
        SAMPLE_4_FIELD_2: '8080',
    }


@fixture
def sample_5():
    return {
        SAMPLE_4_FIELD_1: '127.0.0.1',
        SAMPLE_4_FIELD_2: '5000',
    }


# Temporary test files:
@fixture
def json_config_file_path_1(sample_1) -> str:
    yield from generate_temporary_file(data=sample_1, file_name=SAMPLE_1_FILE_NAME)


@fixture
def json_config_file_path_2(sample_2) -> str:
    yield from generate_temporary_file(data=sample_2, file_name=SAMPLE_2_FILE_NAME)


@fixture
def yaml_config_file_path_3(sample_3) -> str:
    yield from generate_temporary_file(file_name=SAMPLE_3_FILE_NAME, data=sample_3, file_format='yaml')


@fixture
def env_config_file_path_1(sample_1) -> str:
    data = sample_1
    file_name = SAMPLE_1_ENV_FILE_NAME
    validate_file_not_exists(file_name=file_name)

    with open(file_name, 'w') as file:
        file.writelines([f'{key}={value}\n' for key, value in data.items()])

    yield file_name

    os.remove(file_name)


@fixture
def specs_file_path_1(sample_1) -> str:
    yield from generate_temporary_file(file_name=SPECS_1_FILE_NAME, data={'explicit_fields': sample_1})


# Test deployment configs:
DEPLOY_CONFIG_SAMPLE_1_FIELD_1 = 'prod'
DEPLOY_CONFIG_SAMPLE_1_FIELD_2 = 'dev'

DEPLOY_FIELD_1 = 'environment'


@fixture
def deployment_config_samples_4_5(sample_4, sample_5) -> Dict[str, Any]:
    return {
        DEPLOY_CONFIG_SAMPLE_1_FIELD_1: sample_4,
        DEPLOY_CONFIG_SAMPLE_1_FIELD_2: sample_5,
    }


@fixture
def sample_4_with_deployment_field(sample_4) -> Dict[str, Any]:
    return {
        DEPLOY_FIELD_1: DEPLOY_CONFIG_SAMPLE_1_FIELD_1,
        **sample_4
    }


@fixture
def json_deployment_config_file_path_4_5(deployment_config_samples_4_5) -> str:
    yield from generate_temporary_file(
        file_name=DEPLOYMENT_CONFIG_SAMPLE_1_FILE_NAME, data=deployment_config_samples_4_5
    )


# Test input BaseModels:
@fixture
def create_config_class1(sample_1) -> Type[Confident]:
    return create_model(
        'ConfigClass1', __base__=Confident,
        **{key: (type(value), ...) for key, value in sample_1.items()}
    )


@fixture
def create_config_class1_with_default_fields(sample_1) -> Type[Confident]:
    return create_model(
        'ConfigClassWithDefaults1', __base__=Confident,
        **{key: (type(value), value) for key, value in sample_1.items()}
    )


@fixture
def create_config_class3(sample_3) -> Type[Confident]:
    return create_model(
        'ConfigClass3', __base__=Confident,
        **{key: (type(value), ...) for key, value in sample_3.items()}
    )


@fixture
def create_config_class4(sample_4) -> Type[Confident]:
    return create_model(
        'ConfigClass4', __base__=Confident,
        **{key: (type(value), ...) for key, value in sample_4.items()}
    )


@fixture
def create_config_class4_with_deployment_field(sample_4_with_deployment_field) -> Type[Confident]:
    return create_model(
        'ConfigClass4', __base__=Confident,
        **{key: (type(value), ...) for key, value in sample_4_with_deployment_field.items()}
    )
