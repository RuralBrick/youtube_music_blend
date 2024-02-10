import logging
from typing import TypedDict, Any
from enum import Enum, auto
import random

import ytmb.authentication as auth


class Playlist(TypedDict):
    playlistId: str
    title: str
    thumbnails: list
    count: int

type Track = Any

class SampleLimit(Enum):
    ALL = auto()
    SHORTEST_PLAYLIST = auto()

type SampleSize = SampleLimit | int

class SampleMethod(Enum):
    RANDOM = auto()
    IN_ORDER = auto()

class CombinationMethod(Enum):
    INTERLEAVED = auto()
    CONCATENATED = auto()
    SHUFFLED = auto()

def get_playlists(name) -> list[Playlist]:
    return auth.get_client(name).get_library_playlists(limit=None)

def get_tracks(name, playlist) -> list[Track]:
    return (auth.get_client(name)
                .get_playlist(playlist['playlistId'], limit=None)
                .get('tracks', []))

def add_tracks(name, playlist, tracks):
    videoIds = [t['videoId'] for t in tracks]
    auth.get_client(name).add_playlist_items(playlist['playlistId'], videoIds)

def remove_tracks(name, playlist, tracks):
    if tracks:
        (auth.get_client(name)
             .remove_playlist_items(playlist['playlistId'], tracks))

def clear_playlist(name, playlist):
    tracks = get_tracks(name, playlist)
    remove_tracks(name, playlist, tracks)

def combine_playlists(
        name,
        source_playlists,
        target_playlist,
        sample_size: SampleSize=SampleLimit.ALL,
        sample_method: SampleMethod=SampleMethod.IN_ORDER,
        combination_method: CombinationMethod=CombinationMethod.CONCATENATED,
):
    tracks = (get_tracks(p) for p in source_playlists)
    match sample_size:
        case SampleLimit.ALL:
            limit = None
        case SampleLimit.SHORTEST_PLAYLIST:
            limit = min(map(len, tracks))
        case int():
            limit = sample_size
    match sample_method:
        case SampleMethod.RANDOM:
            sampled_tracks = (
                random.sample(t, min(limit, len(t))) for t in tracks
            )
        case SampleMethod.IN_ORDER:
            sampled_tracks = (t[:limit] for t in tracks)
