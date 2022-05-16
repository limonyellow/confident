import os
from typing import List

from confident import BaseConfig, MapField


class ServerConfig(BaseConfig):
    environment: str = MapField(default='local')
    host: str
    port: int
    api_endpoint: str = '/api'
    log_level: str = 'debug'
    output_paths: List[str] = ['S3://bucket_local']

    class Config:
        config_map = os.path.abspath(os.path.join(__file__, os.path.pardir, 'config_map.json'))


def main():
    # Will load deployment='local'
    config_a = ServerConfig()
    print(f'{config_a=}')

    # Will load deployment='prod'
    os.environ['environment'] = 'prod'  # Simulating setting environment variable deployment=prod
    config_b = ServerConfig()
    print(f'{config_b=}')

    # Will load deployment='dev'
    config_c = ServerConfig(environment='dev')
    print(f'{config_c=}')


if __name__ == '__main__':
    main()

