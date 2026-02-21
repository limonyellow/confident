from __future__ import annotations

from pathlib import Path
from typing import Any, List

from pydantic import BaseModel

from confident.config_source import ConfigSource
from confident.map_field import MAP_FIELD_FLAG

IGNORE_MISSING_FILES_DEFAULT = True
DEFAULT_SOURCE_PRIORITY = [
    ConfigSource.init,
    ConfigSource.env_var,
    ConfigSource.map,
    ConfigSource.file,
    ConfigSource.class_default,
]


class ConfigSpecs(BaseModel):
    """
    A model that holds all the metadata regarding the Confident config object.
    """

    specs_path: Path | None = None
    files: List[Path] = []
    ignore_missing_files: bool = IGNORE_MISSING_FILES_DEFAULT
    map_name: str | None = None
    map_field: str | None = None
    config_map: Path | dict | None = None
    class_path: Path | None = None
    creation_path: Path | None = None
    source_priority: List[ConfigSource] = DEFAULT_SOURCE_PRIORITY

    @classmethod
    def from_path(
        cls,
        path: Path | str,
        class_path: str | Path | None = None,
        creation_path: str | Path | None = None,
    ) -> ConfigSpecs:
        obj = cls.model_validate_json(Path(path).read_text())
        obj.specs_path = Path(path)
        obj.class_path = Path(class_path) if class_path else obj.class_path
        obj.creation_path = Path(creation_path) if creation_path else obj.creation_path
        return obj

    @classmethod
    def from_model(cls, model, values, class_path=None, creation_path=None):
        model_config = {
            key: getattr(model, "model_config", {})[key]
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
            if key in getattr(model, "model_config", {})
        }

        map_field = cls._find_map_field(
            model=model,
            explicit_map_field=values.pop("_map_field", None)
            or model_config.get("map_field"),
        )

        files = values.pop("_files", None) or model_config.get("files")
        files = [files] if isinstance(files, str) else files or []

        ignore_missing_files = values.pop("_ignore_missing_files", None)
        ignore_missing_files = (
            ignore_missing_files
            if ignore_missing_files is not None
            else model_config.get("ignore_missing_files", IGNORE_MISSING_FILES_DEFAULT)
        )

        obj = cls(
            specs_path=values.pop("_specs_path", None),
            files=files,
            ignore_missing_files=ignore_missing_files,
            map_name=values.pop("_map_name", None) or model_config.get("map_name"),
            map_field=map_field,
            config_map=values.pop("_config_map", None)
            or model_config.get("config_map"),
            class_path=class_path,
            creation_path=creation_path,
            source_priority=(
                values.pop("_source_priority", None)
                or model_config.get("source_priority")
                or DEFAULT_SOURCE_PRIORITY
            ),
        )
        return obj

    @staticmethod
    def _find_map_field(model: Any, explicit_map_field: str | None) -> str | None:
        """
        Searches if one of the fields declared in the subclass has marked as the deployment field.
        Args:
            explicit_map_field: The deployment field received as argument.

        Returns:
            A single deployment field. None if no field provided in any way.

        Raises:
            ValueError - If more than one deployment fields is received.
        """
        properties_marked_as_map_field: list[str] = [
            name
            for name, model_field in type(model).model_fields.items()
            if (model_field.json_schema_extra or {}).get(MAP_FIELD_FLAG)
        ]
        if not properties_marked_as_map_field:
            return explicit_map_field
        if explicit_map_field and properties_marked_as_map_field:
            raise ValueError(
                f"Cannot have both explicit `_map_field` and also `MapField()` "
                f"in {model.__class__.__name__} declaration"
            )
        if len(properties_marked_as_map_field) > 1:
            raise ValueError(
                f"Cannot have more then one `MapField()` in {model.__class__.__name__} declaration"
            )
        return properties_marked_as_map_field[0]
