import logging

import ytmusicapi

from ytmb.utils import is_ok_filename, get_data_path, get_config


def create_headers(name):
    """raises ValueError"""
    if not is_ok_filename(name):
        raise ValueError("Bad name")
    p_headers = get_data_path() / get_config()['authentication']['header_path']
    ytmusicapi.setup_oauth(p_headers / f'{name}.json')
