from ytmb.ui import Menu, Action
import ytmb.utils as utils
import ytmb.authentication as auth


def sign_in():
    prompt = "Name the user: "
    while True:
        username = input(prompt)
        if not utils.is_ok_filename(username):
            print("Please come up with a name using only letters, numbers, "
                  "underscores, and dashes.")
            continue
        elif auth.is_existing_header(username):
            confirm_prompt = "User already logged in. Override? (y/[n]) "
            match input(confirm_prompt):
                case 'y':
                    break
                case _:
                    print("No user logged in.")
                    return
        else:
            break
    auth.create_headers(username)
    print(f"User {username} successfully signed in.")

def users_menu():
    menu = Menu({
        '1': Action(sign_in, "Sign in new user"),

    })
    menu.user_execute()
