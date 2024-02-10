from ytmb.ui import create_name_selector, create_playlist_selector
import ytmb.playlists as pl


def mixtape_flow():
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
    pl.combine_playlists(
        name,
        source_playlists,
        target_playlist,
        pl.SampleLimit.SHORTEST_PLAYLIST,
        pl.SampleMethod.RANDOM,
        pl.CombinationMethod.INTERLEAVED,
    )
    print("Done.")
