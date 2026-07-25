from dataclasses import dataclass
from typing import Callable
import sys


@dataclass(slots=True)
class FunctionSignature:
    starting_address: int | None
    param_names: tuple[str, ...] | None
    local_slots_count: int | None
    native_impl: Callable | None


def my_input(prompt: str) -> str:
    sys.stdout.write(prompt)
    sys.stdout.flush()
    return sys.stdin.readline().strip()

def my_print(msg: str):
    sys.stdout.write(f"{msg}\n")
    sys.stdout.flush()

def my_error(err_msg: str):
    sys.stdout.write(f"{err_msg}\n")
    sys.exit(1)


builtins = {
    "log" : FunctionSignature(None, None, None, my_print),
    "input" : FunctionSignature(None, ("arg",), None, my_input),
    "error" : FunctionSignature(None, ("arg",), None, my_error),
    "Integer" : FunctionSignature(None, ("arg",), None, lambda string: int(string)),


}

if __name__ == '__main__':
    pass




