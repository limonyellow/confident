import importlib
import inspect
import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Union, List, Any, Dict, Optional

from confident.utils import load_file, load_env_files
from config_property import ConfigProperty
from config_source import ConfigSource
from pydantic import BaseModel

SPECS_ATTR = '_specs'
FULL_CONFIG_ATTR = '_full'
ALL_LOADED_CONFIG_ATTR = '_loaded'

DEFAULT_SOURCE_PRIORITY = [
    ConfigSource.explicit, ConfigSource.env_var, ConfigSource.deployment, ConfigSource.file, ConfigSource.class_default
]

SOURCE_PRIORITY_PREFER_FILES = [
    ConfigSource.explicit, ConfigSource.env_var, ConfigSource.file, ConfigSource.deployment, ConfigSource.class_default
]


class ConfidentConfigSpecs(BaseModel):
    """
    A model that holds all the metadata regarding the Confident config object.
    """
    specs_path: Optional[Path] = None
    env_files: Optional[List[Path]] = None
    config_files: Optional[List[Path]] = None
    prefer_files: bool = False
    ignore_missing_files: bool = True
    explicit_fields: Optional[Dict[str, Any]] = None
    deployment_name: Optional[str] = None
    deployment_attr: Optional[str] = None
    deployments: Optional[Union[Dict[str, Union[Dict[str, str], Path]], Path]] = None
    class_path: Optional[Path] = None
    creation_path: Optional[Path] = None
    source_priority: List[ConfigSource] = DEFAULT_SOURCE_PRIORITY


