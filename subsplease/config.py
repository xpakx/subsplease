import os
from pathlib import Path
import msgspec


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


class Config(msgspec.Struct, rename="camel"):
    torrent_host: str = msgspec.field(name="torrent_provider_host", default="localhost")
    torrent_port: int = msgspec.field(name="torrent_provider_port", default=9091)
    torrent_username: str = msgspec.field(name="torrent_provider_username", default="test")
    torrent_password: str = msgspec.field(name="torrent_provider_password", default="test_password")
    library_path: Path = Path.home() / 'Videos' / 'TV Series'


def load_config():
    location = get_config_location()
    config_file = location / 'config.json'
    if not config_file.is_file():
        return Config()
    data = config_file.read_text()
    if not data:
        return Config()
    try:
        config = msgspec.json.decode(data, type=Config)
        return config
    except msgspec.DecodeError as e:
        print(f"Couldn't load config file {e}")
        return Config()
