import logging
from typing import TypedDict
import __main__
from pathlib import Path
import re

import yaml


class AuthenticationConfig(TypedDict):
    header_path: str

class Config(TypedDict):
    data_path: str
    authentication: AuthenticationConfig

def get_config() -> Config:
    p_main = Path(__main__.__file__)
    p_config = p_main.parent / 'config.yml'
    with open(p_config) as f:
        dict_config = yaml.safe_load(f)
    dict_config['data_path'] = __main__.__file__
    return dict_config

def get_data_path() -> Path:
    return Path(get_config()['data_path'])

def is_ok_filename(name) -> bool:
    
