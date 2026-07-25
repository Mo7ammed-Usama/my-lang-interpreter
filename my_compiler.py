from my_builtins import builtins, FunctionSignature
from my_instruction import *
from my_instruction import Instruction
from my_statement import *
from my_expr import *

from my_token import ARITHMETIC_TOKENS

from dataclasses import dataclass



@dataclass(slots=True)
class Scope:
    variables: dict[str, tuple[int, object]]
    is_function_scope: bool = False
    is_nested: bool = False

@dataclass(slots=True)
class LoopContext:
    continue_jmp_target: int
    break_jmp_addresses: list[int]


class Compiler:
    def __init__(self, parse_tree: tuple[Stmt, ...]):
        self.__parse_tree = parse_tree
        self.__instructions: list[Instruction] = []

        self.__constants : dict[object, int] = {}
        self.__scopes_stack: list[Scope] = [Scope({})]
        self.__loop_stack: list[LoopContext] = []
        self.__function_signatures : dict[str, FunctionSignature] = {}

        self.__node_to_method = {
            # =========== Statements ============
            FuncDeclaration : self.__func_declaration_stmt,
            ReturnStmt : self.__return_stmt,

            VarDeclaration : self.__var_declaration_stmt,
            VarUpdate : self.__var_update_stmt,

            IfStmt : self.__if_stmt,

            WhileStmt : self.__while_stmt,
            ForStmt : self.__for_stmt,
            BreakStmt : self.__break_stmt,
            ContinueStmt : self.__continue_stmt,

            ExprStmt : self.__expr_stmt,
            # ===================================

            # =========== Expressions ===========
            Binary : self.__binary_expr,
            FuncCall : self.__func_call_expr,
            VarReference : self.__var_reference_expr,
            Unary : self.__unary_expr,

            Integer : self.__literal_expr,
            Double : self.__literal_expr,
            String : self.__literal_expr,
            Boolean : self.__literal_expr,
            Null : self.__literal_expr
            # ===================================
        }

    # ============= Main Compiling Method ==============
    def compile(self) -> tuple[Instruction, ...]:
        parse_tree = self.__parse_tree

        self.__function_signatures.update(builtins)

        entry_jmp_address = self.__emit(OpCode.JUMP, ())

        global_scope = self.__scopes_stack[0]

        for node in parse_tree:
            if isinstance(node, VarDeclaration):
                global_scope.variables[node.name] = (len(global_scope.variables), node.value)

            elif isinstance(node, (IfStmt, WhileStmt, ForStmt)):
                for micro in node.block:
                    if isinstance(micro, VarDeclaration):
                        global_scope.variables[micro.name] = (len(global_scope.variables), micro.value)

        for node in parse_tree:
            if isinstance(node, FuncDeclaration):
                self.__func_declaration_stmt(node, 0)

        self.__patch_jump(entry_jmp_address, len(self.__instructions))

        for node in parse_tree:
            if not isinstance(node, FuncDeclaration):
                self.__compile_node(node, 0)

        self.__emit(OpCode.HALT, ())

        return tuple(self.__instructions)

    @property
    def constants(self) -> tuple[object, ...]:
        return tuple(self.__constants)
    @property
    def global_slots_count(self) -> int:
        return len(self.__scopes_stack[0].variables)
    @property
    def function_signatures(self):
        return self.__function_signatures

    # ======= Core Instruction Emitting Methods ========
    def __emit(self, op_code: OpCode, argument: tuple) -> int:
        self.__instructions.append(Instruction(op_code, argument))
        return len(self.__instructions) - 1

    def __patch_jump(self, instruction_address: int, target_address: int):
        self.__instructions[instruction_address].argument = (target_address,)

    def __add_const(self, value) -> int:
        if value in self.__constants:
            return self.__constants[value]

        slot = len(self.__constants)
        self.__constants[value] = slot
        return slot

    def __resolve_variable(self, name: str, scope_index: int):
        depth = 0

        while scope_index >= 0:
            cur_scope = self.__scopes_stack[scope_index]

            if name not in cur_scope.variables:
                if cur_scope.is_nested:
                    scope_index -= 1
                    depth += 1
                    continue

                elif scope_index != 0:
                    depth = scope_index + 1
                    scope_index = 0
                    continue

                else:
                    break

            return depth

        raise RuntimeError(f"Unresolved variable reference '{name}'")

    def __compile_node(self, node: Stmt | Expr, scope_index: int):
        method = self.__node_to_method.get(node.__class__)

        if method is None:
            raise RuntimeError(f"Unexpected node: ( {node} )")

        method(node, scope_index)

    # ============== Statements Compiling ==============
    def __func_declaration_stmt(self, node: FuncDeclaration, scope_index: int):
        cur_scope = self.__scopes_stack[scope_index]
        is_nested_function = True if cur_scope.is_function_scope else False

        stmt_starting_address = len(self.__instructions)

        local_scope_index = len(self.__scopes_stack)
        self.__scopes_stack.append(Scope({}, True, is_nested_function))
        local_scope = self.__scopes_stack[-1]

        for param in node.param_names:
            local_scope.variables[param] = (len(local_scope.variables), None)

        func_block_skip_jmp_address = -1
        if is_nested_function:
            func_block_skip_jmp_address = self.__emit(OpCode.JUMP, ())
            stmt_starting_address += 1

        self.__function_signatures[node.name] = FunctionSignature(stmt_starting_address, node.param_names, -1, None)

        for stmt in node.block:
            self.__compile_node(stmt, local_scope_index)
        if is_nested_function:
            self.__patch_jump(func_block_skip_jmp_address, len(self.__instructions))

        self.__function_signatures[node.name].local_slots_count = len(local_scope.variables)

    def __return_stmt(self, node: ReturnStmt, scope_index: int):
        self.__compile_node(node.value, scope_index)
        self.__emit(OpCode.RETURN, ())

    def __var_declaration_stmt(self, node: VarDeclaration, scope_index: int):
        cur_scope = self.__scopes_stack[scope_index]
        if node.name in cur_scope.variables and cur_scope != self.__scopes_stack[0]:
            raise RuntimeError(f"Variable '{node.name}' is defined already, update it instead of typing 'var' before variable Identifier")

        self.__compile_node(node.value, scope_index)

        store_slot = cur_scope.variables[node.name][0] if node.name in cur_scope.variables else len(cur_scope.variables)

        op_code = OpCode.STORE_LOCAL if cur_scope.is_function_scope else OpCode.STORE_GLOBAL
        argument = (0, store_slot) if op_code == OpCode.STORE_LOCAL else (store_slot,)

        self.__emit(op_code, argument)

        if cur_scope == self.__scopes_stack[0]:
            return
        cur_scope.variables[node.name] = (store_slot, node.value)

    def __var_update_stmt(self, node: VarUpdate, scope_index: int):
        depth = self.__resolve_variable(node.name, scope_index)
        cur_scope = self.__scopes_stack[scope_index - depth]

        store_slot = cur_scope.variables[node.name][0]

        self.__compile_node(node.new_value, scope_index)

        op_code = OpCode.STORE_LOCAL if cur_scope.is_function_scope else OpCode.STORE_GLOBAL
        argument = (depth, store_slot) if op_code == OpCode.STORE_LOCAL else (store_slot,)
        self.__emit(op_code, argument)

    def __if_stmt(self, node: IfStmt, scope_index: int):
        self.__compile_node(node.condition, scope_index)
        condition_jmp_address = self.__emit(OpCode.JUMP_IF_FALSE, ())

        for stmt in node.block:
            self.__compile_node(stmt, scope_index)

        stmt_end_address = len(self.__instructions)
        self.__patch_jump(condition_jmp_address, stmt_end_address)


    def __while_stmt(self, node: WhileStmt, scope_index: int):
        stmt_starting_address = len(self.__instructions)

        self.__compile_node(node.condition, scope_index)
        condition_jmp_address = self.__emit(OpCode.JUMP_IF_FALSE, ())

        # context_index = len(self.__loop_stack)
        self.__loop_stack.append(LoopContext(stmt_starting_address, []))
        for stmt in node.block:
            self.__compile_node(stmt, scope_index)

        self.__emit(OpCode.JUMP, (stmt_starting_address,))

        stmt_end_address = len(self.__instructions)
        self.__patch_jump(condition_jmp_address, stmt_end_address)

        for break_jmp_instruction_address in self.__loop_stack[-1].break_jmp_addresses:
            self.__patch_jump(break_jmp_instruction_address, stmt_end_address)

        del self.__loop_stack[-1]

    def __for_stmt(self, node: ForStmt, scope_index: int):
        pass

    def __break_stmt(self, node: BreakStmt, scope_index: int):
        self.__loop_stack[-1].break_jmp_addresses.append(self.__emit(OpCode.JUMP, ()))

    def __continue_stmt(self, node: ContinueStmt, scope_index: int):
        self.__emit(OpCode.JUMP, (self.__loop_stack[-1].continue_jmp_target,))


    def __expr_stmt(self, node: ExprStmt, scope_index: int):
        self.__compile_node(node.expression, scope_index)

    # ============= Expressions Compiling ==============
    def __binary_expr(self, node: Binary, scope_index: int):
        if node.operator.type not in ARITHMETIC_TOKENS:
            op_code = OpCode.COMPARE_OP
        else:
            op_code = OpCode.BINARY_OP

        self.__compile_node(node.left, scope_index)
        self.__compile_node(node.right, scope_index)

        self.__emit(op_code, (node.operator.type,))

    def __func_call_expr(self, node: FuncCall, scope_index: int):
        if node.name not in self.__function_signatures:
            raise RuntimeError(f"Calling an undefined function '{node.name}'")
        signature = self.__function_signatures[node.name]

        args_len = len(node.args)
        param_names_len = len(signature.param_names) if signature.param_names is not None else None
        if param_names_len is not None and args_len != param_names_len:
            raise RuntimeError(f"Expected ({param_names_len}) arguments for '{node.name}' Function , got ({args_len})")

        for expr in node.args:
            self.__compile_node(expr, scope_index)

        self.__emit(OpCode.CALL, (signature.starting_address, args_len, signature.local_slots_count, signature.native_impl))

    def __var_reference_expr(self, node: VarReference, scope_index: int):
        depth = self.__resolve_variable(node.name, scope_index)
        cur_scope = self.__scopes_stack[scope_index - depth]

        load_slot = cur_scope.variables[node.name][0]

        op_code = OpCode.LOAD_LOCAL if cur_scope.is_function_scope else OpCode.LOAD_GLOBAL
        argument = (depth, load_slot) if op_code == OpCode.LOAD_LOCAL else (load_slot,)
        self.__emit(op_code, argument)

    def __unary_expr(self, node: Unary, scope_index: int):
        self.__compile_node(node.operand, scope_index)
        self.__emit(OpCode.UNARY_OP, (node.operator.type,))

    def __literal_expr(self, node: Literal, scope_index: int):
        if isinstance(node, Null):
            self.__emit(OpCode.LOAD_NULL, ())
        else:
            address = self.__add_const(node.value)
            self.__emit(OpCode.LOAD_CONST, (address,))

    # ================ Utility Methods =================
    def get_info(self) -> str:
        info = "Instructions: \n"
        for index, instruction in enumerate(self.__instructions):
            end = "\n\n" if instruction.op_code == OpCode.RETURN or index == 0 else "\n"
            info += f"[{index}] {instruction}{end}"

        info += "\nConstants:\n"
        for const_num, (const, slot) in enumerate(self.__constants.items()):
            info += f"\t[{const_num}] {const.__repr__()} : slot ( {slot} )\n"

        info += "\nVariables:"
        for scope_num, scope in enumerate(self.__scopes_stack):
            info += "\n\tGlobal Variables:\n" if scope_num == 0 else f"\n\tLocal Variables ({scope_num}):\n"

            for var_num, (name, store_info) in enumerate(scope.variables.items()):
                info += f"\t\t[{var_num}] {name} : ( slot= {store_info[0]}, value= {store_info[1].__repr__()} )\n"

        info += "\nFunctions Signatures:\n"
        for signature_num, (name, signature) in enumerate(self.__function_signatures.items()):
            info += f"\t[{signature_num}] {name} : {signature}\n"

        info += "\nLoop Stack:\n"
        for context_num, loop_context in enumerate(self.__loop_stack):
            info += f"\t[{context_num}] {loop_context}\n"

        return info


if __name__ == '__main__':
    pass