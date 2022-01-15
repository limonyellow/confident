import importlib
import inspect
import os
from copy import deepcopy
from typing import Union, List, Any, Dict, Optional

from confident.utils import load_file, load_env_files
from config_property import ConfigProperty
from config_source import ConfigSource
from pydantic import BaseModel

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
    deployment_name: Optional[str] = None
    deployment_attr: Optional[str] = None
    deployments: Optional[Union[Dict[str, Union[Dict[str, str], str]], str]] = None
    class_path: Optional[str] = None
    creation_path: Optional[str] = None


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
            fields: Optional[Dict['str', Any]] = None,
            deployment_name: Optional[str] = None,
            deployment_attr: Optional[str] = None,
            deployments: Optional[Union[Dict[str, Union[Dict[str, str], str]], str]] = None
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
        subclass_location = self.get_subclass_file_path()
        caller_module = inspect.getmodule(inspect.stack()[1][0])
        caller_location = caller_module.__file__ if caller_module else None

        if specs_path:
            specs = ConfidentConfigSpecs.parse_file(specs_path)
            specs.specs_path = specs_path
        else:
            env_files = [env_files] if isinstance(env_files, str) else env_files or []
            config_files = [config_files] if isinstance(config_files, str) else config_files or []
            specs = ConfidentConfigSpecs(
                specs_path=specs_path, env_files=env_files, config_files=config_files,
                prefer_file=prefer_files, ignore_missing_files=ignore_missing_files,
                explicit_fields=fields, deployment_name=deployment_name, deployment_attr=deployment_attr,
                deployments=deployments, class_path=subclass_location, creation_path=caller_location
            )

        # Load properties from all sources.
        if specs.env_files:
            load_env_files(specs.env_files)
        env_vars_properties = self._load_env_properties()
        file_properties = self._load_file_properties(specs=specs)
        explicit_properties = self._load_explicit_properties(specs=specs)
        default_properties = self._load_default_properties(specs=specs)

        full_properties = self._merge_properties(
            specs=specs,
            explicit_properties=explicit_properties,
            env_vars_properties=env_vars_properties,
            file_properties=file_properties,
            default_properties=default_properties
        )

        deployment_properties = self._load_deployment_properties(specs=specs, properties=full_properties)
        full_properties = self._merge_env_default_properties(
            properties=full_properties, deployment_properties=deployment_properties
        )

        # Create the final object.
        object.__setattr__(self, SPECS_ATTR, specs)
        object.__setattr__(self, FULL_CONFIG_ATTR, full_properties)
        super().__init__(
            **{key: config_property.value for key, config_property in full_properties.items()}
        )

    @staticmethod
    def _merge_properties(
            specs, explicit_properties, env_vars_properties, file_properties, default_properties
    ) -> Dict[str, Any]:
        """
        Construct a dictionary with properties from all sources according to their priority.
        Args:
            specs: Config specifications object.
            explicit_properties: Fields that were given explicitly in the constructor.
            env_vars_properties: Fields retrieved from environment variables.
            file_properties: Fields retrieved from files.
            default_properties: Default values in the class declaration.

        Returns:
            Dictionary with all the properties together. Less important keys will be overridden by higher priority keys.
        """
        properties = {}
        if specs.prefer_files:
            properties.update({**default_properties, **explicit_properties, **env_vars_properties, **file_properties})
        else:
            properties.update({**default_properties, **explicit_properties, **file_properties, **env_vars_properties})
        return properties

    @staticmethod
    def _merge_env_default_properties(
            properties: Dict[str, ConfigProperty], deployment_properties: Dict[str, Any]
    ):
        for name, config_property in deployment_properties.items():
            if properties[name].source_type == ConfigSource.class_default:
                properties[name] = config_property
        return properties

    @staticmethod
    def _load_deployment_properties(specs: ConfidentConfigSpecs, properties: Dict[str, ConfigProperty]):
        """
        Loads the relevant deployment config properties.

        Args:
            specs: Config specifications object.
            properties: All loaded properties to find the deployment attribute in.
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
        if isinstance(deployments, str):
            deployment_location = deployments
            deployments = load_file(deployment_location)

        deployment = {}
        deployment_properties = {}

        if deployment_name:
            deployment = deployments.get(deployment_name)
        if deployment_attr:
            deployment_name = properties.get(deployment_attr).value
            if not isinstance(deployment_name, str):
                raise ValueError(f'deployment_attr: {deployment_attr} is not valid.')
            deployment = deployments.get(deployment_name)

        if isinstance(deployment, str):
            deployment = load_file(deployment)

        for name, value in deployment.items():
            deployment_properties[name] = ConfigProperty(
                name=name,
                value=value,
                source_name=deployment_name,
                source_type=ConfigSource.deployment,
                source_location=deployment_location,
            )

        return deployment_properties

    def _load_default_properties(self, specs: ConfidentConfigSpecs) -> Dict[str, ConfigProperty]:
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
                    source_name=self.__class__.__name__,
                    source_type=ConfigSource.class_default,
                    source_location=specs.class_path,
                )
        return default_properties

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
                    name=key, value=env_value, source_name=key, source_type=ConfigSource.env_var, source_location=key
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

            file_properties.update(
                {key: ConfigProperty(
                    name=key, value=value, source_name=os.path.basename(file_path),
                    source_type=ConfigSource.file, source_location=file_path
                ) for key, value in file_dict.items()})

        return {key: file_properties[key] for key in file_properties.keys() & self.__fields__.keys()}

    def get_subclass_file_path(self):
        try:
            return importlib.import_module(self.__module__).__file__
        except ImportError:
            return self.__module__

    def get_specs(self):
        return deepcopy(self.__getattribute__(SPECS_ATTR))

    def get_full_details(self):
        return deepcopy(self.__getattribute__(FULL_CONFIG_ATTR))
