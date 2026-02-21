import os
from typing import List

from confident import BaseConfig, MapField

CONFIG_FILE_PATH = os.path.abspath(
    os.path.join(__file__, os.path.pardir, "config.yaml")
)
CONFIG_MAP_FILE_PATH = os.path.abspath(
    os.path.join(__file__, os.path.pardir, "config_map.json")
)


class AppConfig(BaseConfig):
    env: str = MapField("local")
    title: str
    host: str
    port: int
    log_level: str
    output_paths: List[str]


def main():
    # Load from a file and a config map in a single typed call.
    config = AppConfig.from_sources(
        files=CONFIG_FILE_PATH,
        config_map=CONFIG_MAP_FILE_PATH,
    )
    print(f"{config=}")
    print(f"{config.model_dump()=}")


main()
