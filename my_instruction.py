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

    # NEGATE = auto()

    JUMP = auto()
    JUMP_IF_FALSE = auto()

    POP = auto()

    HALT = auto()

    def __repr__(self) -> str:
        return f"{self.name}"

@dataclass(slots=True)
class Instruction:
    op_code: OpCode
    argument: tuple

    def __repr__(self) -> str:
        instruction_repr = f"{self.op_code.name}"

        if self.op_code in (OpCode.LOAD_CONST, OpCode.LOAD_GLOBAL, OpCode.STORE_GLOBAL):
            instruction_repr += f" (slot= {self.argument[0]}) "

        elif self.op_code in (OpCode.LOAD_LOCAL, OpCode.STORE_LOCAL):
            instruction_repr += f" (depth= {self.argument[0]}, slot= {self.argument[1]}) "

        elif self.op_code in (OpCode.BINARY_OP, OpCode.COMPARE_OP, OpCode.UNARY_OP):
            instruction_repr += f" (operator= {self.argument[0]}) "

        elif self.op_code == OpCode.CALL:
            instruction_repr += f" (starting_address= {self.argument[0]}, arity= {self.argument[1]}. local_slots_count= {self.argument[2]}) "

        elif self.op_code in (OpCode.JUMP, OpCode.JUMP_IF_FALSE):
            instruction_repr += f" (target_address= {self.argument[0]}) "

        return instruction_repr

