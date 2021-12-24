import os
from typing import Union, List, Any, Dict, Optional

from pydantic import BaseModel
from pydantic.fields import ModelField

from confident.utils import load_config_file, load_env_files


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
    __config_specs__: ConfidentConfigSpecs

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
        if specs_path:
            specs = ConfidentConfigSpecs.parse_file(specs_path)
            specs.specs_path = specs_path
        else:
            env_files = [env_files] if isinstance(env_files, str) else env_files or []
            config_files = [config_files] if isinstance(config_files, str) else config_files or []
            specs = ConfidentConfigSpecs(specs_path=specs_path, env_files=env_files, config_files=config_files,
                                         prefer_file=prefer_files, ignore_missing_files=ignore_missing_files,
                                         explicit_fields=fields)

        if specs.env_files:
            load_env_files(specs.env_files)
        env_properties = self._load_env_properties()
        file_properties = self._load_file_properties(specs) if specs.config_files else {}

        # Adds explicit config fields.
        explicit_properties = specs.explicit_fields if specs.explicit_fields else {}

        properties = self._merge_properties(specs=specs, explicit_properties=explicit_properties,
                                            env_properties=env_properties, file_properties=file_properties)

        super().__init__(ConfigSpecs=specs, **properties)

    @staticmethod
    def _merge_properties(specs, explicit_properties, env_properties, file_properties) -> Dict['str', Any]:
        """
        Construct a dictionary with properties from all sources according to their priority.
        Args:
            specs: Config specifications object.
            explicit_properties: Fields that were given explicitly in the constructor.
            env_properties: Fields retrieved from environment variables.
            file_properties: Fields retrieved from files.

        Returns:
            Dictionary with all the properties together. Less important keys will be overridden by higher priority keys.
        """
        properties = {}
        if specs.prefer_files:
            properties.update({**explicit_properties, **env_properties, **file_properties})
        else:
            properties.update({**explicit_properties, **file_properties, **env_properties})
        return properties

    def _load_env_properties(self) -> Dict[str, Any]:
        """
        Finds and loads requested config fields from environment variables into a dictionary.
        """
        env_properties = {}

        for key in self.__config_fields__.keys():
            env_value = os.getenv(key)
            if env_value:
                env_properties[key] = env_value
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
            file_properties.update(file_dict)

        return {key: file_properties[key] for key in file_properties.keys() & self.__fields__.keys()}

    @property
    def __metadata_fields__(self) -> Dict[str, ModelField]:
        return Confident.__fields__

    @property
    def __config_fields__(self) -> Dict[str, ModelField]:
        return {key: value for key, value in self.__fields__.items() if key not in self.__metadata_fields__}
