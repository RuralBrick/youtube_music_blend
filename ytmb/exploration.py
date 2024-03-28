import logging
from typing import TypedDict, NotRequired, Optional
from pathlib import Path
from itertools import repeat, zip_longest

from ytmb.utils import get_config, get_data_path
import ytmb.authentication as auth
import ytmb.playlists as pl


class Track(TypedDict):
    videoId: str
    title: str
    thumbnails: list
    artists: list

class Song(Track):
    playlistId: NotRequired[str]
    isExplicit: NotRequired[bool]
    views: NotRequired[str]

class Playlist(TypedDict):
    title: str
    playlistId: str
    thumbnails: list
    description: str
    count: NotRequired[int]
    author: NotRequired[list]

class Radio(TypedDict):
    title: str
    playlistId: str
    thumbnails: list
    description: str

class Album(TypedDict):
    title: str
    type: str
    year: str
    artists: list
    browseId: str
    audioPlaylistId: Optional[str]
    thumbnails: list
    isExplicit: bool

class Artist(TypedDict):
    title: str
    browseId: str
    subscribers: str
    thumbnails: list

type Listing = Song | Playlist | Radio | Album | Artist

class HomeSection(TypedDict):
    title: str
    contents: list[Listing]

def get_whitelist_path() -> Path:
    whitelist_path = get_config()['blend']['filtering']['whitelist_path']
    p_whitelists = get_data_path() / whitelist_path
    if not p_whitelists.is_dir():
        p_whitelists.mkdir(parents=True)
    return p_whitelists

def get_blacklist_path() -> Path:
    blacklist_path = get_config()['blend']['filtering']['blacklist_path']
    p_blacklists = get_data_path() / blacklist_path
    if not p_blacklists.is_dir():
        p_blacklists.mkdir(parents=True)
    return p_blacklists

def get_whitelist(name) -> Optional[set]:
    p_whitelist = get_whitelist_path() / f'{name}.txt'
    if not p_whitelist.is_file():
        return None
    with open(p_whitelist) as f:
        return {l for l in f.read().split('\n') if l}

def get_blacklist(name) -> Optional[set]:
    p_blacklist = get_blacklist_path() / f'{name}.txt'
    if not p_blacklist.is_file():
        return None
    with open(p_blacklist) as f:
        return {l for l in f.read().split('\n') if l}

def get_home(name) -> list[HomeSection]:
    resp = auth.get_client().get_home(limit=float('inf'))
    logging.debug(f"Found {len(resp)} home sections for {name}")
    return resp

def sample_home(name, k) -> list[Track]:
    pass

def create_blend(name, source_names, target_playlist):
    blend_length = get_config()['blend']['default_length']
    num_per_user, padding = divmod(blend_length, len(source_names))
    tracks = [
        sample_home(user, num_per_user + num_extra) for user, num_extra
        in zip_longest(source_names, repeat(1, padding), fillvalue=0)
    ]
    all_tracks = pl.combine_tracks(
        tracks,
        pl.SampleLimit.ALL,
        pl.SampleMethod.IN_ORDER,
        pl.CombinationMethod.INTERLEAVED,
    )
    pl.overwrite_playlist(name, target_playlist, all_tracks)
