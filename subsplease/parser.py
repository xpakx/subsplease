import argparse


def build_parser(spec: dict, parser=None) -> argparse.ArgumentParser:
    if parser is None:
        parser = argparse.ArgumentParser(
                description=spec.get("description", ""))

    for arg in spec.get("args", []):
        flags = arg.pop("flags")
        parser.add_argument(*flags, **arg)

    if "defaults" in spec:
        parser.set_defaults(**spec["defaults"])

    if "subparsers" in spec:
        sp_spec = spec["subparsers"]
        subparsers = parser.add_subparsers(
            dest=sp_spec["dest"], help=sp_spec.get("help")
        )
        for name, cmd_spec in sp_spec.get("commands", {}).items():
            parser_args = {
                k: v
                for k, v in cmd_spec.items()
                if k not in ["args", "subparsers", "defaults"]
            }
            sub = subparsers.add_parser(name, **parser_args)
            build_parser(cmd_spec, parser=sub)

    return parser


def get_parser() -> argparse.ArgumentParser:
    spec = {
        "defaults": {"cmd_key": "today"},
        "subparsers": {
            "dest": "command",
            "help": "Available commands",
            "commands": {
                "show": {
                    "aliases": ["s"],
                    "help": "Operate on show",
                    "args": [
                        {
                            "flags": ["name"],
                            "type": str,
                            "help": "Name of the show"
                        }
                    ],
                    "defaults": {"cmd_key": "show_view"},
                    "subparsers": {
                        "dest": "show_action",
                        "commands": {
                            "subscribe": {
                                "aliases": ["sub"],
                                "help": "Subscribe",
                                "defaults": {"cmd_key": "subscribe"},
                                "args": [
                                    {
                                        "flags": ["-u", "--unsubscribe"],
                                        "action": "store_true",
                                        "help": "Unsubscribe show",
                                    }
                                ],
                            },
                            "latest": {
                                "help": "Latest episodes for the show",
                                "defaults": {"cmd_key": "show_latest"},
                            },
                            "get": {
                                "help": "get episode",
                                "defaults": {"cmd_key": "show_get"},
                                "args": [
                                    {
                                        "flags": ["-e", "--episode"],
                                        "type": int,
                                        "help": "episode number",
                                    }
                                ],
                            },
                            "delete": {
                                "help": "Delete show",
                                "defaults": {"cmd_key": "show_delete"},
                            },
                        },
                    },
                },
                "day": {
                    "help": "Operate on day",
                    "defaults": {"cmd_key": "day"},
                    "args": [
                        {
                            "flags": ["weekday"],
                            "type": str,
                            "help": "Weekday"
                        }
                    ],
                },
                "sync": {
                        "help": "Sync files",
                        "defaults": {"cmd_key": "sync"}
                },
                "season": {
                    "help": "Weekly schedule",
                    "defaults": {"cmd_key": "show_season"},
                    "subparsers": {
                        "dest": "season_action",
                        "commands": {
                            "update": {
                                "help": "Update schedule",
                                "defaults": {"cmd_key": "update_season"},
                            }
                        },
                    },
                },
                "clean": {
                        "help": "Clean torrents",
                        "defaults": {"cmd_key": "clean"}
                },
                "latest": {
                    "help": "All latest uploads",
                    "defaults": {"cmd_key": "all_latest"},
                },
                "search": {
                    "help": "Search meta data",
                    "args": [
                        {
                            "flags": ["name"],
                            "type": str, "help": "Name of the show"
                        }
                    ],
                    "defaults": {"cmd_key": "search_show_meta"},
                    "subparsers": {
                        "dest": "command_search",
                        "help": "Available commands",
                        "commands": {
                            "nyaa": {
                                "help": "Search torrents",
                                "defaults": {
                                    "cmd_key": "search_show_torrents"
                                },
                            }
                        },
                    },
                },
                "subs": {
                    "help": "Subscribed shows",
                    "defaults": {"cmd_key": "show_subs"},
                    "subparsers": {
                        "dest": "subs_action",
                        "commands": {
                            "get": {
                                "help": "Get all subscribed",
                                "defaults": {"cmd_key": "get_all_subs"},
                            }
                        },
                    },
                },
            },
        },

    }
    return build_parser(spec)
