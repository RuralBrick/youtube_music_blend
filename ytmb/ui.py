import logging
import warnings
from typing import Any
from dataclasses import dataclass
from itertools import islice

from ytmb.utils import get_config
import ytmb.authentication as auth
from ytmb.playlists import get_playlists


@dataclass
class Choice:
    obj: Any
    desc: str

class Action:
    def __init__(self, callable, desc) -> None:
        self.__callable = callable
        self.__desc = desc

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.__callable(*args, **kwds)

    @property
    def desc(self):
        return self.__desc

class Pager:
    def __init__(self, listings: dict={}) -> None:
        self.__listings = listings
        self.__current_page = 0

    def __getitem__(self, key) -> Any:
        return self.__listings[key]

    def __setitem__(self, key, listing) -> None:
        self.__listings[key] = listing

    def at_first_page(self):
        return self.__current_page <= 0

    def at_last_page(self):
        last_index = len(self.__listings) - 1
        last_page = last_index // get_config()['ui']['menu_limit']
        return self.__current_page >= last_page

    def go_prev(self):
        """raises ValueError"""
        if self.at_first_page():
            raise ValueError("Page cannot be decremented further")
        self.__current_page -= 1

    def go_next(self):
        """raises ValueError"""
        if self.at_last_page():
            raise ValueError("Page cannot be incremented further")
        self.__current_page += 1

    def return_menu(self):
        """raises StopIteration"""
        raise StopIteration()

    def get_current_page(self) -> dict:
        page_size = get_config()['ui']['menu_limit']
        current_page_first_index = self.__current_page * page_size
        return {
            key: listing for key, listing in islice(
                self.__listings.items(),
                current_page_first_index,
                current_page_first_index + page_size
            )
        }

    def get_current_page_with_navigation(
            self,
            prev_key,
            next_key,
            return_key=None,
            return_desc="Return to previous menu",
    ) -> dict:
        current_page = self.get_current_page()
        prev_action = (
            {prev_key: Action(self.go_prev, "Previous page")}
            if not self.at_first_page()
            else {}
        )
        next_action = (
            {next_key: Action(self.go_next, "Next page")}
            if not self.at_last_page()
            else {}
        )
        return_action = (
            {return_key: Action(self.return_menu, return_desc)}
            if return_key
            else {}
        )
        return prev_action | current_page | next_action | return_action

    def page_to_string(self, page) -> str:
        return '\n'.join(f'{k}: {l.desc}' for k, l in page.items())

class Selector:
    def __init__(
            self,
            choices={},
            *,
            prompt="Choose an option: ",
            redo="Please choose an option by its key.",
            prev_key='p',
            next_key='n',
    ) -> None:
        self._prompt = prompt
        self._redo = redo
        self._prev_key = prev_key
        self._next_key = next_key
        if prev_key in choices:
            warnings.warn(
                "A choice uses the same key as the prev action. Selector may "
                "behave unexpectedly."
            )
        if next_key in choices:
            warnings.warn(
                "A choice uses the same key as the next action. Selector may "
                "behave unexpectedly."
            )
        self._current_page = 0
        self.__pager = Pager(choices)

    def __setitem__(self, key, choice: Choice) -> None:
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
        self.__pager[key] = choice

    def _get_current_choices(self) -> dict:
        return self.__pager.get_current_page_with_navigation(
            self._prev_key,
            self._next_key,
        )

    def user_choose(self) -> Any:
        while True:
            current_choices = self._get_current_choices()
            prompt = (f"{self.__pager.page_to_string(current_choices)}\n"
                      f"{self._prompt}")
            while (user_key := input(prompt)) not in current_choices:
                print(self._redo)
            match current_choices[user_key]:
                case Choice(obj=obj):
                    return obj
                case Action():
                    current_choices[user_key]()
                case something:
                    logging.warning(
                        f"Mysterious object found in selector: {something}"
                    )
                    return

class Actor:
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
        self.__pager = Pager(actions)

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
        self.__pager[key] = action

    def _get_current_actions(self) -> dict:
        return self.__pager.get_current_page_with_navigation(
            self._prev_key,
            self._next_key,
            self._return_key,
            self._return_desc,
        )

    def execute(self, key, *args: Any, **kwds: Any) -> Any:
        try:
            action = self._get_current_actions()[key]
        except KeyError:
            raise KeyError(f"Key \"{key}\" not on current page")
        return action(*args, **kwds)

    def user_execute(self) -> None:
        while True:
            current_actions = self._get_current_actions()
            prompt = (f"{self.__pager.page_to_string(current_actions)}\n"
                      f"{self._prompt}")
            while (user_key := input(prompt)) not in current_actions:
                print(self._redo)
            try:
                self.execute(user_key)
            except StopIteration:
                return
            except Exception as e:
                logging.error(f"Could not complete action:\n{repr(e)}")

def create_name_selector() -> Selector:
    names = auth.get_header_names()
    name_menu = Selector(
        {str(i+1): Choice(n, n) for i, n in enumerate(names)},
        prompt="Choose a name: ",
        redo="Please choose a name by its number.",
    )
    return name_menu

def create_playlist_selector(name) -> Selector:
    playlists = get_playlists(name)
    playlist_menu = Selector(
        {
            str(i+1): Choice(
                p, f"{p['title']} ({p.get('count', 'auto-generated')} tracks)"
            )
            for i, p in enumerate(playlists)
        },
        prompt="Choose a playlist: ",
        redo="Please choose a playlist by its number.",
    )
    return playlist_menu
