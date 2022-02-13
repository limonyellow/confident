import os
from unittest.mock import patch

import pytest
from _pytest.fixtures import fixture
from pydantic import create_model

from confident import Confident
from confident.config_source import ConfigSource
from tests.conftest import generate_temporary_file

EXPLICIT_A = {
    'ex_field': 'ex'
}
ENV_VARS_A = {
    'ex_field': 'env',
    'env_field': 'env'
}
DEPLOYMENT_NAME = 'default_deploy'
DEPLOYMENT_CONFIG_A = {
    DEPLOYMENT_NAME: {
        'ex_field': 'deploy',
        'env_field': 'deploy',
        'deploy_field': 'deploy'
    }
}
CONFIG_FILE_A_NAME = 'test.json'
CONFIG_FILE_A = {
    'ex_field': 'file',
    'env_field': 'file',
    'deploy_field': 'file',
    'file_field': 'file'
}
DEFAULT_VALUES_A = {
    'ex_field': 'default',
    'env_field': 'default',
    'deploy_field': 'default',
    'file_field': 'default',
    'default_field': 'default'
}
SOURCE_PRIORITY_A = [
    ConfigSource.explicit, ConfigSource.env_var, ConfigSource.deployment, ConfigSource.file, ConfigSource.class_default
]
RESULT_FIELDS_A = {
    'ex_field': 'ex',
    'env_field': 'env',
    'deploy_field': 'deploy',
    'file_field': 'file',
    'default_field': 'default'
}
SOURCE_PRIORITY_B = [
    ConfigSource.deployment, ConfigSource.explicit, ConfigSource.env_var, ConfigSource.file, ConfigSource.class_default
]
RESULT_FIELDS_B = {
    'ex_field': 'deploy',
    'env_field': 'deploy',
    'deploy_field': 'deploy',
    'file_field': 'file',
    'default_field': 'default'
}
SOURCE_PRIORITY_C = [ConfigSource.file]
RESULT_FIELDS_C = {
    'ex_field': 'file',
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
        source_priority=source_priority, fields=EXPLICIT_A, deployment_name=DEPLOYMENT_NAME,
        deployment_config=DEPLOYMENT_CONFIG_A, files=json_config_file_path
    )

    assert config.dict() == expected_fields
