from dataclasses import dataclass
from enum import Enum, auto


class OpCode(Enum):
    LOAD_CONST = auto()
    LOAD_NULL = auto()
    LOAD_GLOBAL = auto()
    STORE_GLOBAL = auto()

    LOAD_LOCAL = auto()
    STORE_LOCAL = auto()

    BINARY_OP = auto()
    COMPARE_OP = auto()
    UNARY_OP = auto()

    CALL = auto()
    RETURN = auto()

    NEGATE = auto()

    JUMP = auto()
    JUMP_IF_FALSE = auto()
    BREAK = auto()
    CONTINUE = auto()

    POP = auto()

    HALT = auto()

    def __repr__(self) -> str:
        return f"{self.name}"

@dataclass(slots=True)
class Instruction:
    op_code: OpCode
    operand: object = None

    def __repr__(self):
        return f"{self.op_code.name} {self.operand}"