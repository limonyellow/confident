import pytest

from confident import Confident, DeploymentField
from tests.conftest import DEPLOY_CONFIG_SAMPLE_1_FIELD_1, DEPLOY_FIELD_1, SAMPLE_4_FIELD_1


def test__load_deployment_config__deploy_name(create_config_class4, json_deployment_config_file_path_4_5, sample_4):
    """
    Test with explicit `deployment_name`.
    """
    # Act
    config = create_config_class4(
        deployment_name=DEPLOY_CONFIG_SAMPLE_1_FIELD_1, deployment_config=json_deployment_config_file_path_4_5
    )

    # Assert
    assert config.dict() == sample_4


def test__load_deployment_config__deploy_field(
        create_config_class4_with_deployment_field, json_deployment_config_file_path_4_5, sample_4_with_deployment_field
):
    """
    Test with explicit `deployment_name`.
    """
    # Act
    config = create_config_class4_with_deployment_field(
        fields={DEPLOY_FIELD_1: DEPLOY_CONFIG_SAMPLE_1_FIELD_1}, deployment_field=DEPLOY_FIELD_1,
        deployment_config=json_deployment_config_file_path_4_5
    )

    # Assert
    assert config.dict() == sample_4_with_deployment_field


def test__load_deployment_config_dict__deploy_field(create_config_class4, deployment_config_samples_4_5, sample_4):
    """
    Test with explicit `deployment_name` and deployment_config as dictionary.
    """
    # Act
    config = create_config_class4(
        deployment_name=DEPLOY_CONFIG_SAMPLE_1_FIELD_1, deployment_config=deployment_config_samples_4_5
    )

    # Assert
    assert config.dict() == sample_4


def test__load_deployment_config__2_deploy_fields_a():
    """
    Test that deployment field is not explicit and declared by `DeploymentField` at the same time.
    """
    # Arrange
    class ConfigA(Confident):
        env_a: str = 'nothing'
        env_b: str = DeploymentField('nothing')

    class ConfigB(Confident):
        env_a: str = DeploymentField('nothing')

    # Act & Assert
    with pytest.raises(ValueError):
        ConfigA(deployment_field='env_a', deployment_config={})

    with pytest.raises(ValueError):
        ConfigB(deployment_field='env_a', deployment_config={})


def test__load_deployment_config__2_deploy_fields_b():
    """
    Test that deployment field is not declared by `DeploymentField` and in `ConfidentConfig` class at the same time.
    """
    # Arrange
    class Config(Confident):
        env_a: str = DeploymentField('nothing')

        class ConfidentConfig:
            deployment_field = 'env_a'

    # Act & Assert
    with pytest.raises(ValueError):
        Config(deployment_config={})


def test__load_deployment_config__2_deploy_fields_c():
    """
    Test that deployment field is not declared by `DeploymentField` more than one.
    """
    # Arrange
    class Config(Confident):
        env_a: str = DeploymentField('nothing')
        env_b: str = DeploymentField('nothing')

    # Act & Assert
    with pytest.raises(ValueError):
        Config(deployment_config={})


def test__load_deployment_config__deploy_field_and_deploy_name():
    """
    Test that deployment field and deployment name are not used at the same time.
    """
    # Arrange
    class Config(Confident):
        env_a: str = 'nothing'

    # Act & Assert
    with pytest.raises(ValueError):
        Config(deployment_field='env_a', deployment_name='thing', deployment_config={})


@pytest.mark.parametrize('deployment_field, deployment_name', [('env_a', None), (None, 'nothing')])
def test__load_deployment_config__no_deploy_config(deployment_field, deployment_name):
    """
    Test that deployment config is inserted if deployment field or name is used.
    Case 1 - Only `deployment_field` is provided.
    Case 2 - Only `deployment_name` is provided.
    """
    # Arrange
    class Config(Confident):
        env_a: str = 'nothing'

    # Act & Assert
    with pytest.raises(ValueError):
        Config(deployment_field=deployment_field, deployment_name=deployment_name)


@pytest.mark.parametrize('deployment_name', [True, 7])
def test__load_deployment_config__deploy_name_is_not_valid(deployment_name):
    """
    Test that deployment name is a string.
    Case 1 - The `deployment_name` is type `bool`.
    Case 2 - The `deployment_name` is type `int`.
    """
    # Arrange
    deployment_config = {
        True: {
            "title": "a"
        },
        7: {
            "title": "b"
        }
    }

    class Config(Confident):
        env_a: str = deployment_name
        title: str

    # Act & Assert
    with pytest.raises(ValueError):
        Config(deployment_field='env_a', deployment_config=deployment_config)


def test__load_deployment_config__deploy_field_also_inside_deploy_config(
        create_config_class4, deployment_config_samples_4_5, sample_4
):
    """
    Test that the `deployment_field` is not appear in the 'deployment_config'.
    The `deployment_field` has to be decided before loading the `deployment_config` and cannot be change according
    to the deployment config.
    For example, `env` field (the deployment field) cannot appear in 'prod' deploy config:
    ```
    Class Config(Confident):
        env: str = DeploymentField('prod')  # <- declaring the deployment field and its default value.
        host: str

    deploy_config = {
        'prod': {
            env: 'dev'  # <- Redefining the deployment field.
            host: '0.0.0.0'
        }
        'dev': {
            host: '0.0.0.0'
        }
    }

    Config(deployment_config=deploy_config)  # Will raise `ValueError`. Otherwise, 'prod' deploy config will be chosen
                                             # but will be changed to value 'dev'.
    ```
    """
    # Act & Assert
    with pytest.raises(ValueError):
        create_config_class4(
            fields={SAMPLE_4_FIELD_1: DEPLOY_CONFIG_SAMPLE_1_FIELD_1},
            deployment_field=SAMPLE_4_FIELD_1,
            deployment_config=deployment_config_samples_4_5
        )
