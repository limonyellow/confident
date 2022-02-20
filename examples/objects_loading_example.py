import os
from typing import List, Dict

from pydantic import BaseModel

from confident import Confident


class UserModel(BaseModel):
    name: str
    last_name: str
    email: str


class AppConfig(Confident):
    title: str
    input_paths: List[str]
    timeout: int = 60
    users_mapping: Dict[str, UserModel]  # Loading dict\object to pydantic BaseModel will be made in the background.


if __name__ == '__main__':
    # Will load from both 'config.yaml' and 'users.yaml' config files.
    config_a = AppConfig(files=['config.yaml', 'users.yaml'])
    print(f'{config_a=}')

    # Will load from both 'config.yaml' and 'users.yaml' config files.
    # Environment variable will be loaded as json list:
    os.environ['input_paths'] = '["/tmp/input_a", "/tmp/input_b"]'
    # Environment variable will be loaded as json objects:
    os.environ['users_mapping'] = '{"mrOrange": {"name": "tim", "last_name": "ro", "email": "tim@mr.com"}}'

    config_b = AppConfig(files='config.yaml')
    print(f'{config_b=}')
