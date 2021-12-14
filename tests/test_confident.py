from tests.conftest import SAMPLE_1_FILE_NAME, SAMPLE_3_FILE_NAME


def test_load_fields_from_json_file(json_config_file_path_1, ConfigClass1, sample_1):
    # Act
    config = ConfigClass1(config_files=SAMPLE_1_FILE_NAME)

    # Assert
    assert config.dict() == sample_1


def test_load_fields_from_yaml_file(yaml_config_file_path_3, ConfigClass3, sample_3):
    # Act
    config = ConfigClass3(config_files=SAMPLE_3_FILE_NAME)

    # Assert
    assert config.dict() == sample_3
