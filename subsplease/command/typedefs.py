from dataclasses import dataclass
from typing import Callable, Any, Type
from typing import TypeIs


class CmdArg:
    type = 'ARG'

    def __init__(
            self,
            name: str,
            *,
            help: str | None = None,
            true_type: Type[Any] | None = None,
    ):
        self.name = name
        self.help = help
        # TODO: that should be later autodetected based on
        # transformation, etc
        self.true_type = true_type


CmdElem = str | CmdArg


class CmdFlag:
    type = 'FLAG'

    def __init__(
            self,
            name: str,
            *,
            aliases: list[str] | str | None = None,
            help: str | None = None,
    ):
        self.name = name
        if type(aliases) is str:
            self.aliases = [aliases]
        else:
            self.aliases = aliases
        self.help = help


class CmdCmd:
    def __init__(
            self,
            name: str,
    ):
        self.name = name
        self.type = 'CMD'


PathPart = CmdCmd | CmdArg


@dataclass
class CommandDefinition:
    name: str
    arguments: list[str]
    argument_types: dict[str, Type[Any]]
    func: Callable
    docs: str | None
    flags: dict[str, CmdFlag]
    path: str | list[CmdElem] | None = None,


@dataclass
class ServiceData:
    name: str
    type: Type[Any]
    service: Any


def is_cmd(val: PathPart) -> TypeIs[CmdCmd]:
    return val.type == 'CMD'


def is_arg(val: PathPart) -> TypeIs[CmdArg]:
    return val.type == 'ARG'
