import os
from unittest.mock import patch

import pytest
from _pytest.fixtures import fixture
from pydantic import create_model

from confident import Confident
from confident.config_source import ConfigSource
from tests.conftest import generate_temporary_file

INIT_A = {
    'init_field': 'init'
}
ENV_VARS_A = {
    'init_field': 'env',
    'env_field': 'env'
}
DEPLOYMENT_NAME = 'default_deploy'
DEPLOYMENT_CONFIG_A = {
    DEPLOYMENT_NAME: {
        'init_field': 'deploy',
        'env_field': 'deploy',
        'deploy_field': 'deploy'
    }
}
CONFIG_FILE_A_NAME = 'test.json'
CONFIG_FILE_A = {
    'init_field': 'file',
    'env_field': 'file',
    'deploy_field': 'file',
    'file_field': 'file'
}
DEFAULT_VALUES_A = {
    'init_field': 'default',
    'env_field': 'default',
    'deploy_field': 'default',
    'file_field': 'default',
    'default_field': 'default'
}
SOURCE_PRIORITY_A = [
    ConfigSource.init, ConfigSource.env_var, ConfigSource.map, ConfigSource.file, ConfigSource.class_default
]
RESULT_FIELDS_A = {
    'init_field': 'init',
    'env_field': 'env',
    'deploy_field': 'deploy',
    'file_field': 'file',
    'default_field': 'default'
}
SOURCE_PRIORITY_B = [
    ConfigSource.map, ConfigSource.init, ConfigSource.env_var, ConfigSource.file, ConfigSource.class_default
]
RESULT_FIELDS_B = {
    'init_field': 'deploy',
    'env_field': 'deploy',
    'deploy_field': 'deploy',
    'file_field': 'file',
    'default_field': 'default'
}
SOURCE_PRIORITY_C = [ConfigSource.file]
RESULT_FIELDS_C = {
    'init_field': 'file',
    'env_field': 'file',
    'deploy_field': 'file',
    'file_field': 'file',
    'default_field': 'default'
}


@fixture
def json_config_file_path() -> str:
    yield from generate_temporary_file(file_name=CONFIG_FILE_A_NAME, data=CONFIG_FILE_A)


@patch.dict(os.environ, ENV_VARS_A)
@pytest.mark.parametrize(
    "source_priority, expected_fields", [
        (SOURCE_PRIORITY_A, RESULT_FIELDS_A),
        (SOURCE_PRIORITY_B, RESULT_FIELDS_B),
        (SOURCE_PRIORITY_C, RESULT_FIELDS_C),
    ]
)
def test__priority_loading(source_priority, expected_fields, json_config_file_path):
    config_class = create_model(
        'ConfigClass1', __base__=Confident,
        **{key: (type(value), value) for key, value in DEFAULT_VALUES_A.items()}
    )
    config = config_class(
        **INIT_A, _source_priority=source_priority, _map_name=DEPLOYMENT_NAME,
        _config_map=DEPLOYMENT_CONFIG_A, _files=json_config_file_path
    )

    assert config.dict() == expected_fields
