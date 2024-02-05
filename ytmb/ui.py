from typing import Any


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
    ) -> None:
        self.__prompt = prompt
        self.__redo = "Please choose an action by its number."
        self.__actions = actions

    def __str__(self) -> str:
        return '\n'.join(f'{k}: {a.desc}' for k, a in self.__actions.items())

    def __contains__(self, action_key) -> bool:
        return action_key in self.__actions

    def __setitem__(self, key, action: Action) -> None:
        self.__actions[key] = action

    def execute(self, key, *args: Any, **kwds: Any) -> Any:
        return self.__actions[key](*args, **kwds)

    def user_execute(self) -> Any:
        prompt = f"{self}\n{self.__prompt}"
        while (user_key := input(prompt)) not in self:
            print(self.__redo)
        return self.execute(user_key)
