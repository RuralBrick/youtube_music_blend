import logging
from typing import NotRequired, Optional
from collections.abc import Iterable
from enum import Enum
import random
from itertools import zip_longest, chain

import ytmb.authentication as auth
from ytmb.exploration import Playlist, Track


class PlaylistItem(Track):
    album: Optional[dict]
    likeStats: Optional[str]
    inLibrary: Optional[bool]
    isAvailable: bool
    isExplicit: bool
    videoType: str
    views: Optional[str]
    duration: NotRequired[str]
    duration_seconds: NotRequired[int]
    setVideoId: str
    feedbackTokens: NotRequired[dict]

class SampleLimit(Enum):
    ALL = 'all'
    SHORTEST_PLAYLIST = 'shortest_playlist'

type SampleSize = SampleLimit | int

class SampleMethod(Enum):
    RANDOM = 'random'
    IN_ORDER = 'in_order'

class CombinationMethod(Enum):
    INTERLEAVED = 'interleaved'
    CONCATENATED = 'concatenated'
    SHUFFLED = 'shuffled'

def get_playlists(name) -> list[Playlist]:
    try:
        return auth.get_client(name).get_library_playlists(limit=None)
    except Exception as e:
        logging.error(f"Could not get user playlists:\n{repr(e)}")
        return []

def serialize_playlist(playlist: Playlist) -> str:
    return playlist['playlistId']

def deserialize_playlist(name, str_playlist) -> Playlist:
    info = auth.get_client(name).get_playlist(str_playlist, limit=0)
    playlist: Playlist = {
        'title': info['title'],
        'playlistId': info['id'] or str_playlist,
        'thumbnails': info.get('thumbnails', []),
        'description': info['description'],
    }
    return playlist

def get_tracks(name, playlist) -> list[PlaylistItem]:
    try:
        return (auth.get_client(name)
                    .get_playlist(playlist['playlistId'], limit=None)
                    .get('tracks', []))
    except Exception as e:
        logging.error(f"Could not get playlist tracks:\n{repr(e)}")
        return []

def add_tracks(name, playlist, tracks):
    if tracks:
        videoIds = [t['videoId'] for t in tracks]
        logging.debug(f"{videoIds=}")
        resp = (
            auth.get_client(name)
                .add_playlist_items(
                    playlist['playlistId'],
                    videoIds=videoIds,
                    duplicates=True,
                )
        )
        logging.debug(f"{resp=}")

def remove_tracks(name, playlist, tracks):
    if tracks:
        resp = (auth.get_client(name)
                    .remove_playlist_items(playlist['playlistId'], tracks))
        logging.debug(f"{resp=}")

def clear_playlist(name, playlist):
    tracks = get_tracks(name, playlist)
    remove_tracks(name, playlist, tracks)

def overwrite_playlist(name, playlist, tracks):
    old_tracks = get_tracks(name, playlist)
    logging.debug(f"Found {len(old_tracks)} tracks")
    logging.debug(f"Adding {len(tracks)} tracks")
    add_tracks(name, playlist, tracks)
    logging.debug(f"Removing old tracks")
    remove_tracks(name, playlist, old_tracks)

def tracks_difference(minuend, subtrahend):
    subtrahend_videoId = {t['videoId'] for t in subtrahend}
    return [t for t in minuend if t['videoId'] not in subtrahend_videoId]

def update_playlist(name, playlist, tracks):
    existing_tracks = get_tracks(name, playlist)
    logging.debug(f"Found {len(existing_tracks)} tracks")
    new_tracks = tracks_difference(tracks, existing_tracks)
    logging.debug(f"Adding {len(new_tracks)} new tracks")
    add_tracks(name, playlist, new_tracks)
    retired_tracks = tracks_difference(existing_tracks, tracks)
    logging.debug(f"Removing {len(retired_tracks)} old tracks")
    remove_tracks(name, playlist, retired_tracks)

def combine_tracks(
        tracks: Iterable[Iterable[Track]],
        sample_size: SampleSize=SampleLimit.ALL,
        sample_method: SampleMethod=SampleMethod.IN_ORDER,
        combination_method: CombinationMethod=CombinationMethod.CONCATENATED,
) -> list[Track]:
    match sample_size:
        case SampleLimit.ALL:
            limit = None
        case SampleLimit.SHORTEST_PLAYLIST:
            limit = min(map(len, tracks))
        case int():
            limit = sample_size
    match sample_method:
        case SampleMethod.RANDOM:
            sampled_tracks = [
                random.sample(t, min(limit, len(t))) for t in tracks
            ]
        case SampleMethod.IN_ORDER:
            sampled_tracks = [t[:limit] for t in tracks]
    match combination_method:
        case CombinationMethod.INTERLEAVED:
            combined_tracks = [
                t
                for t in chain.from_iterable(zip_longest(*sampled_tracks))
                if t
            ]
        case CombinationMethod.CONCATENATED:
            combined_tracks = list(chain.from_iterable(sampled_tracks))
        case CombinationMethod.SHUFFLED:
            combined_tracks = list(chain.from_iterable(sampled_tracks))
            random.shuffle(combined_tracks)
    return combined_tracks

def combine_playlists(
        name,
        source_playlists,
        target_playlist,
        sample_size: SampleSize=SampleLimit.ALL,
        sample_method: SampleMethod=SampleMethod.IN_ORDER,
        combination_method: CombinationMethod=CombinationMethod.CONCATENATED,
):
    logging.info("Getting tracks")
    tracks = [get_tracks(name, p) for p in source_playlists]
    logging.debug(
        ", ".join(
            f"{p['title']} -- {len(t)} tracks"
            for p, t in zip(source_playlists, tracks)
        )
    )
    combined_tracks = combine_tracks(
        tracks,
        sample_size,
        sample_method,
        combination_method,
    )
    logging.info("Adding tracks to target playlist")
    overwrite_playlist(name, target_playlist, combined_tracks)
