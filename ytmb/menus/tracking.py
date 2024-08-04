from typing import TypedDict
from pathlib import Path
from datetime import date

from ytmb.ui import create_name_selector, create_playlist_selector
import ytmb.playlists as pl
from ytmb.utils import get_config, get_data_directory
from ytmb.exploration import Playlist


class TrackingParameters(TypedDict):
    name: str
    playlist: str

def get_audits_directory(name: str, playlist: Playlist) -> Path:
    p_all_audits = get_data_directory(get_config()['tracking']['audits_path'])
    p_audits = p_all_audits / name / playlist['title']
    if not p_audits.is_dir():
        p_audits.mkdir(parents=True)
    return p_audits

def tracking_args() -> TrackingParameters:
    name_selector = create_name_selector()
    name = name_selector.user_choose()

    playlist_selector = create_playlist_selector(name)
    playlist = playlist_selector.user_choose()

    args: TrackingParameters = {
        'name': name,
        'playlist': pl.serialize_playlist(playlist),
    }
    return args

def process_tracking(args: TrackingParameters):
    # HACK

    # TODO: Make process more structured/automated

    p_playlist_audits = get_audits_directory(
        args['name'],
        pl.deserialize_playlist(args['name'], args['playlist'])
    )
    audit_name = date.today().strftime('%y-%m-%d.txt')

    with open(p_playlist_audits / audit_name, 'w', encoding='utf-8') as f:
        f.writelines(
            t['title'] + '\n' for t in pl.get_tracks(
                args['name'],
                pl.deserialize_playlist(args['name'], args['playlist'])
            )
        )

    # end HACK

def tracking_flow():
    args = tracking_args()
    process_tracking(args)
    print("Done.")
