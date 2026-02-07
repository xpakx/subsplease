from __future__ import annotations
from typing import Generic, TypeVar, Callable, Any

T = TypeVar("T")  # Success Type
E = TypeVar("E")  # Error Type
U = TypeVar("U")  # New Success Type
F = TypeVar("F")  # New Error Type


class UnwrapError(Exception):
    pass


class Result(Generic[T, E]):
    _is_ok: bool = False

    def is_ok(self) -> bool:
        return self._is_ok

    def is_err(self) -> bool:
        return not self.is_ok()

    def ok(self) -> T | None:
        return self.value if self.is_ok() else None

    def err(self) -> E | None:
        return self.error if self.is_err() else None

    def unwrap(self) -> T:
        if self.is_ok():
            return self.value
        else:
            raise UnwrapError(f"Called unwrap on an Err: {self.error}")

    def unwrap_or(self, default: T) -> T:
        if self.is_ok():
            return self.value
        return default

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        if self.is_ok():
            return self.value
        else:
            return op(self.error)

    def expect(self, msg: str) -> T:
        if self.is_ok():
            return self.value
        else:
            raise UnwrapError(f"{msg}: {self.error}")

    def map(self, op: Callable[[T], U]) -> Result[U, E]:
        if self.is_ok():
            return Ok(op(self.value))
        else:
            return Err(self.error)

    def try_map(self, op: Callable[[T], U]) -> Result[U, E]:
        if self.is_ok():
            try:
                return Ok(op(self.value))
            except Exception as e:
                return Err(str(e))
        else:
            return Err(self.error)

    def map_err(self, op: Callable[[E], F]) -> Result[T, F]:
        if self.is_ok():
            return Ok(self.value)
        else:
            return Err(op(self.error))

    def and_then(self, op: Callable[[T], Result[U, E]]) -> Result[U, E]:
        if self.is_ok():
            return op(self.value)
        else:
            return Err(self.error)


class Ok(Result[T, Any]):
    _is_ok: bool = True

    def __init__(self, value):
        self.value = value

    def __repr__(self) -> str:
        return f"Ok({self.value!r})"


class Err(Result[Any, E]):
    _is_ok: bool = False

    def __init__(self, error):
        self.error = error

    def __repr__(self) -> str:
        return f"Err({self.error!r})"
