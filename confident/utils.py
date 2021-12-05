import json
import os
from typing import Any, Dict, List

import yaml
from dotenv import load_dotenv


def load_config_file(path: str) -> Dict[str, Any]:
    filename, file_extension = os.path.splitext(path)

    if not os.path.isfile(path):
        raise ValueError(f'{path=} is not exists.')

    if file_extension == '.json':
        with open(path, mode='r') as file:
            return json.load(file)

    if file_extension == '.yaml':
        with open(path, mode='r') as file:
            return yaml.safe_load(file)

    raise ValueError(f'{path=} is not a supported file.')


def load_env_files(paths: List[str]) -> None:
    for path in paths:
        load_dotenv(path)
