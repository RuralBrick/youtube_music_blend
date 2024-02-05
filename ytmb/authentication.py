import logging

import ytmusicapi

from ytmb.utils import get_data_path, get_config


def create_headers(name):
    p_headers = get_data_path() / get_config()['authentication']['header_path']
    ytmusicapi.setup_oauth(p_headers / f'{name}.')
    logging.debug(p_headers)
