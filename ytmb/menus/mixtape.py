from ytmb.ui import create_name_menu, create_playlist_menu
import ytmb.playlists as pl


def mixtape_flow():
    name_menu = create_name_menu()
    source_playlists = []
    print("Adding source playlists.")
    while True:
        name = name_menu.user_choose()
        playlist_menu = create_playlist_menu(name)
        source_playlists.add(playlist_menu.user_choose())
        titles = '\n'.join(f"- {p['title']}" for p in source_playlists)
        print(f"Current source playlists:\n{titles}")
        prompt = "Add another playlist? (y/n) "
        while (add_another := input(prompt)) not in {'y', 'n'}:
            print("Please enter 'y' or 'n'.")
        if add_another == 'n':
            break
    print("Choosing target playlist.")
    name = name_menu.user_choose()
    playlist_menu = create_playlist_menu(name)
    target_playlist = playlist_menu.user_choose()
    print(f"Target playlist: {target_playlist['title']}")
    pl.combine_playlists(
        name,
        source_playlists,
        target_playlist,
        pl.SampleLimit.SHORTEST_PLAYLIST,
        pl.SampleMethod.RANDOM,
        pl.CombinationMethod.INTERLEAVED,
    )
    print("Done.")
