import logging
from typing import TypedDict

from ytmb.ui import create_name_selector, create_playlist_selector
import ytmb.playlists as pl


class CompilationParameters(TypedDict):
    name: str
    source_playlists: list[str]
    target_playlist: str

def compilation_args() -> CompilationParameters:
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

    args: CompilationParameters = {
        'name': name,
        'source_playlists': [
            pl.serialize_playlist(p) for p in source_playlists
        ],
        'target_playlist': pl.serialize_playlist(target_playlist),
    }
    return args

def process_compilation(args: CompilationParameters):
    logging.info("Getting tracks")
    source_tracks = [
        pl.get_tracks(args['name'], pl.deserialize_playlist(args['name'], p))
        for p in args['source_playlists']
    ]
    flat_source_tracks = [t for p in source_tracks for t in p]
    target_tracks = pl.get_tracks(
        args['name'],
        pl.deserialize_playlist(args['name'], args['target_playlist']),
    )
    tracks_to_add = pl.tracks_difference(flat_source_tracks, target_tracks)
    tracks_to_remove = pl.tracks_difference(target_tracks, flat_source_tracks)
    add_names = '\n\t'.join(t['title'] for t in tracks_to_add)
    remove_names = '\n\t'.join(t['title'] for t in tracks_to_remove)
    logging.info(f"Tracks to add:\n\t{add_names}")
    logging.info(f"Tracks to remove:\n\t{remove_names}")
    logging.info("Updating playlist")
    combined_tracks = pl.combine_tracks(
        source_tracks,
        pl.SampleLimit.ALL,
        pl.SampleMethod.IN_ORDER,
        pl.CombinationMethod.CONCATENATED,
    )
    pl.update_playlist(
        args['name'],
        pl.deserialize_playlist(args['name'], args['target_playlist']),
        combined_tracks,
    )

def compilation_flow():
    args = compilation_args()
    process_compilation(args)
    print("Done.")
