import json
import os

import yaml
from confident import Confident
from pydantic import create_model
from pytest import fixture

# Clear the environment variables:
os.environ = {}

# Test files:
SAMPLE_1_FILE_NAME = 'temp_conf1.json'
SAMPLE_2_FILE_NAME = 'temp_conf2.json'
SAMPLE_3_FILE_NAME = 'temp_conf3.yaml'

# Test field names:
SAMPLE_1_FIELD_1 = 'title'
SAMPLE_1_FIELD_2 = 'host'
SAMPLE_1_FIELD_3 = 'port'

SAMPLE_2_FIELD_1 = 'db_title'
SAMPLE_2_FIELD_2 = 'db_host'
SAMPLE_2_FIELD_3 = 'db_port'

SAMPLE_3_FIELD_1 = 'user_name'
SAMPLE_3_FIELD_2 = 'secret_id'

ConfigClass2 = create_model('ConfigClass2', **{
    SAMPLE_1_FIELD_1: (str, ...),
    SAMPLE_1_FIELD_2: (str, ...),
    SAMPLE_1_FIELD_3: (int, ...),
    SAMPLE_2_FIELD_1: (str, ...),
    SAMPLE_2_FIELD_2: (str, ...),
    SAMPLE_2_FIELD_3: (int, ...),
})


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
        SAMPLE_3_FIELD_1: 'splinter',
        SAMPLE_3_FIELD_2: '6',
    }


@fixture
def json_config_file_path_1(sample_1) -> str:
    data = sample_1
    file_name = SAMPLE_1_FILE_NAME
    if os.path.exists(file_name):
        raise FileExistsError(f'File {file_name} should not exists while tests run.')

    with open(file_name, 'w') as file:
        json.dump(data, file)

    yield file_name

    os.remove(file_name)


@fixture
def json_config_file_path_2(sample_2) -> str:
    data = sample_2
    file_name = SAMPLE_2_FILE_NAME
    if os.path.exists(file_name):
        raise FileExistsError(f'File {file_name} should not exists while tests run.')

    with open(file_name, 'w') as file:
        json.dump(data, file)

    yield file_name

    os.remove(file_name)


@fixture
def yaml_config_file_path_3(sample_3) -> str:
    data = sample_3
    file_name = SAMPLE_3_FILE_NAME
    if os.path.exists(file_name):
        raise FileExistsError(f'File {file_name} should not exists while tests run.')

    with open(file_name, 'w') as file:
        yaml.safe_dump(data, file)

    yield file_name

    os.remove(file_name)


# Test input BaseModels:
@fixture
def ConfigClass1(sample_1):
    return create_model('ConfigClass1', __base__=Confident,
                        **{key: (type(value), ...) for key, value in sample_1.items()})


@fixture
def ConfigClass3(sample_3):
    return create_model('ConfigClass3', __base__=Confident,
                        **{key: (type(value), ...) for key, value in sample_3.items()})
