import logging
from typing import TypedDict, Any

import ytmb.authentication as auth


class Playlist(TypedDict):
    playlistId: str
    title: str
    thumbnails: list
    count: int

Track = Any

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
    auth.get_client(name).remove_playlist_items(playlist['playlistId'], tracks)
