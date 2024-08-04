from typing import TypedDict

from ytmb.ui import create_name_selector, create_playlist_selector
import ytmb.playlists as pl


class MixtapeParameters(TypedDict):
    name: str
    source_playlists: list[str]
    target_playlist: str

def mixtape_args() -> MixtapeParameters:
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

    args: MixtapeParameters = {
        'name': name,
        'source_playlists': [
            pl.serialize_playlist(p) for p in source_playlists
        ],
        'target_playlist': pl.serialize_playlist(target_playlist),
    }
    return args

def process_mixtape(args: MixtapeParameters):
    pl.combine_playlists(
        args['name'],
        [
            pl.deserialize_playlist(args['name'], p)
            for p in args['source_playlists']
        ],
        pl.deserialize_playlist(args['name'], args['target_playlist']),
        pl.SampleLimit.SHORTEST_PLAYLIST,
        pl.SampleMethod.RANDOM,
        pl.CombinationMethod.INTERLEAVED,
    )

def mixtape_flow():
    args = mixtape_args()
    process_mixtape(args)
    print("Done.")
