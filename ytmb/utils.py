import logging
from typing import TypedDict
from pathlib import Path
import re

import yaml


global_settings = {
    'debug': False,
}

class UiConfig(TypedDict):
    menu_limit: int

class AuthenticationConfig(TypedDict):
    header_path: str

class FilteringConfig(TypedDict):
    blacklist_path: str
    whitelist_path: str

class BlendConfig(TypedDict):
    default_length: int
    filtering: FilteringConfig

class TrackingConfig(TypedDict):
    audits_path: str

class AutomationConfig(TypedDict):
    routines_path: str

class Config(TypedDict):
    data_path: str
    ui: UiConfig
    authentication: AuthenticationConfig
    blend: BlendConfig
    tracking: TrackingConfig
    automation: AutomationConfig

def get_config() -> Config:
    p_root = Path(__file__).parent
    p_config = p_root / 'config.yml'
    with open(p_config) as f:
        dict_config = yaml.safe_load(f)
    if 'data_path' not in dict_config:
        dict_config['data_path'] = f'{p_root}/data'
    return dict_config

def get_data_path() -> Path:
    return Path(get_config()['data_path'])

def get_data_directory(name) -> Path:
    p_dir: Path = get_data_path() / name
    if not p_dir.is_dir():
        p_dir.mkdir(parents=True)
    return p_dir

def is_ok_filename(name) -> bool:
    return bool(re.fullmatch(r'[A-Za-z0-9_\-]+', name))
