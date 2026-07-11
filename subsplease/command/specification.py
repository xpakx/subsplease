from typing import Any, Literal, Type, Tuple
from typing import get_origin, get_args, Union
from types import UnionType
import argparse
from pathlib import Path
from enum import Enum
from collections.abc import Sequence, Iterable

from subsplease.command.typedefs import (
        CmdElem, CmdArg, CmdFlag,
        PathPart, CommandDefinition,
        CmdCmd, is_cmd
)


class CommandSpecs:
    def __init__(self):
        self.specs = {}

    def is_flag_type(self, tp: Type[Any]) -> Tuple[bool, Type[Any] | None]:
        if tp in {int, float, str, bool, bytes, Path}:
            return True, tp

        if isinstance(tp, type) and issubclass(tp, Enum):
            return True, tp

        origin = get_origin(tp)
        args = get_args(tp)

        if origin is Literal:
            return True, tp

        if origin in {list, set, tuple, Sequence, Iterable}:
            if args:
                return self.is_flag_type(args[0])
            return True, tp

        is_union = origin is Union or (UnionType and origin is UnionType)
        if is_union:
            non_none_args = [arg for arg in args if arg is not type(None)]
            if len(non_none_args) == 1:
                return self.is_flag_type(non_none_args[0])
            return False, None

        return False, None

    def parse_path(self, path: str) -> list[PathPart]:
        fragment_list: list[PathPart] = []
        fragments = path.split()
        for fragment in fragments:
            arg = False
            if fragment[0] == ':':
                arg = True
                fragment = fragment[1:]
            if not fragment.isalpha():
                print(f"Part of path {fragment} is incorrect")
                continue
            part = CmdArg(fragment) if arg else CmdCmd(fragment)
            fragment_list.append(part)
        return fragment_list

    def transform_cmd_elems(self, path: list[CmdElem]) -> list[PathPart]:
        fragment_list: list[PathPart] = []
        for fragment in path:
            if isinstance(fragment, CmdArg):
                fragment_list.append(fragment)
            elif fragment.startswith(':'):
                value = fragment[1:]
                fragment_list.append(CmdArg(value))
            else:
                fragment_list.append(CmdCmd(fragment))
        return fragment_list

    def prepare_path(self, cmd_def: CommandDefinition) -> list[PathPart]:
        path = cmd_def.path
        if path is None:
            return [CmdCmd(cmd_def.name)]
        if not path:
            return []
        if isinstance(path, str):
            return self.parse_path(path)
        return self.transform_cmd_elems(path)

    def unpack_optional(self, tp):
        origin = get_origin(tp)
        if origin is Union or origin is UnionType:
            args = get_args(tp)
            if len(args) == 2 and type(None) in args:
                tp = args[1] if args[0] is type(None) else args[0]
        return tp

    def add_to_specs(
            self,
            cmd_def: CommandDefinition
    ):
        path = self.prepare_path(cmd_def)
        curr = self.specs
        curr_command = None
        used_args = set()
        for elem in path:
            if is_cmd(elem):
                self.ensure_subparsers(curr, curr_command)
                curr = curr['subparsers']['commands'].setdefault(elem.name, {})
                curr_command = elem.name
            else:
                self.ensure_args(curr)
                match = next((d for d in curr['args'] if elem.name in d['flags']), None)
                if not match:
                    # TODO: this should be actually overwritten if we have preprocessor
                    arg_type = cmd_def.argument_types.get(elem.name, str)
                    arg_type = self.unpack_optional(arg_type)
                    if elem.true_type and elem.true_type != arg_type:
                        arg_type = elem.true_type
                        cmd_def.argument_types[elem.name] = arg_type
                    curr['args'].append({
                        'flags': [elem.name],
                        'type': arg_type,
                        'help': elem.help or '',
                    })
                else:
                    if elem.help and match['help']:
                        print(f"WARNING: redefining help for {elem.name}")
                    if elem.help:
                        match['help'] = elem.help
                    arg_type = cmd_def.argument_types.get(elem.name, str)
                    if elem.true_type:
                        arg_type = elem.true_type
                    if arg_type != match['type']:
                        print(f"WARNING: `{elem.name}` was already defined as "
                              f"{match['type'].__name__} but `{cmd_def.name}()` "
                              f"tries to redefine it as {arg_type.__name__}."
                              )
                used_args.add(elem.name)

        for arg in cmd_def.arguments:
            tp = cmd_def.argument_types.get(arg)
            if not tp or arg in used_args:
                continue
            is_flag, tp = self.is_flag_type(tp)
            tp = self.unpack_optional(tp)
            if is_flag:
                self.add_flag(curr, arg, tp if tp else str, cmd_def)
        if cmd_def.aliases:
            aliases = curr.setdefault('aliases', [])
            aliases.extend(cmd_def.aliases)
        curr['defaults'] = {'cmd_key': cmd_def.name}
        curr['help'] = cmd_def.docs

    def ensure_subparsers(self, curr, curr_command):
        if 'subparsers' not in curr:
            curr['subparsers'] = {
                    'dest': f"{curr_command}_command" if curr_command else 'command',
                    'help': '',
                    'commands': {},
            }

    def add_flag(self, curr: dict, arg: str,
                 tp: Type[Any], cmd_def: CommandDefinition):
        self.ensure_args(curr)
        var: dict[str, Any] = {}
        flag_def = cmd_def.flags.get(arg)
        if not flag_def:
            flag_def = CmdFlag(arg)
        if flag_def.help:
            var['help'] = flag_def.help
        flags = []
        flags.append(f"--{arg}")
        if flag_def.aliases:
            flags.extend(flag_def.aliases)
        var['flags'] = flags
        if tp == bool:
            var['action'] = "store_true"
        else:
            var['type'] = tp
        curr['args'].append(var)

    def ensure_args(self, curr):
        if 'args' not in curr:
            curr['args'] = []

    def build_parser(self, spec: dict, parser=None) -> argparse.ArgumentParser:
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
                self.build_parser(cmd_spec, parser=sub)

        return parser

    def parser(self) -> argparse.ArgumentParser:
        return self.build_parser(self.specs)
