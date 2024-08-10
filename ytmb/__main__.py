import logging
import sys
import argparse
from enum import Enum, auto
from typing import NamedTuple, Optional
from pathlib import Path

from ytmb.utils import global_settings, get_config_path
from ytmb.automation import get_routines, AUTOMATABLES
from ytmb.ui import Actor, Action
from ytmb.menus.users import users_menu
from ytmb.menus.blend import blend_flow
from ytmb.menus.mixtape import mixtape_flow
from ytmb.menus.compilation import compilation_flow
from ytmb.menus.advanced import advanced_flow
from ytmb.menus.tracking import tracking_flow
from ytmb.menus.routines import routines_menu


DEFAULT_LOG_PATH = Path(__file__).parent / 'debug.log'

class LogOptions(Enum):
    SHOW_LOG = auto()

class ArgNamespace(NamedTuple):
    routine: Optional[str]
    config: bool
    verbose: int
    log: Path | LogOptions
    debug: bool

def parse_args() -> ArgNamespace:
    parser = argparse.ArgumentParser()

    parser.add_argument('routine', nargs='?')

    parser.add_argument('--config', action='store_true')

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
        nargs='?',
        type=Path,
        const=LogOptions.SHOW_LOG,
        default=DEFAULT_LOG_PATH,
    )

    parser.add_argument('--debug', action='store_true')

    return parser.parse_args()

def show_config():
    print(get_config_path().resolve())

def show_logs():
    print(DEFAULT_LOG_PATH.resolve())

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

def interactive_mode():
    welcome = "Welcome to YouTube Music Blend!"
    print(welcome)
    print("=" * len(welcome))

    actor = Actor(
        {
            '1': Action(users_menu, "User Management"),
            '2': Action(blend_flow, "Create Blend"),
            '3': Action(mixtape_flow, "Create Mixtape"),
            '4': Action(compilation_flow, "Create Compilation"),
            'a': Action(advanced_flow, "Advanced Playlist Creation"),
            't': Action(tracking_flow, "Track Playlist"),
            'r': Action(routines_menu, "Routines"),
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

def main():
    args = parse_args()

    if args.config:
        show_config()
        return

    match args.log:
        case LogOptions.SHOW_LOG:
            show_logs()
            return

    config_logs(args)
    global_settings['debug'] = args.debug

    if not args.routine:
        interactive_mode()
        return

    routine = get_routines().get(args.routine, None)

    if not routine:
        print("Routine not found.")
        return 1

    automatable = AUTOMATABLES.get(routine['prog'], None)

    if not automatable:
        print("Program not found.")
        return 1

    automatable.program(routine['args'])

if __name__ == '__main__':
    sys.exit(main())
