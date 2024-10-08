from typing import TypedDict, NotRequired

from ytmb.utils import get_config, write_config
from ytmb.ui import (
    create_name_selector,
    create_playlist_selector,
    get_create_playlist_kwargs,
)
from ytmb.exploration import create_blend
import ytmb.playlists as pl


class BlendParameters(TypedDict):
    name: str
    source_users: list[str]
    target_playlist: str
    length: NotRequired[int]

def blend_args() -> BlendParameters:
    """throws ValueError"""
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
    target_playlist = None
    prompt = "Create new playlist? (y/n) "
    while (create_new := input(prompt)) not in {'y', 'n'}:
        print("Please enter 'y' or 'n'.")
    if create_new == 'y':
        kwargs = get_create_playlist_kwargs(name)
        target_playlist = pl.create_playlist(**kwargs)
        if not target_playlist:
            print("Please choose a preexisting playlist instead.")
    if not target_playlist:
        playlist_selector = create_playlist_selector(name)
        target_playlist = playlist_selector.user_choose()
    if len(pl.get_tracks(name, target_playlist)) > 0:
        match input("Target playlist not empty. Continue? (y/[n]) "):
            case 'y':
                pass
            case _:
                raise ValueError("Non-empty target playlist")
    print(f"Target playlist: {target_playlist['title']}")

    args: BlendParameters = {
        'name': name,
        'source_users': source_users,
        'target_playlist': pl.serialize_playlist(target_playlist),
    }

    if get_config()['blend']['ask_for_length']:
        match input("Enter blend length? ([y]/n) "):
            case 'n':
                match input("Ask for blend length next time? ([y]/n) "):
                    case 'n':
                        config = get_config()
                        config['blend']['ask_for_length'] = False
                        write_config(config)
                    case _:
                        pass
            case _:
                while True:
                    try:
                        blend_length = int(input("Input a blend length: "))
                        if blend_length < 0:
                            print("Please input a positive number.")
                            continue
                        break
                    except ValueError:
                        print("Please input a valid number.")
                        continue
                args['length'] = blend_length

    return args

def process_blend(args: BlendParameters):
    create_blend(
        args['name'],
        args['source_users'],
        pl.deserialize_playlist(args['name'], args['target_playlist']),
        args.get('length', get_config()['blend']['default_length']),
    )

def blend_flow():
    try:
        args = blend_args()
    except ValueError:
        print("No blend created.")
        return
    process_blend(args)
    print("Done.")
