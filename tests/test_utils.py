from ytmb.utils import *


def main():
    print(f"{is_ok_filename('abcdefg1234')=}")
    print(f"{is_ok_filename('Some_Test_Name-Version2')=}")
    print(f"{not is_ok_filename('#BadNames')=}")
    print(f"{not is_ok_filename('dots.dots.dots')=}")
    print(f"{not is_ok_filename('we/love/directories')=}")
    print(f"{not is_ok_filename('')=}")

if __name__ == '__main__':
    main()
