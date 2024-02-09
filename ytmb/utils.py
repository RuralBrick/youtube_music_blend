import logging
from typing import TypedDict
from pathlib import Path
import re

import yaml


class UiConfig(TypedDict):
    menu_limit: int

class AuthenticationConfig(TypedDict):
    header_path: str

class Config(TypedDict):
    data_path: str
    ui: UiConfig
    authentication: AuthenticationConfig

def get_config() -> Config:
    p_root = Path(__file__).parent
    p_config = p_root / 'config.yml'
    with open(p_config) as f:
        dict_config = yaml.safe_load(f)
    dict_config['data_path'] = str(p_root)
    return dict_config

def get_data_path() -> Path:
    return Path(get_config()['data_path'])

def is_ok_filename(name) -> bool:
    return bool(re.fullmatch(r'[A-Za-z0-9_\-]+', name))
