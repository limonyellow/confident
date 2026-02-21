import os
from typing import List

from confident import BaseConfig, MapField

CONFIG_MAP_FILE_PATH = os.path.abspath(
    os.path.join(__file__, os.path.pardir, "config_map.json")
)


class AppConfig(BaseConfig):
    env: str = MapField("local")
    host: str
    port: int
    log_level: str
    output_paths: List[str]


def main():
    config = AppConfig.from_map(CONFIG_MAP_FILE_PATH)
    print(f"{config=}")
    print(f"{config.model_dump()=}")
