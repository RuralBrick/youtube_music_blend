import logging
import warnings
from typing import Any
from itertools import islice

from ytmb.utils import get_config
import ytmb.authentication as auth
from ytmb.playlists import get_playlists


class Action:
    def __init__(self, callable, desc) -> None:
        self.__callable = callable
        self.__desc = desc

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        if callable(self.__callable):
            return self.__callable(*args, **kwds)
        else:
            return self.__callable

    @property
    def desc(self):
        return self.__desc

class Menu:
    def __init__(
            self,
            actions={},
            *,
            prompt="What would you like to do? ",
            redo="Please choose an action by its key.",
            prev_key='p',
            next_key='n',
            return_key='r',
            return_desc="Return to previous menu",
    ) -> None:
        self._prompt = prompt
        self._redo = redo
        self._prev_key = prev_key
        self._next_key = next_key
        self._return_key = return_key
        if prev_key in actions:
            warnings.warn(
                "An action uses the same key as the prev action. Actions may "
                "behave unexpectedly."
            )
        if next_key in actions:
            warnings.warn(
                "An action uses the same key as the next action. Actions may "
                "behave unexpectedly."
            )
        if return_key in actions:
            warnings.warn(
                "An action uses the same key as the return action. Actions may "
                "behave unexpectedly."
            )
        self._return_desc = return_desc
        self._current_page = 0
        self.__actions = actions

    def __contains__(self, action_key) -> bool:
        return action_key in self.__actions

    def __setitem__(self, key, action: Action) -> None:
        if key == self._prev_key:
            warnings.warn(
                "This action is being set to the same key as the prev action. "
                "Actions may behave unexpectedly."
            )
        if key == self._next_key:
            warnings.warn(
                "This action is being set to the same key as the next action. "
                "Actions may behave unexpectedly."
            )
        if key == self._return_key:
            warnings.warn(
                "This action is being set to the same key as the return "
                "action. Actions may behave unexpectedly."
            )
        self.__actions[key] = action

    def _at_first_page(self):
        return self._current_page <= 0

    def _at_last_page(self):
        last_index = len(self.__actions) - 1
        last_page = last_index // get_config()['ui']['menu_limit']
        return self._current_page >= last_page

    def _go_prev(self):
        """raises ValueError"""
        if self._at_first_page():
            raise ValueError("Page cannot be decremented further")
        self._current_page -= 1

    def _go_next(self):
        """raises ValueError"""
        if self._at_last_page():
            raise ValueError("Page cannot be incremented further")
        self._current_page += 1

    def _return_menu(self):
        """raises StopIteration"""
        raise StopIteration()

    def _get_actions_page(self):
        page_size = get_config()['ui']['menu_limit']
        current_page_first_index = self._current_page * page_size
        return {
            key: action for key, action in islice(
                self.__actions.items(),
                current_page_first_index,
                current_page_first_index + page_size
            )
        }

    def _get_current_actions(self) -> dict:
        prev_action = (
            {self._prev_key: Action(self._go_prev, "Previous page")}
            if not self._at_first_page()
            else {}
        )
        next_action = (
            {self._next_key: Action(self._go_next, "Next page")}
            if not self._at_last_page()
            else {}
        )
        return_action = {
            self._return_key: Action(self._return_menu, self._return_desc)
        }
        return (
            prev_action |
            self._get_actions_page() |
            next_action |
            return_action
        )

    def current_actions_to_string(self) -> str:
        return '\n'.join(
            f'{k}: {a.desc}' for k, a in self._get_current_actions().items()
        )

    def execute(self, key, *args: Any, **kwds: Any) -> Any:
        try:
            action = self._get_current_actions()[key]
        except KeyError:
            raise KeyError(f"Key \"{key}\" not on current page")
        return action(*args, **kwds)

    def user_execute(self) -> None:
        while True:
            prompt = f"{self.current_actions_to_string()}\n{self._prompt}"
            current_actions = self._get_current_actions()
            while (user_key := input(prompt)) not in current_actions:
                print(self._redo)
            try:
                self.execute(user_key)
            except StopIteration:
                return
            except Exception as e:
                logging.error(f"Could not complete action:\n{e}")

    def user_choose(self) -> Any:
        prompt = f"{self.current_actions_to_string()}\n{self._prompt}"
        current_actions = self._get_current_actions()
        while (user_key := input(prompt)) not in current_actions:
            print(self._redo)
        try:
            return self.execute(user_key)
        except Exception as e:
            logging.error(f"Could not complete action:\n{e}")
            return None

def create_name_menu() -> Menu:
    names = auth.get_header_names()
    name_menu = Menu(
        {str(i+1): n for i, n in enumerate(names)},
        prompt="Choose a name: ",
        redo="Please choose a name by its number.",
    )
    return name_menu

def create_playlist_menu(name) -> Menu:
    playlists = get_playlists(name)
    playlist_menu = Menu(
        {
            str(i+1): f"{p['title']} ({p['count']} tracks)"
            for i, p in enumerate(playlists)
        },
        prompt="Choose a playlist: ",
        redo="Please choose a playlist by its number.",
    )
    return playlist_menu
