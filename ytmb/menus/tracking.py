from pathlib import Path

from ytmb.ui import create_name_selector, create_playlist_selector
import ytmb.playlists as pl
import ytmb.utils as utils
from ytmb.exploration import Playlist


def get_audits_directory(name: str, playlist: Playlist) -> Path:
    p_all_audits = utils.get_data_directory(
        utils.get_config()['tracking']['audits_path']
    )
    p_audits = p_all_audits / name / playlist['title']
    if not p_audits.is_dir():
        p_audits.mkdir(parents=True)
    return p_audits

def tracking_flow():

    name_selector = create_name_selector()
    name = name_selector.user_choose()

    playlist_selector = create_playlist_selector(name)
    playlist = playlist_selector.user_choose()

    get_audits_directory(name, playlist)

    pl.get_tracks(playlist)
