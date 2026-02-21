from __future__ import annotations

import inspect
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List

from pydantic_settings import BaseSettings

from confident.config_field import ConfigField
from confident.config_source import ConfigSource
from confident.loader_manager import LoaderManager
from confident.loaders.default_source_loader import DefaultSourceLoader
from confident.loaders.env_source_loader import EnvSourceLoader
from confident.loaders.file_source_loader import FileSourceLoader
from confident.loaders.init_source_loader import InitSourceLoader
from confident.loaders.map_source_loader import MapSourceLoader
from confident.specs import ConfigSpecs
from confident.utils import get_class_file_path

SPECS_ATTR = "_specs"
LOADER_MANAGER_ATTR = "_loader_manager"


class BaseConfig(BaseSettings):
    __slots__ = (SPECS_ATTR, LOADER_MANAGER_ATTR)

    _confident_loader_manager_context_: LoaderManager  # type: ignore[assignment]
    _confident_specs_context_: ConfigSpecs  # type: ignore[assignment]

    def __init__(self, **values: Any) -> None:
        # Prepare metadata.
        subclass_location = get_class_file_path(cls=self)
        caller_module = inspect.getmodule(inspect.stack()[1][0])
        caller_location: str | Path = (
            caller_module.__file__
            if caller_module and caller_module.__file__
            else Path.cwd()
        )

        config_dict = self._get_confident_config_dict()

        specs = config_dict.get("specs")
        if not specs:
            specs_path = values.pop("_specs_path", None) or config_dict.get(
                "specs_path"
            )
            source_priority = values.pop("_source_priority", None)
            if specs_path:
                specs = ConfigSpecs.from_path(
                    path=specs_path,
                    class_path=subclass_location,
                    creation_path=caller_location,
                    source_priority=source_priority,
                )
            else:
                specs = ConfigSpecs.from_model(
                    model=self,
                    values=values,
                    class_path=subclass_location,
                    creation_path=caller_location,
                    source_priority=source_priority,
                )

        loader_manager = LoaderManager(
            settings_obj=self, source_priority=specs.source_priority
        )
        object.__setattr__(self, SPECS_ATTR, specs)
        object.__setattr__(self, LOADER_MANAGER_ATTR, loader_manager)

        # Create temporary context on the class for settings_customise_sources.
        self.__class__._confident_loader_manager_context_ = loader_manager
        self.__class__._confident_specs_context_ = specs

        super().__init__(**values)

        # Reset the context, so it will be clean for the next object creation.
        del self.__class__._confident_loader_manager_context_
        del self.__class__._confident_specs_context_

    @classmethod
    def _get_confident_config_dict(cls) -> dict:
        model_config = getattr(cls, "model_config", {})
        return {
            key: model_config[key]
            for key in (
                "files",
                "ignore_missing_files",
                "map_name",
                "map_field",
                "config_map",
                "source_priority",
                "specs",
                "specs_path",
            )
            if key in model_config
        }

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        # Get BaseSettings default loaders callables.
        loader_manager = cls._confident_loader_manager_context_
        specs = cls._confident_specs_context_
        loader_manager.init_settings_callable = init_settings
        loader_manager.env_settings_callable = env_settings
        loader_manager.file_secret_settings_callable = file_secret_settings

        # Add all the default loaders.
        loader_manager.loaders.extend(
            [
                InitSourceLoader(specs=specs, init_settings_callable=init_settings),
                EnvSourceLoader(specs=specs, env_settings_callable=env_settings),
                MapSourceLoader(
                    specs=specs, all_loaded_fields=loader_manager.all_loaded_fields
                ),
                FileSourceLoader(specs=specs),
                DefaultSourceLoader(specs=specs),
            ]
        )

        return loader_manager.load_all()

    @classmethod
    def from_files(
        cls, files, *, ignore_missing_files=None, source_priority=None, **values
    ):
        if files is not None:
            values["_files"] = files
        if ignore_missing_files is not None:
            values["_ignore_missing_files"] = ignore_missing_files
        if source_priority is not None:
            values["_source_priority"] = source_priority
        return cls(**values)

    @classmethod
    def from_map(
        cls,
        config_map,
        *,
        map_name=None,
        map_field=None,
        source_priority=None,
        **values,
    ):
        if config_map is not None:
            values["_config_map"] = config_map
        if map_name is not None:
            values["_map_name"] = map_name
        if map_field is not None:
            values["_map_field"] = map_field
        if source_priority is not None:
            values["_source_priority"] = source_priority
        return cls(**values)

    @classmethod
    def from_specs(cls, specs_path, *, source_priority=None, **values):
        if specs_path is not None:
            values["_specs_path"] = specs_path
        if source_priority is not None:
            values["_source_priority"] = source_priority
        return cls(**values)

    @classmethod
    def from_sources(
        cls,
        *,
        files: str | Path | List[str | Path] | None = None,
        ignore_missing_files: bool | None = None,
        config_map: str | Path | Dict[str, Any] | None = None,
        map_name: str | None = None,
        map_field: str | None = None,
        specs_path: str | Path | None = None,
        source_priority: List[ConfigSource] | None = None,
        **values: Any,
    ):
        if files is not None:
            values["_files"] = files
        if ignore_missing_files is not None:
            values["_ignore_missing_files"] = ignore_missing_files
        if config_map is not None:
            values["_config_map"] = config_map
        if map_name is not None:
            values["_map_name"] = map_name
        if map_field is not None:
            values["_map_field"] = map_field
        if specs_path is not None:
            values["_specs_path"] = specs_path
        if source_priority is not None:
            values["_source_priority"] = source_priority
        return cls(**values)

    @property
    def __specs__(self) -> ConfigSpecs:
        """
        Returns: The model specs.
        """
        specs: ConfigSpecs = object.__getattribute__(self, SPECS_ATTR)
        return specs

    def specs(self) -> ConfigSpecs:
        return deepcopy(self.__specs__)

    @property
    def __source_priority__(self) -> List[ConfigSource]:
        """
        Returns: List of sources from the highest priority to the lowest.
        """
        return self.__specs__.source_priority

    def source_priority(self) -> List[ConfigSource]:
        return deepcopy(self.__source_priority__)

    @property
    def __full_fields__(self) -> Dict[str, ConfigField]:
        """
        Returns: A dictionary with details of every field.
        """
        loader_manager: LoaderManager = object.__getattribute__(
            self, LOADER_MANAGER_ATTR
        )
        return loader_manager.full_fields

    def full_fields(self) -> Dict[str, ConfigField]:
        return deepcopy(self.__full_fields__)

    @property
    def __all_loaded_fields__(self) -> Dict[ConfigSource, Dict[str, ConfigField]]:
        """
        Returns: A dictionary with all the fields that were loaded before the prioritization classified by sources.
        """
        loader_manager: LoaderManager = object.__getattribute__(
            self, LOADER_MANAGER_ATTR
        )
        return loader_manager.all_loaded_fields

    def all_loaded_fields(self) -> Dict[ConfigSource, Dict[str, ConfigField]]:
        return deepcopy(self.__all_loaded_fields__)


class Confident(BaseConfig):
    pass
