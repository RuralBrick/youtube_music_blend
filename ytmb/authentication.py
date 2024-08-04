import logging
from pathlib import Path
from functools import cache

import ytmusicapi
from ytmusicapi import YTMusic

from ytmb.utils import is_ok_filename, get_data_directory, get_config


def get_headers_path() -> Path:
    return get_data_directory(get_config()['authentication']['header_path'])

def name_to_path(name) -> Path:
    return get_headers_path() / f'{name}.json'

def is_existing_header(name) -> bool:
    return name_to_path(name).is_file()

def create_headers(name):
    """raises ValueError"""
    if not is_ok_filename(name):
        raise ValueError("Bad name")
    ytmusicapi.setup_oauth(name_to_path(name))

def delete_headers(name):
    """raises ValueError"""
    if not is_existing_header(name):
        raise ValueError("Name not found")
    name_to_path(name).unlink()

def get_header_names() -> list:
    return [p.stem for p in get_headers_path().iterdir()]

@cache
def get_client(name) -> YTMusic:
    return YTMusic(str(name_to_path(name).resolve()))
