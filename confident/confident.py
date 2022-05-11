import inspect
from copy import deepcopy
from pathlib import Path
from typing import Tuple, Any, Dict, List

from pydantic import BaseSettings
from pydantic.env_settings import SettingsSourceCallable

from confident.config_property import ConfigProperty
from confident.config_source import ConfigSource
from confident.loader_manager import LoaderManager
from confident.loaders.default_source_loader import DefaultSourceLoader
from confident.loaders.env_source_loader import EnvSourceLoader
from confident.loaders.file_source_loader import FileSourceLoader
from confident.loaders.init_source_loader import InitSourceLoader
from confident.loaders.map_source_loader import MapSourceLoader
from confident.specs import SettingsSpecs
from confident.utils import get_class_file_path


class Confident(BaseSettings):
    def __init__(self, **values: Any):
        # Prepare metadata.
        subclass_location = get_class_file_path(cls=self)
        caller_module = inspect.getmodule(inspect.stack()[1][0])
        caller_location = caller_module.__file__ if caller_module else Path.cwd()

        if not self.__config__._specs:
            specs_path = values.pop('_specs_path', None) or self.Config.__dict__.get('specs_path')
            if specs_path:
                self.__config__._specs = SettingsSpecs.from_path(
                    path=specs_path, class_path=subclass_location, creation_path=caller_location
                )
            else:
                self.__config__._specs = SettingsSpecs.from_model(
                    model=self, values=values, class_path=subclass_location, creation_path=caller_location
                )

        self.__config__._loader_manager = LoaderManager(
            settings_obj=self, source_priority=self.__config__._specs.source_priority
        )
        super().__init__(**values)

    def _build_values(self, init_kwargs: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        values_dict = super()._build_values(init_kwargs, **kwargs)
        self.__config__._loader_manager.full_fields = values_dict
        return {name: field.value for name, field in values_dict.items()}

    class Config:
        _loader_manager = None
        _specs = None

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            # Get BaseSettings default loaders callables.
            cls._loader_manager.init_settings_callable = init_settings
            cls._loader_manager.env_settings_callable = env_settings
            cls._loader_manager.file_secret_settings_callable = file_secret_settings

            # Add all the default loaders.
            cls._loader_manager.loaders.extend([
                InitSourceLoader(specs=cls._specs, init_settings_callable=init_settings),
                EnvSourceLoader(specs=cls._specs, env_settings_callable=env_settings),
                MapSourceLoader(specs=cls._specs, all_loaded_fields=cls._loader_manager.all_loaded_fields),
                FileSourceLoader(specs=cls._specs),
                DefaultSourceLoader(specs=cls._specs)
            ])

            return cls._loader_manager.load_all()

    def specs(self) -> SettingsSpecs:
        """
        Returns: A deep copy of the settings class specs.
        """
        return deepcopy(self.__config__._specs)

    def full_fields(self) -> Dict[str, Any]:
        """
        Returns: A dictionary with details of every field.
        """
        return deepcopy(self.__config__._loader_manager.full_fields)

    def all_loaded_fields(self) -> Dict[str, List[ConfigProperty]]:
        """
        Returns: A dictionary with details of every field.
        """
        return deepcopy(self.__config__._loader_manager.all_loaded_fields)

    def source_priority(self) -> List[ConfigSource]:
        """
        Returns: List of sources from the highest priority to the lowest.
        """
        return deepcopy(self.__config__._specs.source_priority)
