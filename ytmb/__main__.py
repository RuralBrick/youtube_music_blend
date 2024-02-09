import sys
import logging
import argparse
from pathlib import Path

from ytmb.ui import Menu, Action
from ytmb.menus.users import users_menu


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_const',
        const=logging.DEBUG,
        default=logging.INFO,
    )
    parser.add_argument('--log', type=Path, default=Path('debug.log'))
    args = parser.parse_args()

    verbosity_logs = logging.StreamHandler()
    verbosity_logs.setLevel(args.verbose)

    debug_logs = logging.FileHandler(Path(__file__).parent / 'debug.log')
    debug_logs.setLevel(logging.DEBUG)

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s: (%(module)s.%(funcName)s) [%(asctime)s] %(message)s',
        handlers=[
            verbosity_logs,
            debug_logs,
        ],
    )

    welcome = "Welcome to YouTube Music Blend!"
    print(welcome)
    print("=" * len(welcome))

    menu = Menu(
        {
            '1': Action(users_menu, "User Management"),

        },
        return_key='q',
        return_desc="Quit script",
    )
    menu.user_execute()

if __name__ == '__main__':
    main()
