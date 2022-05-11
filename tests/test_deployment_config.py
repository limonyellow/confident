import pytest

from confident import Confident, MapField
from tests.conftest import DEPLOY_CONFIG_SAMPLE_1_FIELD_1, DEPLOY_FIELD_1, SAMPLE_4_FIELD_1


def test__load_deployment_config__deploy_name(create_config_class4, json_deployment_config_file_path_4_5, sample_4):
    """
    Test with explicit `_map_name`.
    """
    # Act
    config = create_config_class4(
        _map_name=DEPLOY_CONFIG_SAMPLE_1_FIELD_1, _config_map=json_deployment_config_file_path_4_5
    )

    # Assert
    assert config.dict() == sample_4


def test__load_deployment_config__deploy_field(
        create_config_class4_with_deployment_field, json_deployment_config_file_path_4_5, sample_4_with_deployment_field
):
    """
    Test with explicit `_map_name`.
    """
    # Act
    config = create_config_class4_with_deployment_field(
        **{DEPLOY_FIELD_1: DEPLOY_CONFIG_SAMPLE_1_FIELD_1}, _map_field=DEPLOY_FIELD_1,
        _config_map=json_deployment_config_file_path_4_5
    )

    # Assert
    assert config.dict() == sample_4_with_deployment_field


def test__load_deployment_config_dict__deploy_field(create_config_class4, deployment_config_samples_4_5, sample_4):
    """
    Test with explicit `_map_name` and deployment_config as dictionary.
    """
    # Act
    config = create_config_class4(
        _map_name=DEPLOY_CONFIG_SAMPLE_1_FIELD_1, _config_map=deployment_config_samples_4_5
    )

    # Assert
    assert config.dict() == sample_4


def test__load_deployment_config__2_deploy_fields_a():
    """
    Test that map field is not explicit and declared by `MapField` at the same time.
    """
    # Arrange
    class ConfigA(Confident):
        env_a: str = 'nothing'
        env_b: str = MapField('nothing')

    class ConfigB(Confident):
        env_a: str = MapField('nothing')

    # Act & Assert
    with pytest.raises(ValueError):
        ConfigA(_map_field='env_a', _config_map={})

    with pytest.raises(ValueError):
        ConfigB(_map_field='env_a', _config_map={})


def test__load_deployment_config__2_deploy_fields_b():
    """
    Test that map field is not declared by `MapField` and in `ConfidentConfig` class at the same time.
    """
    # Arrange
    class Config(Confident):
        env_a: str = MapField('nothing')

        class ConfidentConfig:
            _map_field = 'env_a'

    # Act & Assert
    with pytest.raises(ValueError):
        Config(_config_map={})


def test__load_deployment_config__2_deploy_fields_c():
    """
    Test that map field is not declared by `MapField` more than one.
    """
    # Arrange
    class Config(Confident):
        env_a: str = MapField('nothing')
        env_b: str = MapField('nothing')

    # Act & Assert
    with pytest.raises(ValueError):
        Config(_config_map={})


def test__load_deployment_config__deploy_field_and_deploy_name():
    """
    Test that map field and map name are not used at the same time.
    """
    # Arrange
    class Config(Confident):
        env_a: str = 'nothing'

    # Act & Assert
    with pytest.raises(ValueError):
        Config(_map_field='env_a', _map_name='thing', _config_map={})


@pytest.mark.parametrize('map_field, map_name', [('env_a', None), (None, 'nothing')])
def test__load_deployment_config__no_deploy_config(map_field, map_name):
    """
    Test that deployment config is inserted if deployment field or name is used.
    Case 1 - Only `map_field` is provided.
    Case 2 - Only `map_name` is provided.
    """
    # Arrange
    class Config(Confident):
        env_a: str = 'nothing'

    # Act & Assert
    with pytest.raises(ValueError):
        Config(_map_field=map_field, _map_name=map_name)


@pytest.mark.parametrize('map_name', [True, 7])
def test__load_deployment_config__deploy_name_is_not_valid(map_name):
    """
    Test that deployment name is a string.
    Case 1 - The `map_name` is type `bool`.
    Case 2 - The `map_name` is type `int`.
    """
    # Arrange
    config_map = {
        True: {
            "title": "a"
        },
        7: {
            "title": "b"
        }
    }

    class Config(Confident):
        env_a: str = map_name
        title: str

    # Act & Assert
    with pytest.raises(ValueError):
        Config(_map_field='env_a', _config_map=config_map)


def test__load_deployment_config__deploy_field_also_inside_deploy_config(
        create_config_class4, deployment_config_samples_4_5, sample_4
):
    """
    Test that the `map_field` is not appear in the 'config_map'.
    The `map_field` has to be decided before loading the `config_map` and cannot be change according
    to the map config.
    For example, `env` field (the map field) cannot appear in 'prod' config:
    ```
    Class Config(Confident):
        env: str = MapField('prod')  # <- declaring the map field and its default value.
        host: str

    deploy_config = {
        'prod': {
            env: 'dev'  # <- Redefining the map field.
            host: '0.0.0.0'
        }
        'dev': {
            host: '0.0.0.0'
        }
    }

    Config(_config_map=deploy_config)  # Will raise `ValueError`. Otherwise, 'prod' config will be chosen
                                             # but will be changed to value 'dev'.
    ```
    """
    # Act & Assert
    with pytest.raises(ValueError) as error:
        create_config_class4(
            **{SAMPLE_4_FIELD_1: DEPLOY_CONFIG_SAMPLE_1_FIELD_1},
            _map_field=SAMPLE_4_FIELD_1,
            _config_map=deployment_config_samples_4_5
        )
    assert '''map_field='host' cannot appear in the map config key 'prod'.''' in str(error.value)
