from my_instruction import *
from my_instruction import Instruction
from my_statement import *
from my_expr import *
from dataclasses import dataclass

from my_token import ARITHMETIC_TOKENS


@dataclass(slots=True)
class FunctionSignature:
    address: int
    param_names: tuple[str, ...]

@dataclass(slots=True)
class Scope:
    variables: dict[str, int]
    is_function_scope: bool = False


class Compiler:
    def __init__(self, parse_tree: tuple[Stmt, ...]):
        self.__parse_tree = parse_tree
        self.__instructions: list[Instruction] = []

        self.__global_scope = Scope({})
        self.__constants : dict[object, int] = {}
        self.__function_signatures : dict[str, FunctionSignature] = {}

        self.__cur_loop_break_jmp_addresses = []
        self.__cur_loop_continue_jmp_addresses = []


    # ============= Main Compiling Method ==============
    def compile(self) -> tuple[Instruction, ...]:
        parse_tree = self.__parse_tree

        entry_jmp_address = self.__emit(OpCode.JUMP)

        for node in parse_tree:
            if isinstance(node, VarDeclaration):
                self.__var_declaration_stmt(node, self.__global_scope)
            elif isinstance(node, FuncDeclaration):
                self.__func_declaration_stmt(node)

        self.__patch_jump(entry_jmp_address, len(self.__instructions))

        for node in parse_tree:
            if not isinstance(node, (VarDeclaration, FuncDeclaration)):
                self.__compile_node(node, self.__global_scope)
        self.__emit(OpCode.HALT)

        return tuple(self.__instructions)

    # ======= Core Instruction Emitting Methods ========
    def __emit(self, op_code: OpCode, operand: object = None) -> int:
        self.__instructions.append(Instruction(op_code, operand))
        return len(self.__instructions) - 1

    def __patch_jump(self, instruction_address: int, target_address: int):
        self.__instructions[instruction_address].argument = target_address

    def __add_const(self, value) -> int:
        if value in self.__constants:
            return self.__constants[value]

        slot = len(self.__constants)
        self.__constants[value] = slot
        return slot

    def __compile_node(self, node: Stmt | Expr, scope):
        if isinstance(node, Stmt):
            self.__compile_stmt(node, scope)

        elif isinstance(node, Expr):
            self.__compile_expr(node, scope)

        else:
            raise RuntimeError(f"Unexpected node: {node}")

    def __compile_stmt(self, node: Stmt, scope):
        if isinstance(node, FuncDeclaration):
            self.__func_declaration_stmt(node)
        elif isinstance(node, ReturnStmt):
            self.__return_stmt(node, scope)

        elif isinstance(node, VarDeclaration):
            self.__var_declaration_stmt(node, scope)
        elif isinstance(node, VarUpdate):
            self.__var_update_stmt(node, scope)

        elif isinstance(node, IfStmt):
            self.__if_stmt(node, scope)

        elif isinstance(node, WhileStmt):
            self.__while_stmt(node, scope)
        elif isinstance(node, ForStmt):
            self.__for_stmt(node, scope)
        elif isinstance(node, BreakStmt):
            self.__break_stmt()
        elif isinstance(node, ContinueStmt):
            self.__continue_stmt()

        elif isinstance(node, ExprStmt):
            self.__expr_stmt(node, scope)

    def __compile_expr(self, node: Expr, scope):
        if isinstance(node, Binary):
            self.__binary_expr(node, scope)
        elif isinstance(node, FuncCall):
            self.__func_call_expr(node, scope)
        elif isinstance(node, VarReference):
            self.__var_reference_expr(node, scope)
        elif isinstance(node, Unary):
            self.__unary_expr(node, scope)
        elif isinstance(node, Literal):
            self.__literal_expr(node)

    # ============== Statements Compiling ==============
    def __func_declaration_stmt(self, node: FuncDeclaration):
        stmt_starting_address = len(self.__instructions)
        self.__function_signatures[node.name] = FunctionSignature(stmt_starting_address, node.param_names)

        local_scope = Scope({}, True)
        for param in node.param_names:
            local_scope.variables[param] = len(local_scope.variables)

        for stmt in node.block:
            self.__compile_node(stmt, local_scope)


    def __return_stmt(self, node: ReturnStmt, scope):
        self.__compile_node(node.value, scope)
        self.__emit(OpCode.RETURN)


    def __var_declaration_stmt(self, node: VarDeclaration, scope):
        if node.name in scope.variables:
            raise RuntimeError(f"Variable '{node.name}' is defined already, update it instead by typing 'var' before variable Identifier")

        self.__compile_node(node.value, scope)

        store_slot = len(scope.variables)
        op_code = OpCode.STORE_LOCAL if scope.is_function_scope else OpCode.STORE_GLOBAL

        self.__emit(op_code, store_slot)

        scope.variables[node.name] = store_slot

    def __var_update_stmt(self, node: VarUpdate, scope: Scope):
        if node.name in scope.variables:
            cur_scope = scope
        elif node.name in self.__global_scope.variables:
            cur_scope = self.__global_scope
        else:
            raise RuntimeError(f"Updating an undefined variable '{node.name}'")

        store_slot = cur_scope.variables[node.name]

        self.__compile_node(node.new_value, cur_scope)

        op_code = OpCode.STORE_LOCAL if cur_scope.is_function_scope else OpCode.STORE_GLOBAL
        self.__emit(op_code, store_slot)

    def __if_stmt(self, node: IfStmt, scope):
        self.__compile_node(node.condition, scope)
        condition_jmp_address = self.__emit(OpCode.JUMP_IF_FALSE)

        for stmt in node.block:
            self.__compile_node(stmt, scope)

        stmt_end_address = len(self.__instructions)
        self.__patch_jump(condition_jmp_address, stmt_end_address)

    def __while_stmt(self, node: WhileStmt, scope):
        stmt_starting_address = len(self.__instructions)

        self.__compile_node(node.condition, scope)
        condition_jmp_address = self.__emit(OpCode.JUMP_IF_FALSE)

        for stmt in node.block:
            self.__compile_node(stmt, scope)

        self.__emit(OpCode.JUMP, stmt_starting_address)

        stmt_end_address = len(self.__instructions)
        self.__patch_jump(condition_jmp_address, stmt_end_address)

        for instruction_address in self.__cur_loop_break_jmp_addresses:
            self.__patch_jump(instruction_address, stmt_end_address)
        for instruction_address in self.__cur_loop_continue_jmp_addresses:
            self.__patch_jump(instruction_address, stmt_starting_address)

    def __for_stmt(self, node: ForStmt, scope):
        pass

    def __break_stmt(self):
        self.__cur_loop_break_jmp_addresses.append(self.__emit(OpCode.JUMP))

    def __continue_stmt(self):
        self.__cur_loop_continue_jmp_addresses.append(self.__emit(OpCode.JUMP))


    def __expr_stmt(self, node: ExprStmt, scope):
        self.__compile_node(node.expression, scope)

    # ============= Expressions Compiling ==============
    def __binary_expr(self, node: Binary, scope):
        self.__compile_node(node.left, scope)
        self.__compile_node(node.right, scope)
        if node.operator.type not in ARITHMETIC_TOKENS:
            op_code = OpCode.COMPARE_OP
        else:
            op_code = OpCode.BINARY_OP

        self.__emit(op_code, node.operator.type)

    def __func_call_expr(self, node: FuncCall, scope):
        if node.name not in self.__function_signatures:
            raise RuntimeError(f"Calling an undefined function '{node.name}'")
        signature = self.__function_signatures[node.name]

        args_len = len(node.args)
        param_names_len = len(signature.param_names)
        if args_len != param_names_len:
            raise RuntimeError(f"Expected ({param_names_len}) arguments for '{node.name}' Function , got ({args_len})")

        for expr in node.args:
            self.__compile_node(expr, scope)

        self.__emit(OpCode.CALL, node.name)

    def __var_reference_expr(self, node: VarReference, scope):
        if node.name in scope.variables:
            cur_scope = scope
        elif node.name in self.__global_scope.variables:
            cur_scope = self.__global_scope
        else:
            raise RuntimeError(f"Updating an undefined variable '{node.name}'")

        load_slot = cur_scope.variables[node.name]
        cur_scope.variables[node.name] = load_slot

        op_code = OpCode.LOAD_LOCAL if cur_scope.is_function_scope else OpCode.LOAD_GLOBAL
        self.__emit(op_code, load_slot)

    def __unary_expr(self, node: Unary, scope):
        self.__compile_node(node.operand, scope)
        self.__emit(OpCode.UNARY_OP, node.operator.type)

    def __literal_expr(self, node: Literal):
        if isinstance(node, Null):
            self.__emit(OpCode.LOAD_NULL)
        else:
            address = self.__add_const(node.value)
            self.__emit(OpCode.LOAD_CONST, address)


    def get_info(self):
        info = "Constants:\n"

        for const, slot in self.__constants.items():
            info += f"const ({const.__repr__()}) : slot ({slot})\n"

        info += "\nGlobal Variables:\n"

        for name, slot in self.__global_scope.variables.items():
            info += f"var name ({name}) : slot ({slot})\n"

        info += "\nFunctions Signatures:\n"

        for name, signature in self.__function_signatures.items():
            info += f"func name({name}) : {signature}\n"

        info += f"Current loop 'break' jump Address:\n{self.__cur_loop_break_jmp_addresses}\n"
        info += f"Current loop 'continue' jump Address:\n{self.__cur_loop_continue_jmp_addresses}"

        return info
