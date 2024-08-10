import logging
import warnings
from enum import StrEnum
from typing import TypedDict

from ytmb.ui import (
    create_name_selector,
    create_playlist_selector,
    Selector,
    Choice,
)
import ytmb.playlists as pl


class PlaylistWriteMethod(StrEnum):
    UPDATE = 'update'
    OVERWRITE = 'overwrite'

class AdvancedParameters(TypedDict):
    name: str
    source_playlists: list[str]
    target_playlist: str
    sample_size: str | int
    sample_method: str
    combination_method: str
    write_method: str

def advanced_args() -> AdvancedParameters:
    name_selector = create_name_selector()
    source_playlists = []
    print("Adding source playlists.")
    while True:
        name = name_selector.user_choose()
        playlist_selector = create_playlist_selector(name)
        source_playlists.append(playlist_selector.user_choose())
        titles = '\n'.join(f"- {p['title']}" for p in source_playlists)
        print(f"Current source playlists:\n{titles}")
        prompt = "Add another playlist? (y/n) "
        while (add_another := input(prompt)) not in {'y', 'n'}:
            print("Please enter 'y' or 'n'.")
        if add_another == 'n':
            break
    print("Choosing target playlist.")
    name = name_selector.user_choose()
    playlist_selector = create_playlist_selector(name)
    target_playlist = playlist_selector.user_choose()
    print(f"Target playlist: {target_playlist['title']}")
    sample_size_choices = {'1': Choice(None, "Number")} | {
        str(i+2): Choice(m.value, m.name.replace('_', ' ').title())
        for i, m in enumerate(pl.SampleLimit)
    }
    sample_size = Selector(
        sample_size_choices,
        prompt="Choose a sample size: ",
    ).user_choose()
    if sample_size is None:
        while True:
            try:
                sample_size = int(input("Input a sample limit: "))
                if sample_size < 0:
                    print("Please input a positive number.")
                    continue
                break
            except ValueError:
                print("Please input a valid number.")
                continue
    sample_method = Selector(
        {
            str(i+1): Choice(m.value, m.name.replace('_', ' ').title())
        for i, m in enumerate(pl.SampleMethod)
        },
        prompt="Choose a sample method: ",
    ).user_choose()
    combination_method = Selector(
        {
            str(i+1): Choice(m.value, m.name.replace('_', ' ').title())
        for i, m in enumerate(pl.CombinationMethod)
        },
        prompt="Choose a combination method: ",
    ).user_choose()
    write_method = Selector(
        {
            str(i+1): Choice(m.value, m.name.replace('_', ' ').title())
        for i, m in enumerate(PlaylistWriteMethod)
        },
        prompt="Choose a playlist write method: ",
    ).user_choose()

    args: AdvancedParameters = {
        'name': name,
        'source_playlists': [
            pl.serialize_playlist(p) for p in source_playlists
        ],
        'target_playlist': pl.serialize_playlist(target_playlist),
        'sample_size': sample_size,
        'sample_method': sample_method,
        'combination_method': combination_method,
        'write_method': write_method,
    }
    return args

def process_advanced(args: AdvancedParameters):
    logging.info("Combining tracks")
    tracks = pl.combine_tracks(
        [
            pl.get_tracks(
                args['name'],
                pl.deserialize_playlist(args['name'], p),
            ) for p in args['source_playlists']
        ],
        args['sample_size'],
        args['sample_method'],
        args['combination_method'],
    )
    match args['write_method']:
        case PlaylistWriteMethod.UPDATE:
            logging.info("Updating playlist")
            pl.update_playlist(
                args['name'],
                pl.deserialize_playlist(args['name'], args['target_playlist']),
                tracks,
            )
        case PlaylistWriteMethod.OVERWRITE:
            logging.info("Overwriting playlist")
            pl.overwrite_playlist(
                args['name'],
                pl.deserialize_playlist(args['name'], args['target_playlist']),
                tracks,
            )
        case _:
            warnings.warn(f"Write method {args['write_method']} not "
                          "recognized. Target playlist not edited.")

def advanced_flow():
    args = advanced_args()
    process_advanced(args)
    print("Done.")
