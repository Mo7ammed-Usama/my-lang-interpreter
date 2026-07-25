from dataclasses import dataclass
from typing import Callable
import sys


@dataclass(slots=True)
class FunctionSignature:
    starting_address: int | None
    param_names: tuple[str, ...]
    local_slots_count: int | None
    native_impl: Callable | None


builtins = {
    "log" : FunctionSignature(None, ("arg",), None, print),
    "input" : FunctionSignature(None, ("arg",), None, input),
    "Integer" : FunctionSignature(None, ("arg",), None, lambda string: int(string))

}

if __name__ == '__main__':
    pass