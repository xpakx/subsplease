from inspect import signature
from dataclasses import dataclass
from typing import Callable, Any


@dataclass
class CommandDefiniton:
    name: str
    arguments: list[str]
    func: Callable


class CommandDispatcher:
    def __init__(self):
        self.commands: dict[str, CommandDefiniton] = {}
        self.services: dict[str, Any] = {}
        self.preprocessors: dict[str, Callable] = {}

    def register(self, name: str, command: Callable):
        sig = signature(command)
        args = list(sig.parameters.keys())
        cmd_def = CommandDefiniton(
                name=name,
                func=command,
                arguments=args
        )
        self.commands[name] = cmd_def

    def add_service(self, name: str, service: Any):
        self.services[name] = service

    def add_preprocessor(self, name: str, processor: Callable):
        self.preprocessors[name] = processor

    def dispatch(self, name, args):
        cmd = self.commands.get(name)
        if not cmd:
            return
        kwargs = {}
        vs = vars(args)
        for elem in cmd.arguments:
            if elem in self.services:
                kwargs[elem] = self.services.get(elem)
            else:
                value = vs.get(elem)
                if elem in self.preprocessors:
                    value = self.preprocessors[elem](value)
                kwargs[elem] = value
        cmd.func(**kwargs)

    def command(self, f):
        self.register(f.__name__, f)
        return f
