import os
from typing import Union, List, Any, Dict

from pydantic import BaseModel
from pydantic.fields import ModelField

from confident.utils import load_config_file, load_env_files


class ConfidentConfigSpecs(BaseModel):
    specs_path: str = None
    env_files: Union[str, List[str]] = None
    config_files: Union[str, List[str]] = None
    prefer_files: bool = False
    ignore_missing_files: bool = True
    values: Dict['str', Any] = None


class Confident(BaseModel):
    __config_specs__: ConfidentConfigSpecs

    def __init__(
            self,
            specs_path: str = None,
            env_files: Union[str, List[str]] = None,
            config_files: Union[str, List[str]] = None,
            prefer_files: bool = False,
            ignore_missing_files: bool = True,
            values: Dict['str', Any] = None
    ):
        if specs_path:
            specs = ConfidentConfigSpecs.parse_file(specs_path)
            specs.specs_path = specs_path
        else:
            specs = ConfidentConfigSpecs(specs_path=specs_path, env_files=env_files, config_files=config_files,
                                         prefer_file=prefer_files, ignore_missing_files=ignore_missing_files,
                                         values=values)

        properties = {}
        if specs.env_files:
            load_env_files(specs.env_files)
        env_properties = self.load_env_properties()
        file_properties = self.load_file_properties(specs) if specs.config_files else {}

        # Adds config values by priority.
        if specs.prefer_files:
            properties.update({**env_properties, **file_properties})
        else:
            properties.update({**file_properties, **env_properties})

        # Adds explicit config values.
        if specs.values:
            properties.update(specs.values)

        super().__init__(ConfigSpecs=specs, **properties)

    def load_env_properties(self):
        env_properties = {}

        for key in self.__config_fields__.keys():
            env_value = os.getenv(key)
            if env_value:
                env_properties[key] = env_value
        return env_properties

    def load_file_properties(self, specs: ConfidentConfigSpecs):
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





