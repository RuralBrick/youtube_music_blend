import logging
import argparse
from typing import NamedTuple, Optional
from pathlib import Path

from ytmb.utils import global_settings
from ytmb.ui import Actor, Action
from ytmb.menus.users import users_menu
from ytmb.menus.blend import blend_flow
from ytmb.menus.mixtape import mixtape_flow
from ytmb.menus.compilation import compilation_flow
from ytmb.menus.tracking import tracking_flow


class ArgNamespace(NamedTuple):
    routine: Optional[str]
    verbose: int
    log: Path
    debug: bool

def parse_args() -> ArgNamespace:
    parser = argparse.ArgumentParser()

    parser.add_argument('routine', nargs='?')

    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        '-v',
        '--verbose',
        action='store_const',
        const=logging.DEBUG,
        default=logging.INFO,
    )
    verbosity.add_argument(
        '-q',
        '--quiet',
        dest='verbose',
        action='store_const',
        const=logging.WARNING,
    )

    parser.add_argument(
        '--log',
        type=Path,
        default=Path(__file__).parent / 'debug.log'
    )

    parser.add_argument('--debug', action='store_true')

    return parser.parse_args()

def config_logs(args: ArgNamespace):
    verbosity_logs = logging.StreamHandler()
    verbosity_logs.setLevel(args.verbose)

    debug_logs = logging.FileHandler(args.log, encoding='utf-8')
    debug_logs.setLevel(logging.DEBUG)

    fmt = '%(levelname)s: (%(module)s.%(funcName)s) [%(asctime)s] %(message)s'
    logging.basicConfig(
        level=logging.DEBUG,
        format=fmt,
        handlers=[
            verbosity_logs,
            debug_logs,
        ],
    )

def main():
    args = parse_args()
    config_logs(args)
    global_settings['debug'] = args.debug

    welcome = "Welcome to YouTube Music Blend!"
    print(welcome)
    print("=" * len(welcome))

    actor = Actor(
        {
            '1': Action(users_menu, "User Management"),
            '2': Action(blend_flow, "Create Blend"),
            '3': Action(mixtape_flow, "Create Mixtape"),
            '4': Action(compilation_flow, "Create Compilation"),

            't': Action(tracking_flow, "Track Playlist"),
        },
        return_key='q',
        return_desc="Quit script",
    )
    try:
        actor.user_execute()
    except KeyboardInterrupt:
        print("\nSee you soon!")
    except BaseException as e:
        if global_settings['debug']:
            raise
        logging.critical(f"ytmb crashed:\n{repr(e)}")

if __name__ == '__main__':
    main()
