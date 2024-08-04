from dataclasses import dataclass
from typing import Callable, TypedDict
import json

from ytmb.utils import get_config, get_data_path
from ytmb.menus.blend import blend_args, process_blend
from ytmb.menus.mixtape import mixtape_args, process_mixtape
from ytmb.menus.compilation import compilation_args, process_compilation
from ytmb.menus.tracking import tracking_args, process_tracking


@dataclass
class Automatable:
    parameterizer: Callable[[], dict]
    program: Callable[[dict], None]

AUTOMATABLES = {
    'Automated Blend': Automatable(blend_args, process_blend),
    'Automated Mixtape': Automatable(mixtape_args, process_mixtape),
    'Automated Compilation': Automatable(compilation_args, process_compilation),
    'Automated Tracking': Automatable(tracking_args, process_tracking),
}

class Routine(TypedDict):
    prog: str
    desc: str
    args: dict

def get_routines() -> dict[str, Routine]:
    p_routines = get_data_path() / get_config()['automation']['routines_path']
    if not p_routines.is_file():
        return {}
    with open(p_routines, encoding='utf-8') as f:
        routines = json.load(f)
        return routines

def write_routines(routines: dict[str, Routine]):
    p_routines = get_data_path() / get_config()['automation']['routines_path']
    with open(p_routines, 'w', encoding='utf-8') as f:
        json.dump(routines, f, indent=4)

def add_routine(name: str, routine: Routine):
    routines = get_routines()
    routines[name] = routine
    write_routines(routines)

def remove_routine(name: str):
    routines = get_routines()
    del routines[name]
    write_routines(routines)
