from ytmb.ui import Actor, Action, Selector, Choice
from ytmb.automation import (
    AUTOMATABLES,
    Routine,
    get_routines,
    add_routine,
    remove_routine,
)


def create_routine():
    program_selector = Selector({
        str(i+1): Choice((n, a), n) for i, (n, a)
        in enumerate(AUTOMATABLES.items())
    })
    prog, automatable = program_selector.user_choose()

    try:
        args = automatable.parameterizer()
    except ValueError:
        print("Routine creation aborted.")
        return

    while True:
        name = input("Name the routine: ")
        if not name:
            print("Name cannot be blank.")
            continue
        else:
            break

    desc = input("Add a description (can be left blank): ")

    routine: Routine = {
        'prog': prog,
        'desc': desc,
        'args': args,
    }
    add_routine(name, routine)
    print("Done.")

def delete_routine():
    if not get_routines():
        print("No routines set up yet.")
        return
    routines_selector = Selector(
        {str(i+1): Choice(n, n) for i, n in enumerate(get_routines().keys())}
    )
    name = routines_selector.user_choose()
    remove_routine(name)
    print("Done.")

def routines_menu():
    actor = Actor({
        '1': Action(create_routine, "Create Routine"),
        '2': Action(delete_routine, "Delete Routine"),
    })
    actor.user_execute()
