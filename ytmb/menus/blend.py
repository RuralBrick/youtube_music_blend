from typing import TypedDict

from ytmb.ui import create_name_selector, create_playlist_selector
from ytmb.exploration import create_blend
import ytmb.playlists as pl


class BlendParameters(TypedDict):
    name: str
    source_users: list[str]
    target_playlist: str

def blend_args() -> BlendParameters:
    name_selector = create_name_selector()
    source_users = []
    print("Adding source users.")
    while True:
        source_users.append(name_selector.user_choose())
        names = '\n'.join(source_users)
        print(f"Current source users:\n{names}")
        prompt = "Add another user? (y/n) "
        while (add_another := input(prompt)) not in {'y', 'n'}:
            print("Please enter 'y' or 'n'.")
        if add_another == 'n':
            break
    print("Choosing target playlist.")
    name = name_selector.user_choose()
    playlist_selector = create_playlist_selector(name)
    target_playlist = playlist_selector.user_choose()
    print(f"Target playlist: {target_playlist['title']}")

    args: BlendParameters = {
        'name': name,
        'source_users': source_users,
        'target_playlist': pl.serialize_playlist(target_playlist),
    }
    return args

def process_blend(args: BlendParameters):
    create_blend(
        args['name'],
        args['source_users'],
        pl.deserialize_playlist(args['name'], args['target_playlist']),
    )

def blend_flow():
    args = blend_args()
    process_blend(args)
    print("Done.")
