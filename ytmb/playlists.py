import logging
from typing import TypedDict, NotRequired, Optional
from enum import Enum, auto
import random
from itertools import zip_longest, chain

import ytmb.authentication as auth
from ytmb.exploration import Playlist, Track


class PlaylistItem(TypedDict):
    videoId: str
    title: str
    artists: list
    album: Optional[dict]
    likeStats: Optional[str]
    inLibrary: Optional[bool]
    thumbnails: list
    isAvailable: bool
    isExplicit: bool
    videoType: str
    views: Optional[str]
    duration: NotRequired[str]
    duration_seconds: NotRequired[int]
    setVideoId: str
    feedbackTokens: NotRequired[dict]

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

def get_tracks(name, playlist) -> list[PlaylistItem]:
    return (auth.get_client(name)
                .get_playlist(playlist['playlistId'], limit=None)
                .get('tracks', []))

def add_tracks(name, playlist, tracks):
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
    logging.info("Adding tracks to target playlist")
    overwrite_playlist(name, target_playlist, combined_tracks)
