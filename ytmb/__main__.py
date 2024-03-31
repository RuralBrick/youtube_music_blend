import logging
import argparse
from pathlib import Path

from ytmb.ui import Actor, Action
from ytmb.menus.users import users_menu
from ytmb.menus.blend import blend_flow
from ytmb.menus.mixtape import mixtape_flow


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

    debug_logs = logging.FileHandler(
        Path(__file__).parent / 'debug.log',
        encoding='utf-8',
    )
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

    actor = Actor(
        {
            '1': Action(users_menu, "User Management"),
            '2': Action(blend_flow, "Create Blend"),
            '3': Action(mixtape_flow, "Create Mixtape"),

        },
        return_key='q',
        return_desc="Quit script",
    )
    try:
        actor.user_execute()
    except KeyboardInterrupt:
        print("\nSee you soon!")
    except BaseException as e:
        logging.critical(f"ytmb crashed:\n{repr(e)}")

if __name__ == '__main__':
    main()
