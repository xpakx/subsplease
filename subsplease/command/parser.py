def get_parser() -> dict:
    spec = {
        "defaults": {"cmd_key": "today"},
        "subparsers": {
            "dest": "command",
            "help": "Available commands",
            "commands": {
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
            },
        },
    }
    return spec
