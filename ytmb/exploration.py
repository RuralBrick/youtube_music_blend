from typing import TypedDict, NotRequired, Optional


class Track(TypedDict):
    title: str
    videoId: str
    playlistId: NotRequired[str]
    thumbnails: list
    artists: list
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

type Listing = Track | Playlist | Radio | Album | Artist

class HomeSection(TypedDict):
    title: str
    contents: list[Listing]



def create_blend(name, source_names, target_playlist):
    pass
