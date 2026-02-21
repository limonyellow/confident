import pytest
from pydantic import create_model

from confident import BaseConfig, MapField
from confident.map_field import MAP_FIELD_FLAG
from tests.conftest import CONFIG_SAMPLE_1_FIELD_1, MAP_FIELD_1, SAMPLE_4_FIELD_1


def test__load_config_map__deploy_name(
    create_config_class4, json_config_map_file_path_4_5, sample_4
):
    """
    Test with explicit `_map_name`.
    """
    # Act
    config = create_config_class4(
        _map_name=CONFIG_SAMPLE_1_FIELD_1, _config_map=json_config_map_file_path_4_5
    )

    # Assert
    assert config.model_dump() == sample_4


def test__load_config_map__map_field(
    create_config_class4_with_map_field,
    json_config_map_file_path_4_5,
    sample_4_with_map_field,
):
    """
    Test with explicit `_map_name`.
    """
    # Act
    config = create_config_class4_with_map_field(
        **{MAP_FIELD_1: CONFIG_SAMPLE_1_FIELD_1},
        _map_field=MAP_FIELD_1,
        _config_map=json_config_map_file_path_4_5,
    )

    # Assert
    assert config.model_dump() == sample_4_with_map_field


def test__load_config_map_dict__map_field(
    create_config_class4, config_map_samples_4_5, sample_4
):
    """
    Test with explicit `_map_name` and deployment_config as dictionary.
    """
    # Act
    config = create_config_class4(
        _map_name=CONFIG_SAMPLE_1_FIELD_1, _config_map=config_map_samples_4_5
    )

    # Assert
    assert config.model_dump() == sample_4


def test__load_config_map__map_name_points_to_file(json_config_file_path_1, sample_1):
    """
    Test that the value of the map name can be a path to 'object' (json/yaml).
    """
    # Arrange
    map_name = "prod"
    config_map = {map_name: json_config_file_path_1}
    config_cls = create_model(
        "ConfigClass",
        __base__=BaseConfig,
        **{key: (type(value), ...) for key, value in sample_1.items()},
    )

    # Act
    config = config_cls(_config_map=config_map, _map_name=map_name)

    # Assert
    assert config.model_dump() == sample_1


def test__load_config_map__2_map_fields_a():
    """
    Test that map field is not explicit and declared by `MapField` at the same time.
    """

    # Arrange
    class ConfigA(BaseConfig):
        env_a: str = "nothing"
        env_b: str = MapField("nothing")

    class ConfigB(BaseConfig):
        env_a: str = MapField("nothing")

    # Act & Assert
    with pytest.raises(ValueError) as error:
        ConfigA(_map_field="env_a", _config_map={})
    assert (
        f"Cannot have both explicit `_map_field` and also `MapField()` in {ConfigA.__name__} declaration"
        in str(error.value)
    )

    with pytest.raises(ValueError) as error:
        ConfigB(_map_field="env_a", _config_map={})
    assert (
        f"Cannot have both explicit `_map_field` and also `MapField()` in {ConfigB.__name__} declaration"
        in str(error.value)
    )


def test__load_config_map__2_map_fields_b():
    """
    Test that map field is not declared by `MapField` and in `ConfidentConfig` class at the same time.
    """

    # Arrange
    class Config(BaseConfig):
        env_a: str = MapField("nothing")

    # Act & Assert
    with pytest.raises(ValueError) as error:
        Config(_config_map={})
    assert "No `config_map` was provided." in str(error.value)


def test__load_config_map__2_map_fields_c():
    """
    Test that map field is not declared by `MapField` more than one.
    """

    # Arrange
    class Config(BaseConfig):
        env_a: str = MapField("nothing")
        env_b: str = MapField("nothing")

    # Act & Assert
    with pytest.raises(ValueError) as error:
        Config(_config_map={})
    assert "Cannot have more then one `MapField()` in Config declaration" in str(
        error.value
    )


def test__use_map_field_flag_inside_MapField():
    """
    Test that the MAP_FIELD_FLAG isn't used ambiguously.
    """
    with pytest.raises(ValueError) as error:
        MapField("nothing", **{MAP_FIELD_FLAG: "nothing2"})
    assert f'Cannot use "{MAP_FIELD_FLAG}" key inside `MapField()`.' in str(error.value)


def test__load_config_map__map_field_and_deploy_name():
    """
    Test that map field and map name are not used at the same time.
    """

    # Arrange
    class Config(BaseConfig):
        env_a: str = "nothing"

    # Act & Assert
    with pytest.raises(ValueError) as error:
        Config(_map_field="env_a", _map_name="thing", _config_map={})
    assert "Cannot have both `map_field` and `map_name`. Only one can be used." in str(
        error.value
    )


@pytest.mark.parametrize("map_field, map_name", [("env_a", None), (None, "nothing")])
def test__load_config_map__no_config_map(map_field, map_name):
    """
    Test that deployment config is inserted if deployment field or name is used.
    Case 1 - Only `map_field` is provided.
    Case 2 - Only `map_name` is provided.
    """

    # Arrange
    class Config(BaseConfig):
        env_a: str = "nothing"

    # Act & Assert
    with pytest.raises(ValueError) as error:
        Config(_map_field=map_field, _map_name=map_name)
    assert "No `config_map` was provided." in str(error.value)


@pytest.mark.parametrize("map_name", [True, 7])
def test__load_config_map__map_name_is_not_valid(map_name):
    """
    Test that map name is a string.
    Case 1 - The `map_name` is type `bool`.
    Case 2 - The `map_name` is type `int`.
    """
    # Arrange
    config_map = {True: {"title": "a"}, 7: {"title": "b"}}

    class Config(BaseConfig):
        env_a: str = map_name
        title: str

    # Act & Assert
    with pytest.raises(ValueError) as error:
        Config(_map_field="env_a", _config_map=config_map)
    assert (
        f''''env_a' is not valid. Value has to be <str> not "{map_name}" type={type(map_name)}'''
        in str(error.value)
    )


def test__load_config_map__map_name_is_not_found():
    """
    Test if map name is not found - an indicative error will be raised.
    """

    # Arrange
    class Config(BaseConfig):
        env: str = MapField("prod")

    # Act & Assert
    with pytest.raises(KeyError) as error:
        Config(_config_map={"dev": {}})
    assert "No matching map config to map_name='prod'. Check your `config_map`." in str(
        error.value
    )


def test__load_config_map__map_field_also_inside_config_map(
    create_config_class4, config_map_samples_4_5, sample_4
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
            **{SAMPLE_4_FIELD_1: CONFIG_SAMPLE_1_FIELD_1},
            _map_field=SAMPLE_4_FIELD_1,
            _config_map=config_map_samples_4_5,
        )
    assert """map_field='host' cannot appear in the map config key 'prod'.""" in str(
        error.value
    )
