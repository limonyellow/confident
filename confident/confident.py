import importlib
import inspect
import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Union, List, Any, Dict, Optional

from pydantic import BaseModel

from confident.config_property import ConfigProperty
from confident.config_source import ConfigSource
from confident.utils import load_file, load_env_files

SPECS_ATTR = '_specs'
FULL_CONFIG_ATTR = '_full'
ALL_LOADED_CONFIG_ATTR = '_loaded'

CONFIG_CLASS_NAME = 'ConfidentConfig'
CONFIG_CLASS_SPECS_PATH_ATTR = 'specs_path'
CONFIG_CLASS_ENV_FILES_ATTR = 'env_files'
CONFIG_CLASS_FILES_ATTR = 'files'
CONFIG_CLASS_PREFER_FILES_ATTR = 'prefer_files'
CONFIG_CLASS_IGNORE_MISSING_FILES_ATTR = 'ignore_missing_files'
CONFIG_CLASS_DEPLOYMENT_NAME_ATTR = 'deployment_name'
CONFIG_CLASS_DEPLOYMENT_FIELD_ATTR = 'deployment_field'
CONFIG_CLASS_DEPLOYMENT_CONFIG_ATTR = 'deployment_config'
CONFIG_CLASS_SOURCE_PRIORITY_ATTR = 'source_priority'

DEFAULT_SOURCE_PRIORITY = [
    ConfigSource.explicit, ConfigSource.env_var, ConfigSource.deployment, ConfigSource.file, ConfigSource.class_default
]

SOURCE_PRIORITY_PREFER_FILES = [
    ConfigSource.explicit, ConfigSource.env_var, ConfigSource.file, ConfigSource.deployment, ConfigSource.class_default
]

PREFER_FILES_DEFAULT = False
IGNORE_MISSING_FILES_DEFAULT = True


class ConfidentConfigSpecs(BaseModel):
    """
    A model that holds all the metadata regarding the Confident config object.
    """
    specs_path: Optional[Path] = None
    env_files: List[Path] = []
    files: List[Path] = []
    prefer_files: bool = PREFER_FILES_DEFAULT
    ignore_missing_files: bool = IGNORE_MISSING_FILES_DEFAULT
    explicit_fields: Optional[Dict[str, Any]] = None
    deployment_name: Optional[str] = None
    deployment_field: Optional[str] = None
    deployment_config: Optional[Union[Path, Dict[str, Union[Path, Dict[str, Any]]]]] = None
    class_path: Optional[Path] = None
    creation_path: Optional[Path] = None
    source_priority: List[ConfigSource] = DEFAULT_SOURCE_PRIORITY


