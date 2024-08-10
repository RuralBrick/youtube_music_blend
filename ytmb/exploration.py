import logging
from typing import TypedDict, NotRequired, Optional, NamedTuple
from pathlib import Path
from collections import defaultdict
from functools import partial
import random
from itertools import repeat, zip_longest

from ytmb.utils import get_config, get_data_directory
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
    return get_data_directory(
        get_config()['blend']['filtering']['whitelist_path']
    )

def get_blacklist_path() -> Path:
    return get_data_directory(
        get_config()['blend']['filtering']['blacklist_path']
    )

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
    resp = auth.get_client(name).get_home(limit=float('inf'))
    logging.debug(f"Found {len(resp)} home sections for {name}")
    return resp

def get_radio_tracks(name, radio):
    try:
        return (auth.get_client(name)
                    .get_watch_playlist(playlistId=radio['playlistId'])
                    .get('tracks', []))
    except Exception as e:
        logging.error(f"Could not get radio tracks:\n{repr(e)}")
        return []

def get_album_tracks(name, album):
    try:
        return (auth.get_client(name)
                    .get_album(album['browseId'])
                    .get('tracks', []))
    except Exception as e:
        logging.error(f"Could not get album tracks:\n{repr(e)}")
        return []

def get_artist_tracks(name, artist):
    try:
        return (auth.get_client(name)
                    .get_artist(artist['browseId'])
                    .get('songs', {})
                    .get('results', []))
    except Exception as e:
        logging.error(f"Could not get artist tracks:\n{repr(e)}")
        return []

class LabeledListing(NamedTuple):
    listing: Listing
    section: HomeSection

class HomeSampler:
    def __init__(self, name) -> None:
        self.name = name
        self.home = get_home(name)
        if whitelist := get_whitelist(name):
            self.home = [hs for hs in self.home if hs['title'] in whitelist]
            msg = (f"Sections found from {name}'s whitelist: "
                   + ", ".join(hs['title'] for hs in self.home))
            logging.debug(msg)
        elif blacklist := get_blacklist(name):
            self.home = [hs for hs in self.home if hs['title'] not in blacklist]
            msg = (f"Remaining sections not on {name}'s blacklist: "
                   + ", ".join(hs['title'] for hs in self.home))
            logging.debug(msg)
        self.all_listings = [
            LabeledListing(l, hs) for hs in self.home for l in hs['contents']
        ]
        self.selections = defaultdict(partial(defaultdict, set))

    def empty(self) -> bool:
        return len(self.all_listings) == 0

    def sample(self) -> Optional[Track]:
        listing, section = self.all_listings.pop(
            random.randrange(len(self.all_listings))
        )
        match listing:
            case {'videoId': _}:
                logging.debug(f"Found song {listing['title']}")
                self.selections[section['title']]['Songs'].add(listing['title'])
                return listing
            case {'playlistId': _, 'count': _}:
                playlist = pl.get_tracks(self.name, listing)
                msg = (f"Found {len(playlist)} tracks in playlist "
                       f"{listing['title']}")
                logging.debug(msg)
                try:
                    track = random.choice(playlist)
                except IndexError:
                    return None
                self.selections[section['title']][listing['title']].add(
                    track['title']
                )
                return track
            case {'playlistId': _}:
                radio = get_radio_tracks(self.name, listing)
                msg = (f"Choosing from {len(radio)} tracks from radio "
                       f"{listing['title']}")
                logging.debug(msg)
                try:
                    track = random.choice(radio)
                except IndexError:
                    return None
                self.selections[section['title']][listing['title']].add(
                    track['title']
                )
                return track
            case {'type': _}:
                album = get_album_tracks(self.name, listing)
                msg = f"Found {len(album)} tracks in album {listing['title']}"
                logging.debug(msg)
                try:
                    track = random.choice(album)
                except IndexError:
                    return None
                self.selections[section['title']][listing['title']].add(
                    track['title']
                )
                return track
            case {'subscribers': _}:
                artist = get_artist_tracks(self.name, listing)
                msg = f"Found {len(artist)} tracks by artist {listing['title']}"
                logging.debug(msg)
                try:
                    track = random.choice(artist)
                except IndexError:
                    return None
                self.selections[section['title']][listing['title']].add(
                    track['title']
                )
                return track
            case _:
                msg = f"Listing not matched:\n{listing}\nSection:\n{section}"
                logging.warn(msg)
                return None

    def _format_collection(self, tracks) -> str:
        return '\n'.join(f'\t\t{track}' for track in tracks)

    def _format_section(self, collections) -> str:
        return '\n'.join(
            f'\t{collection}\n{self._format_collection(tracks)}'
            for collection, tracks in sorted(collections.items())
        )

    def format_selections(self) -> str:
        return '\n'.join(
            f'{section}\n{self._format_section(collections)}'
            for section, collections in sorted(self.selections.items())
        )

def sample_home(name, k) -> list[Track]:
    sampler = HomeSampler(name)
    tracks = []
    while not sampler.empty() and len(tracks) < k:
        track = sampler.sample()
        if track:
            tracks.append(track)
    if len(tracks) != k:
        msg = (f"Could not sample enough tracks from {name}'s home. Missing "
               f"{k - len(tracks)} tracks.")
        logging.warn(msg)
    logging.info(f"{name}'s selections:\n{sampler.format_selections()}")
    return tracks

def create_blend(
        name,
        source_names,
        target_playlist,
        blend_length=get_config()['blend']['default_length'],
):
    num_per_user, padding = divmod(blend_length, len(source_names))
    logging.debug(
        f"Creating blend with {num_per_user} tracks per user and {padding} "
        "padding"
    )
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
