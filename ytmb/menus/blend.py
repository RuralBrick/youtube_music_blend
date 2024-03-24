from ytmb.ui import create_name_selector, create_playlist_selector


def blend_flow():
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



    print("Done.")