class Confident(BaseModel):
    """
    By inheriting from this class the inheriting object will have its field values filled in the next order
    (can be changed by providing `source_priority` list):
    - Explicit key-value arguments.
    - Environment variables.
    - Deployment config files.
    - Config files.
    - Default values.
    """
    __slots__ = (SPECS_ATTR, FULL_CONFIG_ATTR, ALL_LOADED_CONFIG_ATTR)

    def __init__(
            self,
            specs_path: Optional[Union[Path, str]] = None,
            env_files: Optional[Union[Path, str, List[Union[Path, str]]]] = None,
            files: Optional[Union[Path, str, List[Union[Path, str]]]] = None,
            prefer_files: Optional[bool] = None,
            ignore_missing_files: Optional[bool] = None,
            fields: Optional[Dict[str, Any]] = None,
            deployment_name: Optional[str] = None,
            deployment_field: Optional[str] = None,
            deployment_config: Optional[Union[Path, str, Dict[str, Union[Path, str, Dict[str, Any]]]]] = None,
            source_priority: List[ConfigSource] = None,
    ):
        """
        Args:
            specs_path: File path to load the `ConfidentConfigSpecs` object from.
                This metadata will be used to insert the config properties into the created Confident config object.
            env_files: File paths of '.env' files with rows in the format '<env_var>=<value>'
                to insert as config properties.
            files: File paths of 'json' or 'yaml' files to insert as config properties.
            prefer_files: In case of identical property name from different sources, whether to insert the values from
                the files over the values from environment variables.
            ignore_missing_files: Whether to skip when a given file path is not exists or to raise a matching error.
            fields: Dictionary of keys matching the object fields names to override their values.
        """
        # Prepare metadata.
        subclass_location = self._get_subclass_file_path()
        caller_module = inspect.getmodule(inspect.stack()[1][0])
        caller_location = caller_module.__file__ if caller_module else Path.cwd()
        class_config_dict = self._get_class_config_dict()

        deployment_field = self._find_deployment_field(
            explicit_deployment_field=deployment_field or class_config_dict.get(CONFIG_CLASS_DEPLOYMENT_FIELD_ATTR)
        )

        specs_path = specs_path or class_config_dict.get(CONFIG_CLASS_SPECS_PATH_ATTR)
        if specs_path:
            specs = ConfidentConfigSpecs.parse_file(specs_path)
            specs.specs_path = Path(specs_path)
            specs.class_path = subclass_location
            specs.creation_path = caller_location
        else:
            env_files = env_files or class_config_dict.get(CONFIG_CLASS_ENV_FILES_ATTR)
            env_files = [env_files] if isinstance(env_files, str) else env_files or []

            files = files or class_config_dict.get(CONFIG_CLASS_FILES_ATTR)
            files = [files] if isinstance(files, str) else files or []

            prefer_files = (
                    prefer_files if prefer_files is not None
                    else class_config_dict.get(CONFIG_CLASS_PREFER_FILES_ATTR, PREFER_FILES_DEFAULT)
            )
            ignore_missing_files = (
                ignore_missing_files if ignore_missing_files is not None
                else class_config_dict.get(CONFIG_CLASS_IGNORE_MISSING_FILES_ATTR, IGNORE_MISSING_FILES_DEFAULT)
            )

            specs = ConfidentConfigSpecs(
                specs_path=specs_path,
                env_files=env_files,
                files=files,
                prefer_files=prefer_files,
                ignore_missing_files=ignore_missing_files,
                explicit_fields=fields,
                deployment_name=deployment_name or class_config_dict.get(CONFIG_CLASS_DEPLOYMENT_NAME_ATTR),
                deployment_field=deployment_field,
                deployment_config=deployment_config or class_config_dict.get(CONFIG_CLASS_DEPLOYMENT_CONFIG_ATTR),
                class_path=subclass_location,
                creation_path=caller_location,
                source_priority=(
                    source_priority or class_config_dict.get(CONFIG_CLASS_SOURCE_PRIORITY_ATTR) or
                    (SOURCE_PRIORITY_PREFER_FILES if prefer_files else DEFAULT_SOURCE_PRIORITY)
                )
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

        Raises:
            ValueError -
                If file is not exists and ignore_missing_files=False.
                If the file is not in a supported format.
        """
        file_properties = {}
        for file_path in specs.files:
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
            # If the field is required, there is no default value to load.
            if model_field.required:
                continue
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
    ) -> Dict[str, ConfigProperty]:
        """
        Loads the relevant deployment config properties.

        Args:
            specs: Config specifications object.
            all_properties: All loaded properties to find the deployment attribute in.

        Raises:
            ValueError - If wrong combination or values of fields is detected in the following cases:
                If `deployment_field` and also `deployment_name` are present.
                If no `deployment_config` is provided.
                If the `deployment_name` is not of type `str`.
                If the `deployment_field` appears inside the `deployment_config`.
        """
        # Extracts the deployment metadata field and validates them.
        deployment_name = specs.deployment_name
        deployment_field = specs.deployment_field
        deployment_config = specs.deployment_config
        deployment_location = specs.creation_path

        if deployment_field is None and deployment_name is None:
            return {}
        if deployment_field is not None and deployment_name is not None:
            raise ValueError('Cannot have both `deployment_field` and `deployment_name`. Only one can be used.')
        if deployment_config is None:
            raise ValueError('No `deployment_config` was provided.')
        if isinstance(deployment_config, Path):
            deployment_location = deployment_config
            deployment_config = load_file(deployment_location)

        deployment = {}
        deployment_properties = {}

        # According to the deployment name, extracts the chosen deployment.
        if deployment_name:
            deployment = deployment_config.get(deployment_name)
        if deployment_field:
            # Search for the deployment name in all possible sources ordered by priority.
            for source in dict.fromkeys(specs.source_priority).keys():
                if source == ConfigSource.deployment:
                    continue
                config_property = all_properties[source].get(deployment_field)
                if config_property:
                    deployment_name = config_property.value
                    break

            if not isinstance(deployment_name, str):
                raise ValueError(
                    f'{deployment_field=} is not valid. Value has to be <str> not "{deployment_name}" '
                    f'type={type(deployment_name)}'
                )
            deployment = deployment_config.get(deployment_name)

        if deployment is None:
            raise KeyError(f'No matching deployment to {deployment_name=}. Check your `deployment_config`')

        if isinstance(deployment, str):
            deployment = load_file(deployment)

        # Creates the `ConfigProperty` dictionary.
        for name, value in deployment.items():
            if name == deployment_field:
                raise ValueError(
                    f"{deployment_field=} cannot appear in the deployment config key '{deployment_name}'. "
                    f"Look for {deployment_location=} at '{deployment_name}'. "
                    f"Remove '{deployment_field}' key or change the deployment field."
                )
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

    def _get_subclass_file_path(self) -> Union[str, Path]:
        """
        Gets the path that the config class is initiated from.
        Tries to find the path of the caller module.
        If the module can't be imported returns the module name.
        If there is no module that called this class constructor, returns the current working path.
        """
        try:
            return importlib.import_module(self.__module__).__file__
        except ImportError:
            return self.__module__
        except AttributeError:
            return Path.cwd()

    def _get_class_config_dict(self) -> Dict[str, Any]:
        """
        Tries to retrieve the config class that was declared in the subclass.

        Returns:
            Dictionary with config values.
        """
        try:
            class_config = self.__getattribute__(CONFIG_CLASS_NAME)
        except AttributeError:
            return {}
        return class_config.__dict__

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
        # model_field.outer_type_ can be type annotation and not type.
        if (model_field and isinstance(model_field.outer_type_, type)
                and isinstance(origin_value, model_field.outer_type_)):
            return origin_value
        if isinstance(origin_value, str):
            try:
                return json.loads(origin_value)
            except (TypeError, ValueError):
                pass
        return origin_value

    def _find_deployment_field(self, explicit_deployment_field) -> str:
        """
        Searches if one of the fields declared in the sub class has marked as the deployment field.
        Args:
            explicit_deployment_field: The deployment field received as argument.

        Returns:
            A single deployment field. None if no field provided in any way.

        Raises:
            ValueError - If more than one deployment fields is received.
        """
        properties_marked_as_deployment_field = [
            name for name, model_field in self.__fields__.items() if
            model_field.field_info.extra.get('deployment_field')
        ]
        if not properties_marked_as_deployment_field:
            return explicit_deployment_field
        if explicit_deployment_field and properties_marked_as_deployment_field:
            raise ValueError(
                f'Cannot have both explicit `deployment_field` and also `DeploymentField()` '
                f'in {self.__class__.__name__} declaration'
            )
        if len(properties_marked_as_deployment_field) > 1:
            raise ValueError(f'Cannot have more then one `DeploymentField()` in {self.__class__.__name__} declaration')
        return properties_marked_as_deployment_field[0]

    def specs(self) -> ConfidentConfigSpecs:
        """
        Returns: A deep copy of the config class specs.
        """
        return deepcopy(self.__getattribute__(SPECS_ATTR))

    def full_details(self) -> Dict[str, ConfigProperty]:
        """
        Returns: A dictionary with details of every field.
        """
        return deepcopy(self.__getattribute__(FULL_CONFIG_ATTR))

    def all_loaded_properties(self) -> Dict[ConfigSource, Dict[str, ConfigProperty]]:
        """
        Returns: A dictionary divided to sources with all the fields that were loaded during the creation of the config
        class. Even the fields
        """
        return deepcopy(self.__getattribute__(ALL_LOADED_CONFIG_ATTR))
