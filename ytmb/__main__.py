import argparse
import logging
from pathlib import Path

from ytmb.playlists import dummy_playlist



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

    logging.info('log says hi')
    logging.debug('secrets lie here')
    logging.error('uh, plz react')

    print("Hi from __main__.py")
    print(dummy_playlist())
    print(args.log)
    print(__file__)


if __name__ == '__main__':
    main()
