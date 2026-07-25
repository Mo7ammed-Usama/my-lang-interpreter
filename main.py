def main():
    from time import perf_counter_ns

    from my_compiler import Compiler
    from my_lexer import Lexer
    from my_parser import Parser
    from my_virtual_machine import VirtualMachine


    # ================== Source Code ===================
    with open("source.txt", "r", encoding="utf-8") as source_file:
        source_code = source_file.read()

    start = perf_counter_ns()
    # print(" Source Code ".center(100, "="))
    # print(source_code)
    # ==================================================


    # ===================== Lexer ======================
    tokens = Lexer(source_code).scan()

    # print("\n" + " Tokens ".center(100, "="))
    # for index, token in enumerate(tokens):
    #     end = "\n\n\n" if token.type in (TokenType.CLOSE_BRACE, TokenType.EOF) else "\n\n" if token.type == TokenType.SEMI_COLON else "\n"
    #     print(f"[{index}] {token}", end=end)
    # ==================================================


    # ===================== Parser =====================
    ast = Parser(tokens, True).parse()

    # print("\n" + " Abstract Syntax Tree (Parse Tree) ".center(100, "="))
    # print(*ast, sep="\n\n", end="\n\n")
    # ==================================================


    # ==================== Compiler ====================
    compiler = Compiler(ast)

    instructions = compiler.compile()

    constants = compiler.constants
    global_slots_count = compiler.global_slots_count
    function_signatures = compiler.function_signatures

    # print("\n" + " Instructions ".center(100, "="))
    # print(compiler.get_info())
    # ==================================================


    # ================ Virtual Machine =================
    virtual_machine = VirtualMachine(instructions, constants, global_slots_count, function_signatures, False)
    final_stack = virtual_machine.run()
    # print("\n" + " Final Stack ".center(100, "="))
    # print(final_stack)
    # ==================================================



    # print("\n" + " Process Time ".center(100, "="))

    end = perf_counter_ns()
    duration = end - start

    print(f"Processed in: {duration / 1_000_000} ms ({duration / 1_000_000_000} s)")


if __name__ == '__main__':
    main()
