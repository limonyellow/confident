import os
from copy import deepcopy
from typing import Union, List, Any, Dict, Optional

from confident.utils import load_config_file, load_env_files
from config_property import ConfigProperty
from config_source import ConfigSource
from pydantic import BaseModel
from pydantic.fields import ModelField

SPECS_ATTR = '_specs'
FULL_CONFIG_ATTR = '_full'


class ConfidentConfigSpecs(BaseModel):
    """
    A model that holds all the metadata regarding the Confident config object.
    """
    specs_path: Optional[str] = None
    env_files: Optional[List[str]] = None
    config_files: Optional[List[str]] = None
    prefer_files: bool = False
    ignore_missing_files: bool = True
    explicit_fields: Optional[Dict['str', Any]] = None


class Confident(BaseModel):
    """
    By inheriting from this class the inheriting object will have its field values filled in the next order:
    - Explicit key-value arguments.
    - Files of environment variables ('.env' files).
    - Environment variables of the operating system.
    - Config files.
    """
    __slots__ = (SPECS_ATTR, FULL_CONFIG_ATTR)

    def __init__(
            self,
            specs_path: Optional[str] = None,
            env_files: Optional[Union[str, List[str]]] = None,
            config_files: Optional[Union[str, List[str]]] = None,
            prefer_files: bool = False,
            ignore_missing_files: bool = True,
            fields: Optional[Dict['str', Any]] = None
    ):
        """
        Args:
            specs_path: File path to load the `ConfidentConfigSpecs` object from.
                This metadata will be used to insert the config properties into the created Confident config object.
            env_files: File paths of '.env' files with rows in the format '<env_var>=<value>'
                to insert as config properties.
            config_files: File paths of 'json' or 'yaml' files to insert as config properties.
            prefer_files: In case of identical property name from different sources, whether to insert the values from
                the files over the values from environment variables.
            ignore_missing_files: Whether to skip when a given file path is not exists or to raise a matching error.
            fields: Dictionary of keys matching the object fields names to override their values.
        """
        # Prepare metadata.
        if specs_path:
            specs = ConfidentConfigSpecs.parse_file(specs_path)
            specs.specs_path = specs_path
        else:
            env_files = [env_files] if isinstance(env_files, str) else env_files or []
            config_files = [config_files] if isinstance(config_files, str) else config_files or []
            specs = ConfidentConfigSpecs(specs_path=specs_path, env_files=env_files, config_files=config_files,
                                         prefer_file=prefer_files, ignore_missing_files=ignore_missing_files,
                                         explicit_fields=fields)

        # Load properties from all sources.
        if specs.env_files:
            load_env_files(specs.env_files)
        env_properties = self._load_env_properties()
        file_properties = self._load_file_properties(specs)
        explicit_properties = self._load_explicit_properties(specs)
        default_properties = self._load_default_properties()

        full_properties = self._merge_properties(
            specs=specs,
            explicit_properties=explicit_properties,
            env_properties=env_properties,
            file_properties=file_properties,
            default_properties=default_properties
        )

        # Create the final object.
        object.__setattr__(self, SPECS_ATTR, specs)
        object.__setattr__(self, FULL_CONFIG_ATTR, full_properties)
        super().__init__(
            **{key: config_property.value for key, config_property in full_properties.items()}
        )

    @staticmethod
    def _merge_properties(
            specs, explicit_properties, env_properties, file_properties, default_properties
    ) -> Dict[str, Any]:
        """
        Construct a dictionary with properties from all sources according to their priority.
        Args:
            specs: Config specifications object.
            explicit_properties: Fields that were given explicitly in the constructor.
            env_properties: Fields retrieved from environment variables.
            file_properties: Fields retrieved from files.
            default_properties: Default values in the class declaration.

        Returns:
            Dictionary with all the properties together. Less important keys will be overridden by higher priority keys.
        """
        properties = {}
        if specs.prefer_files:
            properties.update({**explicit_properties, **env_properties, **file_properties, **default_properties})
        else:
            properties.update({**explicit_properties, **file_properties, **env_properties, **default_properties})
        return properties

    def _load_default_properties(self) -> Dict[str, Any]:
        """
        Loads default values declared in the inheriting class into a dictionary.
        """
        default_properties = {}
        for field_name, model_field in self.__fields__.items():
            # Uses `pydantic` ModelField to retrieve the default values of the model.
            default_value = model_field.get_default()
            if default_value is not None:
                default_properties[field_name] = ConfigProperty(
                    name=field_name,
                    value=default_value,
                    source_name=ConfigSource.class_default,
                    source_type=ConfigSource.class_default
                )
        return default_properties

    @staticmethod
    def _load_explicit_properties(specs: ConfidentConfigSpecs) -> Dict[str, Any]:
        if not specs.explicit_fields:
            return {}
        return {key: ConfigProperty(name=key, value=value, source_name=ConfigSource.explicit,
                                    source_type=ConfigSource.explicit) for key, value in specs.explicit_fields.items()}

    def _load_env_properties(self) -> Dict[str, Any]:
        """
        Finds and loads requested config fields from environment variables into a dictionary.
        """
        env_properties = {}

        for key in self.__fields__.keys():
            env_value = os.getenv(key)
            if env_value:
                env_properties[key] = ConfigProperty(name=key, value=env_value, source_name=ConfigSource.environment,
                                                     source_type=ConfigSource.environment)
        return env_properties

    def _load_file_properties(self, specs: ConfidentConfigSpecs) -> Dict[str, Any]:
        """
        Finds and loads requested config fields from files into a dictionary.

        Args:
            specs: The specifications of the config object.
        """
        file_properties = {}
        for file_path in specs.config_files:
            if not os.path.isfile(file_path) and specs.ignore_missing_files:
                continue
            file_dict = load_config_file(path=file_path)
            file_properties.update(
                {key: ConfigProperty(name=key, value=value, source_name=file_path,
                                     source_type=ConfigSource.file) for key, value in file_dict.items()})

        return {key: file_properties[key] for key in file_properties.keys() & self.__fields__.keys()}

    def get_specs(self):
        return deepcopy(self.__getattribute__(SPECS_ATTR))

    def get_full_details(self):
        return deepcopy(self.__getattribute__(FULL_CONFIG_ATTR))
