from typing import TypedDict, NotRequired, Optional
from itertools import repeat, zip_longest

from ytmb.utils import get_config
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
