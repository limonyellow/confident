import os
from typing import List, Dict

from pydantic import BaseModel

from confident import Confident

CONFIG_FILE_PATH = os.path.abspath(os.path.join(__file__, os.path.pardir, 'config.yaml'))
USERS_FILE_PATH = os.path.abspath(os.path.join(__file__, os.path.pardir, 'users.yaml'))


class UserModel(BaseModel):
    name: str
    last_name: str
    email: str


class AppConfig(Confident):
    title: str
    input_paths: List[str]
    timeout: int = 60
    users_mapping: Dict[str, UserModel]  # Loading dict\object to pydantic BaseModel will be made in the background.


def main():
    # Will load from both 'config.yaml' and 'users.yaml' config files.
    config_a = AppConfig(_files=[CONFIG_FILE_PATH, USERS_FILE_PATH])
    print(f'{config_a=}')

    # Will load from both 'config.yaml' and 'users.yaml' config files.
    # Environment variable will be loaded as json list:
    os.environ['input_paths'] = '["/tmp/input_a", "/tmp/input_b"]'
    # Environment variable will be loaded as json objects:
    os.environ['users_mapping'] = '{"mrOrange": {"name": "tim", "last_name": "ro", "email": "tim@mr.com"}}'

    config_b = AppConfig(_files=CONFIG_FILE_PATH)
    print(f'{config_b=}')


if __name__ == '__main__':
    main()
