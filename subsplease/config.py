import os
from pathlib import Path


def get_xdg(var: str, default: str) -> Path:
    path_str = os.environ.get(var)
    if path_str:
        path_str = Path(path_str)
    else:
        home = os.environ.get('HOME', '')
        path_str = Path(home) / default
    path = path_str / 'subsplease'
    return path


def get_config_location() -> Path:
    return get_xdg('XDG_CONFIG_HOME', '.config')


def get_cache_location() -> Path:
    return get_xdg('XDG_CACHE_HOME', '.cache')


def get_data_location() -> Path:
    return get_xdg('XDG_DATA_HOME', '.local/share')
