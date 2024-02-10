import logging
from pathlib import Path

import ytmusicapi
from ytmusicapi import YTMusic

from ytmb.utils import is_ok_filename, get_data_path, get_config


def get_headers_path() -> Path:
    p_headers = get_data_path() / get_config()['authentication']['header_path']
    if not p_headers.is_dir():
        p_headers.mkdir(parents=True)
    return p_headers

def name_to_path(name) -> Path:
    return get_headers_path() / f'{name}.json'

def is_existing_header(name) -> bool:
    return name_to_path(name).is_file()

def create_headers(name):
    """raises ValueError"""
    if not is_ok_filename(name):
        raise ValueError("Bad name")
    ytmusicapi.setup_oauth(name_to_path(name))

def get_header_names() -> list:
    return [p.stem for p in get_headers_path().iterdir()]

def get_client(name) -> YTMusic:
    return YTMusic(str(name_to_path(name).resolve()))
