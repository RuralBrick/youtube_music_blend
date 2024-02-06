import logging
import warnings
from typing import Any
from itertools import islice

from ytmb.utils import get_config


class Action:
    def __init__(self, callable, desc) -> None:
        self.__callable = callable
        self.__desc = desc

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.__callable(*args, **kwds)

    @property
    def desc(self):
        return self.__desc

class Menu:
    def __init__(
            self,
            actions={},
            *,
            prompt="What would you like to do? ",
            prev_key='p',
            next_key='n',
            return_key='r',
            return_desc="Return to previous menu",
    ) -> None:
        self._prompt = prompt
        self._redo = "Please choose an action by its key."
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

    def __str__(self) -> str:
        return '\n'.join(f'{k}: {a.desc}' for k, a in self._actions.items())

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

    @property
    def _actions(self):
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
        return prev_action | self._actions_page() | next_action | return_action

    def _return_menu(self):
        """raises StopIteration"""
        raise StopIteration()

    def _actions_page(self):
        page_size = get_config()['ui']['menu_limit']
        current_page_first_index = self._current_page * page_size
        return {
            key: action for key, action in islice(
                self.__actions.items(),
                current_page_first_index,
                current_page_first_index + page_size
            )
        }

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

    def execute(self, key, *args: Any, **kwds: Any) -> Any:
        return self._actions[key](*args, **kwds)

    def user_execute(self) -> Any:
        try:
            while True:
                prompt = f"{self}\n{self._prompt}"
                while (user_key := input(prompt)) not in self._actions:
                    print(self._redo)
                self.execute(user_key)
        except StopIteration:
            pass
