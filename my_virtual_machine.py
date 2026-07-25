from my_compiler import FunctionSignature
from my_instruction import Instruction, OpCode
from my_token import TokenType


class Frame:
    def __init__(self, local_slots_count: int, return_address: int):
        self.locals: list[object] = [None] * local_slots_count
        self.return_address = return_address

    def __repr__(self):
        return f"Frame(Locals= {self.locals}, return_address= {self.return_address})"

class VirtualMachine:
    def __init__(self, instructions: tuple[Instruction, ...], constants: tuple[object, ...], global_slots_count: int,
                 function_signatures: dict[str, FunctionSignature], enable_tracing: bool = False):
        self.__enable_tracing = enable_tracing
        self.__instructions = instructions

        self.__constants = constants
        self.__globals: list[object] = [None] * global_slots_count
        self.__function_signatures = function_signatures

        self.__stack: list[object] = []
        self.__call_stack: list[Frame] = []

        self.__program_counter = 0
        self.__is_halt = False

        self.__instruction_to_method = {
            OpCode.LOAD_CONST: self.__load_const,
            OpCode.LOAD_NULL: self.__load_null,
            OpCode.LOAD_GLOBAL: self.__load_global,
            OpCode.STORE_GLOBAL: self.__store_global,

            OpCode.LOAD_LOCAL: self.__load_local,
            OpCode.STORE_LOCAL: self.__store_local,

            OpCode.BINARY_OP: self.__binary_op,
            OpCode.COMPARE_OP: self.__compare_op,
            OpCode.UNARY_OP: self.__unary_op,

            OpCode.CALL: self.__call,
            OpCode.RETURN: self.__return,

            OpCode.JUMP: self.__jump,
            OpCode.JUMP_IF_FALSE: self.__jump_if_false,

            OpCode.POP: self.__pop_instruction,

            OpCode.HALT: self.__halt
        }

    # ================== Main Method ===================
    def run(self) -> tuple[object, ...]:
        instructions = self.__instructions

        while not self.__is_halt:
            self.__execute_instruction(instructions[self.__program_counter])

        return tuple(self.__stack)

    # ================== Core Methods ==================
    def __execute_instruction(self, instruction: Instruction):
        program_counter_now = self.__program_counter
        method = self.__instruction_to_method.get(instruction.op_code)

        if method is None:
            raise RuntimeError(f"Unexpected Instruction: {instruction}")

        method(argument=instruction.argument)
        self.__log(f"current stack: {self.__stack}\n")

        if self.__program_counter != program_counter_now:
            return

        self.__program_counter += 1

    # =========== Every Instruction Handling ===========
    def __load_const(self, argument: tuple):
        slot = argument[0]
        self.__push(self.__constants[slot])

    def __load_null(self, argument: tuple):
        self.__push(None)

    def __load_global(self, argument: tuple):
        slot = argument[0]
        self.__log(f"Global variable in slot: ({slot}), will load to the top the stack")
        self.__push(self.__globals[slot])

    def __store_global(self, argument: tuple):
        slot = argument[0]
        self.__globals[slot] = self.__pop()
        self.__log(f"{self.__globals[slot].__repr__()} stored to slot ({slot}), in globals")

    def __load_local(self, argument: tuple):
        depth, slot = argument
        self.__log(f"local variable in slot: ({slot}), in: {"current call frame" if depth == 0 else f"({depth}) previous call stack"}, will load to the top the stack")
        self.__push(self.__call_stack[-(depth + 1)].locals[slot])

    def __store_local(self, argument: tuple):
        depth, slot = argument
        self.__call_stack[-(depth + 1)].locals[slot] = self.__pop()
        self.__log(f"top of the stack stored to slot: ({slot}), in: {"current call frame" if depth == 0 else f"({depth}) previous call frame"}")

    def __binary_op(self, argument: tuple):
        operator = argument[0]
        right = self.__pop()
        left = self.__pop()

        self.__log(f"Arithmetic Operation: ({operator}), will be done between popped values")

        if operator == TokenType.PLUS:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                self.__push(left + right)
            elif isinstance(left, str) and isinstance(right, str):
                self.__push(left + right)
            else:
                raise RuntimeError(f"Invalid operator '{operator.value}', with types: ")

        elif operator == TokenType.MINUS:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                self.__push(left - right)
            else:
                raise RuntimeError(f"Invalid operator '{operator.value}', with types: ")

        elif operator == TokenType.MULTIPLY:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                self.__push(left * right)
            else:
                raise RuntimeError(f"Invalid operator '{operator.value}', with types: ")

        elif operator == TokenType.DIVIDE:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                self.__push(left / right)
            else:
                raise RuntimeError(f"Invalid operator '{operator.value}', with types: ")

        elif operator == TokenType.EXPONENT:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                self.__push(left ** right)
            else:
                raise RuntimeError(f"Invalid operator '{operator.value}', with types: ")

        else:
            raise RuntimeError(f"Unexpected operator {operator}")

    def __compare_op(self, argument: tuple):
        operator = argument[0]
        right = self.__pop()
        left = self.__pop()

        self.__log(f"Comparison Operation: ({operator}), will be done between popped values")

        if operator == TokenType.EQUAL:
            self.__push(int(left == right))

        elif operator == TokenType.NOT_EQUAL:
            self.__push(int(left != right))

        elif operator == TokenType.LESS_THAN:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                self.__push(int(left < right))
            else:
                raise RuntimeError(f"Invalid operator '{operator.value}', with types: ")

        elif operator == TokenType.GREATER_THAN:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                self.__push(int(left > right))
            else:
                raise RuntimeError(f"Invalid operator '{operator.value}', with types: ")

        elif operator == TokenType.LESS_THAN_EQUAL:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                self.__push(int(left <= right))
            else:
                raise RuntimeError(f"Invalid operator '{operator.value}', with types: ")

        elif operator == TokenType.GREATER_THAN_EQUAL:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                self.__push(int(left >= right))
            else:
                raise RuntimeError(f"Invalid operator '{operator.value}', with types: ")

        else:
            raise RuntimeError(f"Unexpected operator {operator}")

    def __unary_op(self, argument: tuple):
        operator = argument[0]
        operand = self.__pop()

        self.__log(f"Unary Operation '{operator}', will be done between popped values")

        if operator == TokenType.MINUS:
            if isinstance(operand, (int, float)):
                self.__push(-operand)

            else:
                raise RuntimeError(f"Invalid operator '{operator}' with type: ")

    def __call(self, argument: tuple):
        starting_address, arity, local_slots_count, native_impl = argument

        args = [self.__pop() for num in range(arity)].__reversed__()

        if native_impl is not None:
            self.__push(native_impl(*args))
            return

        frame = Frame(local_slots_count, self.__program_counter + 1)

        frame.locals[0 : arity] = args
        self.__push_frame(frame)

        self.__program_counter = starting_address
        self.__log(f"PC set to address: {self.__program_counter}")

    def __return(self, argument: tuple) -> object:
        self.__program_counter = self.__call_stack[-1].return_address
        self.__log(f"PC set to address: {self.__program_counter}")
        self.__pop_frame()

    def __jump(self, argument: tuple):
        self.__program_counter = argument[0]
        self.__log(f"PC set to address: ({argument[0]}), Jump done")

    def __jump_if_false(self, argument: tuple):
        boolean = self.__pop()
        if boolean == 0:
            self.__program_counter = argument[0]
            self.__log(f"PC is set to address: ({argument[0]}), Jump If False done")
            return
        self.__log("PC will not be set, Jump If False done")

    def __pop_instruction(self, argument: tuple):
        del self.__stack[-1]

    def __halt(self, argument: tuple):
        self.__log("Program Halt (stop)")
        self.__is_halt = True

    # ================ Stack Call Methods ================
    def __push_frame(self, frame: Frame):
        self.__call_stack.append(frame)
        self.__log(f"{frame}, pushed to call stack")

    def __pop_frame(self):
        self.__log(f"{self.__call_stack[-1]}, popped from call stack")
        del self.__call_stack[-1]

    def __current_frame(self) -> Frame:
        self.__log(f"current call frame is: {self.__call_stack[-1]}")
        return self.__call_stack[-1]

    # ============= Stack Operation Methods =============
    def __push(self, value):
        self.__stack.append(value)
        self.__log(f"{value} pushed to the stack")

    def __pop(self) -> object:
        stack_top = self.__stack[-1]
        del self.__stack[-1]
        self.__log(f"{stack_top.__repr__()} popped from the stack")
        return stack_top


    # ================ Utility Methods =================
    def __log(self, msg: str):
        if not self.__enable_tracing:
            return
        print(msg)




if __name__ == '__main__':
    pass