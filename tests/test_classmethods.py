from pathlib import Path

import pytest

from confident import BaseConfig, ConfigSource
from tests.conftest import (
    CONFIG_SAMPLE_1_FIELD_1,
    MAP_FIELD_1,
    SPECS_FILE_1_SOURCE_PRIORITY,
    validate_file_not_exists,
)


class TestFromFiles:
    def test__from_files__loads_json(
        self, json_config_file_path_1, create_config_class1, sample_1
    ):
        config = create_config_class1.from_files(json_config_file_path_1)
        assert config.model_dump() == sample_1

    def test__from_files__loads_yaml(
        self, yaml_config_file_path_2, create_config_class3, sample_2
    ):
        config = create_config_class3.from_files(yaml_config_file_path_2)
        assert config.model_dump() == sample_2

    def test__from_files__ignore_missing_files_true(
        self, json_config_file_path_1, create_config_class1, sample_1
    ):
        not_exists = "not_exists_classmethod.json"
        validate_file_not_exists(file_name=not_exists)
        config = create_config_class1.from_files(
            [not_exists, json_config_file_path_1], ignore_missing_files=True
        )
        assert config.model_dump() == sample_1

    def test__from_files__ignore_missing_files_false(self, create_config_class1):
        not_exists = "not_exists_classmethod.json"
        validate_file_not_exists(file_name=not_exists)
        with pytest.raises(ValueError) as error:
            create_config_class1.from_files(not_exists, ignore_missing_files=False)
        assert "is not exists." in str(error.value)

    def test__from_files__with_explicit_values(self, json_config_file_path_1, sample_1):
        class MyConfig(BaseConfig):
            title: str
            host: str = "0.0.0.0"
            port: int = 80

        config = MyConfig.from_files(json_config_file_path_1, title="override")
        assert config.title == "override"

    def test__from_files__with_source_priority(
        self, json_config_file_path_1, create_config_class1, sample_1
    ):
        config = create_config_class1.from_files(
            json_config_file_path_1,
            source_priority=[ConfigSource.file, ConfigSource.init],
        )
        assert config.model_dump() == sample_1
        assert config.source_priority() == [ConfigSource.file, ConfigSource.init]


class TestFromMap:
    def test__from_map__with_map_name(
        self, create_config_class4, json_config_map_file_path_4_5, sample_4
    ):
        config = create_config_class4.from_map(
            json_config_map_file_path_4_5, map_name=CONFIG_SAMPLE_1_FIELD_1
        )
        assert config.model_dump() == sample_4

    def test__from_map__with_dict_config_map(
        self, create_config_class4, config_map_samples_4_5, sample_4
    ):
        config = create_config_class4.from_map(
            config_map_samples_4_5, map_name=CONFIG_SAMPLE_1_FIELD_1
        )
        assert config.model_dump() == sample_4

    def test__from_map__with_map_field(
        self,
        create_config_class4_with_map_field,
        json_config_map_file_path_4_5,
        sample_4_with_map_field,
    ):
        config = create_config_class4_with_map_field.from_map(
            json_config_map_file_path_4_5,
            map_field=MAP_FIELD_1,
            **{MAP_FIELD_1: CONFIG_SAMPLE_1_FIELD_1},
        )
        assert config.model_dump() == sample_4_with_map_field

    def test__from_map__with_source_priority(
        self, create_config_class4, config_map_samples_4_5, sample_4
    ):
        config = create_config_class4.from_map(
            config_map_samples_4_5,
            map_name=CONFIG_SAMPLE_1_FIELD_1,
            source_priority=[ConfigSource.map, ConfigSource.init],
        )
        assert config.model_dump() == sample_4
        assert config.source_priority() == [ConfigSource.map, ConfigSource.init]


class TestFromSpecs:
    def test__from_specs__loads_specs(
        self, specs_file_path_1, create_config_class1, sample_1
    ):
        config = create_config_class1.from_specs(specs_file_path_1, **sample_1)
        assert config.model_dump() == sample_1
        assert config.source_priority() == SPECS_FILE_1_SOURCE_PRIORITY
        assert config.specs().specs_path == Path(specs_file_path_1)

    def test__from_specs__with_source_priority(
        self, specs_file_path_1, create_config_class1, sample_1
    ):
        config = create_config_class1.from_specs(
            specs_file_path_1,
            source_priority=[ConfigSource.init, ConfigSource.file],
            **sample_1,
        )
        assert config.model_dump() == sample_1
        assert config.source_priority() == [ConfigSource.init, ConfigSource.file]

    def test__from_specs__equivalent_to_kwargs(
        self, specs_file_path_1, create_config_class1, sample_1
    ):
        """Verify from_specs produces the same result as passing _specs_path directly."""
        config_classmethod = create_config_class1.from_specs(
            specs_file_path_1, **sample_1
        )
        config_kwargs = create_config_class1(_specs_path=specs_file_path_1, **sample_1)
        assert config_classmethod.model_dump() == config_kwargs.model_dump()
        assert config_classmethod.source_priority() == config_kwargs.source_priority()


class TestFromSources:
    def test__from_sources__with_files(
        self, json_config_file_path_1, create_config_class1, sample_1
    ):
        config = create_config_class1.from_sources(files=json_config_file_path_1)
        assert config.model_dump() == sample_1

    def test__from_sources__with_map(
        self, create_config_class4, json_config_map_file_path_4_5, sample_4
    ):
        config = create_config_class4.from_sources(
            config_map=json_config_map_file_path_4_5,
            map_name=CONFIG_SAMPLE_1_FIELD_1,
        )
        assert config.model_dump() == sample_4

    def test__from_sources__with_files_and_map(
        self, json_config_file_path_1, json_config_map_file_path_4_5
    ):
        """Verify from_sources can combine files and config map in a single call."""

        class CombinedConfig(BaseConfig):
            title: str
            host: str
            port: int

        config = CombinedConfig.from_sources(
            files=json_config_file_path_1,
            config_map=json_config_map_file_path_4_5,
            map_name=CONFIG_SAMPLE_1_FIELD_1,
        )
        assert config.title == "my_app_1"
        assert config.host == "1.1.1.1"
        assert config.port == 8080

    def test__from_sources__with_ignore_missing_files(
        self, json_config_file_path_1, create_config_class1, sample_1
    ):
        config = create_config_class1.from_sources(
            files=[json_config_file_path_1, "not_exists_from_sources.json"],
            ignore_missing_files=True,
        )
        assert config.model_dump() == sample_1

    def test__from_sources__with_map_field(
        self,
        create_config_class4_with_map_field,
        json_config_map_file_path_4_5,
        sample_4_with_map_field,
    ):
        config = create_config_class4_with_map_field.from_sources(
            config_map=json_config_map_file_path_4_5,
            map_field=MAP_FIELD_1,
            **{MAP_FIELD_1: CONFIG_SAMPLE_1_FIELD_1},
        )
        assert config.model_dump() == sample_4_with_map_field

    def test__from_sources__with_specs_path(
        self, specs_file_path_1, create_config_class1, sample_1
    ):
        config = create_config_class1.from_sources(
            specs_path=specs_file_path_1, **sample_1
        )
        assert config.model_dump() == sample_1

    def test__from_sources__with_source_priority(
        self, json_config_file_path_1, create_config_class1, sample_1
    ):
        config = create_config_class1.from_sources(
            files=json_config_file_path_1,
            source_priority=[ConfigSource.file, ConfigSource.init],
        )
        assert config.model_dump() == sample_1
        assert config.source_priority() == [ConfigSource.file, ConfigSource.init]
