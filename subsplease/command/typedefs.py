from dataclasses import dataclass
from typing import Callable


@dataclass
class CommandDefiniton:
    name: str
    arguments: list[str]
    func: Callable