class Confident(BaseModel):
    """
    By inheriting from this class the inheriting object will have its field values filled in the next order:
    - Explicit key-value arguments.
    - Files of environment variables ('.env' files).
    - Environment variables of the operating system.
    - Config files.
    """
    __slots__ = (SPECS_ATTR, FULL_CONFIG_ATTR, ALL_LOADED_CONFIG_ATTR)

    def __init__(
            self,
            specs_path: Optional[str] = None,
            env_files: Optional[Union[str, List[str]]] = None,
            config_files: Optional[Union[str, List[str]]] = None,
            prefer_files: bool = False,
            ignore_missing_files: bool = True,
            fields: Optional[Dict['str', Any]] = None,
            deployment_name: Optional[str] = None,
            deployment_attr: Optional[str] = None,
            deployments: Optional[Union[Dict[str, Union[Dict[str, str], str]], str]] = None,
            source_priority: List[ConfigSource] = None,
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
        subclass_location = self._get_subclass_file_path()
        caller_module = inspect.getmodule(inspect.stack()[1][0])
        caller_location = caller_module.__file__ if caller_module else None

        if specs_path:
            specs = ConfidentConfigSpecs.parse_file(specs_path)
            specs.specs_path = specs_path
        else:
            env_files = [env_files] if isinstance(env_files, str) else env_files or []
            config_files = [config_files] if isinstance(config_files, str) else config_files or []
            specs = ConfidentConfigSpecs(
                specs_path=specs_path,
                env_files=env_files,
                config_files=config_files,
                prefer_file=prefer_files,
                ignore_missing_files=ignore_missing_files,
                explicit_fields=fields,
                deployment_name=deployment_name,
                deployment_attr=deployment_attr,
                deployments=deployments,
                class_path=subclass_location,
                creation_path=caller_location,
                source_priority=source_priority or SOURCE_PRIORITY_PREFER_FILES if prefer_files else
                SOURCE_PRIORITY_PREFER_FILES
            )

        # Load properties from all sources.
        all_properties = {ConfigSource.explicit: self._load_explicit_properties(specs=specs)}
        if specs.env_files:
            load_env_files(specs.env_files)
        all_properties[ConfigSource.env_var] = self._load_env_properties()
        all_properties[ConfigSource.file] = self._load_file_properties(specs=specs)
        all_properties[ConfigSource.class_default] = self._load_default_properties(specs=specs)
        all_properties[ConfigSource.deployment] = self._load_deployment_properties(
            specs=specs, all_properties=all_properties
        )

        merged_properties = self._merge_properties(specs=specs, all_properties=all_properties)

        # Create the final object.
        object.__setattr__(self, SPECS_ATTR, specs)
        object.__setattr__(self, FULL_CONFIG_ATTR, merged_properties)
        object.__setattr__(self, ALL_LOADED_CONFIG_ATTR, all_properties)
        super().__init__(
            **{key: config_property.value for key, config_property in merged_properties.items()}
        )

    @staticmethod
    def _merge_properties(
            specs: ConfidentConfigSpecs, all_properties: Dict[ConfigSource, Dict[str, ConfigProperty]]
    ) -> Dict[str, Any]:
        """
        Construct a dictionary with properties from all sources according to their priority.
        Args:
            specs: Config specifications object.
            all_properties: Dictionary with all properties from every source.

        Returns:
            Dictionary with all the properties together. Less important keys will be overridden by higher priority keys.
        """
        merged_properties = {}
        # Remove duplicate `ConfigSource` values and maintain the list order.
        for source in reversed(dict.fromkeys(specs.source_priority).keys()):
            merged_properties.update(all_properties.get(source, {}))

        return merged_properties

    @staticmethod
    def _load_explicit_properties(specs: ConfidentConfigSpecs) -> Dict[str, ConfigProperty]:
        if not specs.explicit_fields:
            return {}
        return {
            key: ConfigProperty(
                name=key, value=value, source_name=ConfigSource.explicit, source_type=ConfigSource.explicit,
                source_location=specs.creation_path
            ) for key, value in specs.explicit_fields.items()
        }

    def _load_env_properties(self) -> Dict[str, ConfigProperty]:
        """
        Finds and loads requested config fields from environment variables into a dictionary.
        """
        env_properties = {}

        for key in self.__fields__.keys():
            env_value = os.getenv(key)
            if env_value:
                env_properties[key] = ConfigProperty(
                    name=key,
                    value=self._convert_property_value(property_name=key, origin_value=env_value),
                    origin_value=env_value,
                    source_name=key,
                    source_type=ConfigSource.env_var,
                    source_location=key
                )
        return env_properties

    def _load_file_properties(self, specs: ConfidentConfigSpecs) -> Dict[str, ConfigProperty]:
        """
        Finds and loads requested config fields from files into a dictionary.

        Args:
            specs: The specifications of the config object.
        """
        file_properties = {}
        for file_path in specs.config_files:
            if not os.path.isfile(file_path) and specs.ignore_missing_files:
                continue
            file_dict = load_file(path=file_path)

            # Creates a dict with `ConfigProperty` from the file data and merges them with the rest of the properties
            # from other files.
            file_properties.update(
                {key: ConfigProperty(
                    name=key,
                    value=self._convert_property_value(property_name=key, origin_value=value),
                    origin_value=value,
                    source_name=os.path.basename(file_path),
                    source_type=ConfigSource.file,
                    source_location=file_path
                ) for key, value in file_dict.items()})

        # Returns only the properties that are relevant to the class definition.
        return {key: file_properties[key] for key in file_properties.keys() & self.__fields__.keys()}

    def _load_default_properties(self, specs: ConfidentConfigSpecs) -> Dict[str, ConfigProperty]:
        """
        Loads default values declared in the inheriting class into a dictionary.
        """
        default_properties = {}
        for field_name, model_field in self.__fields__.items():
            # Uses `pydantic` ModelField to retrieve the default values of the model.
            default_value = model_field.get_default()
            default_properties[field_name] = ConfigProperty(
                name=field_name,
                value=default_value,
                source_name=self.__class__.__name__,
                source_type=ConfigSource.class_default,
                source_location=specs.class_path,
            )
        return default_properties

    def _load_deployment_properties(
            self, specs: ConfidentConfigSpecs, all_properties: Dict[ConfigSource, Dict[str, ConfigProperty]]
    ):
        """
        Loads the relevant deployment config properties.

        Args:
            specs: Config specifications object.
            all_properties: All loaded properties to find the deployment attribute in.
        """
        deployment_name = specs.deployment_name
        deployment_attr = specs.deployment_attr
        deployments = specs.deployments
        deployment_location = specs.creation_path

        if deployment_attr is None and deployment_name is None:
            return {}
        if deployment_attr is not None and deployment_name is not None:
            raise ValueError('Can not have both `deployment_attr` and `deployment_name`. Only one can be used.')
        if deployments is None:
            raise ValueError('Environment default is enabled but no `deployments` was provided.')
        if isinstance(deployments, Path):
            deployment_location = deployments
            deployments = load_file(deployment_location)

        deployment = {}
        deployment_properties = {}

        if deployment_name:
            deployment = deployments.get(deployment_name)
        if deployment_attr:
            # Search for the deployment name in all possible sources ordered by priority.
            for source in reversed(dict.fromkeys(specs.source_priority).keys()):
                if source == ConfigSource.deployment:
                    continue
                config_property = all_properties[source].get(deployment_attr)
                if config_property:
                    deployment_name = config_property.value
                    break

            if not isinstance(deployment_name, str):
                raise ValueError(
                    f'{deployment_attr=} is not valid. Value has to be <str> not {deployment_name} '
                    f'type={type(deployment_name)}'
                )
            deployment = deployments.get(deployment_name)

        if isinstance(deployment, str):
            deployment = load_file(deployment)

        for name, value in deployment.items():
            deployment_properties[name] = ConfigProperty(
                name=name,
                value=self._convert_property_value(property_name=name, origin_value=value),
                origin_value=value,
                source_name=deployment_name,
                source_type=ConfigSource.deployment,
                source_location=deployment_location,
            )

        specs.deployment_name = deployment_name
        return deployment_properties

    def _get_subclass_file_path(self):
        try:
            return importlib.import_module(self.__module__).__file__
        except ImportError:
            return self.__module__

    def _convert_property_value(self, property_name: str, origin_value: Any) -> Any:
        """
        Tries to convert the property value to the right type.
        If nothing works, do nothing and let pydantic `BaseModel` `__init__` call handle the validation.
        Args:
            property_name: The name of the attribute to find its expected type.
            origin_value: The original value retrieved from the config source.

        Returns:
            The converted origin value. Can also be untouched.
        """
        model_field = self.__fields__.get(property_name)
        if model_field and isinstance(origin_value, model_field.type_):
            return origin_value
        if isinstance(origin_value, str):
            try:
                return json.loads(origin_value)
            except (TypeError, ValueError):
                pass
        return origin_value

    def specs(self):
        return deepcopy(self.__getattribute__(SPECS_ATTR))

    def full_details(self):
        return deepcopy(self.__getattribute__(FULL_CONFIG_ATTR))

    def all_loaded_properties(self):
        return deepcopy(self.__getattribute__(ALL_LOADED_CONFIG_ATTR))
