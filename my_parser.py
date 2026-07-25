"""
Context Free Grammar (CFG):


* --> Can happen any number of times
| --> Or
? --> Optional


EqualityExpression -->   ComparisonExpression ( ( '==' | '!=' ) ComparisonExpression )?
ComparisonExpression --> Expression ( ( '==' | '!=' | '<' | '>' | '<=' | '>=' ) Expression )?
Expression --> Term ( '+' | '-' Term )*
Term -->       Factor ( '*' | '/' Factor )*
Factor -->     Literal value | Identifier | '(' Expression ')'

Identifier -->    [a-z][a-z]*
Literal Value --> Integer | Double | String | Boolean | Null

Integer --> [0-9][0-9]*
Double -->  Integer '.' Integer
String -->  ' " ' | " ' " (Anything) ' " ' | " ' "
Boolean --> 'True' | 'False'
Null -->    'Null'


Program --> Statement*

Statement --> ExpressionStatement |
              VariableDeclaration |
              VariableUpdate |
              IfStatement |
              WhileStatement |
              ForStatement |
              BreakStatement |
              ContinueStatement |
              FunctionDeclaration |
              ReturnStatement

ExpressionStatement --> ComparissonExpression ';'

IfStatement -->       'if' '(' EqualityExpression ')' '{' Statement* '}'
WhileStatement -->    'while' '(' EqualityExpression ')' '{' Statement* '}'
ForStatement -->      'for' '(' Identifier in Iterable ')' '{' Statement* '}'
BreakStatement -->    'break' ';'
ContinueStatement --> 'continue' ';'

VariableDeclaration --> 'var' Identifier '=' EqualityExpression ';'
VariableUpdate -->      Identifier '=' EqualityExpression ';'

FunctionDeclaration --> 'func' '(' Identifier ( ',' Identifier )* ')' '{' Statement* '}'
ReturnStatement -->     'return' EqualityExpression ';'


Iterable --> ... (not defined)

Data Structure --> List | Tuple | Dictionary | Set

List -->       '[' ( EqualityExpression ( ',' EqualityExpression )* )? ']'
Tuple -->      '(' EqualityExpression ',' ( EqualityExpression ',' )* ')'
Set -->        '{' EqualityExpression ( ',' EqualityExpression )* '}'
Dictionary --> '{' ( EqualityExpression ':' EqualityExpression ( ',' EqualityExpression ':' EqualityExpression )* )?  '}'
"""

from my_token import *
from my_expr import *
from my_statement import *


class Parser:
    def __init__(self, tokens: tuple[Token, ...], enable_log: bool = False):
        self.__tokens = tokens
        self.__enable_log = enable_log
        self.__cur_index = 0

        self.__is_loop_block = False
        self.__is_function_block = False

    # ========================================= Parsing Methods ==========================================
    # ============== Main Parsing Method ===============
    def parse(self) -> tuple[Stmt, ...]:
        statements = []
        while not self.__is_at_end():
            statements.append(self.__declaration())

        self.__consume(TokenType.EOF, "Expected EOF Token to terminate the program")
        return tuple(statements)

    # =============== Statement Parsing ================
    def __declaration(self) -> Stmt:
        if self.__match(TokenType.FUNC):
            return self.__func_declaration()

        return self.__parse_statement()

    def __parse_statement(self) -> Stmt:
        if self.__match(TokenType.FUNC):
            return self.__func_declaration()

        if self.__match(TokenType.VAR):
            return self.__var_declaration()
        if self.__check(TokenType.IDENTIFIER) and self.__peek(1).type in ASSIGNING_TOKENS:
            return self.__var_update()

        if self.__match(TokenType.IF):
            return self.__if_statement()

        if self.__match(TokenType.WHILE):
            return self.__while_statement()
        if self.__match(TokenType.FOR):
            return self.__for_statement()
        if self.__match(TokenType.BREAK):
            return self.__break_statement()
        if self.__match(TokenType.CONTINUE):
            return self.__continue_statement()

        if self.__match(TokenType.RETURN):
            return self.__return_statement()

        return self.__expr_statement()

    def __expr_statement(self) -> Stmt:
        expression = self.__expression()
        self.__consume(TokenType.SEMI_COLON, "Expected ( ';' Semi Colon ) after the Statement")
        return ExprStmt(expression)

    # ======= Function Statements =======
    def __func_declaration(self) -> Stmt:
        self.__is_function_block = True

        name = self.__consume(TokenType.IDENTIFIER, "Expected an Identifier (name) to the Function").literal_value

        self.__consume(TokenType.OPEN_PARENTHESES, "Expected ( '(' Open Parentheses ) after the function Identifier")
        parameters_names = []
        while not self.__is_at_end() and not self.__match(TokenType.CLOSE_PARENTHESES):
            if len(parameters_names) > 0:
                self.__consume(TokenType.COMMA, f"Expected ( ',' Comma ) after '{self.__peek()}'")
            parameters_names.append(self.__advance().literal_value)

        self.__consume(TokenType.OPEN_BRACE, "Expected ( '{' Open Brace ) to assign function block")
        block = []
        while not self.__is_at_end() and not self.__match(TokenType.CLOSE_BRACE):
            block.append(self.__parse_statement())
            self.__is_function_block = True

        if any(isinstance(stmt, ReturnStmt) for stmt in block):
            self.__is_function_block = False
            return FuncDeclaration(name, tuple(parameters_names), tuple(block))

        block.append(ReturnStmt(Null(None)))
        return FuncDeclaration(name, tuple(parameters_names), tuple(block))

    def __return_statement(self) -> Stmt:
        if not self.__is_function_block:
            raise RuntimeError("Return Statement should be included inside a Function Declaration")
        expression = self.__expression()
        self.__consume(TokenType.SEMI_COLON, "Expected ( ';' Semi Colon ) after the Statement")
        return ReturnStmt(expression)

    # ======= Variable Statements =======
    def __var_declaration(self) -> Stmt:
        name = self.__consume(TokenType.IDENTIFIER, "Expected an Identifier (name) to the Variable").literal_value
        self.__consume(TokenType.ASSIGN, f"Expected ( '=' Equal ) to assign a value to '{name}' Variable")
        expression = self.__expression()

        self.__consume(TokenType.SEMI_COLON, "Expected ( ';' Semi Colon ) after the Statement")
        return VarDeclaration(name, expression)

    def __var_update(self) -> Stmt:
        name = self.__advance().literal_value
        assign_token_type = self.__advance().type
        op_token_type = ASSIGNING_TOKENS_TO_BASIC[assign_token_type]

        if assign_token_type in (TokenType.PLUS_PLUS, TokenType.MINUS_MINUS):
            expr_right_side = Integer(1)
        else:
            expr_right_side = self.__expression()

        self.__consume(TokenType.SEMI_COLON, "Expected ( ';' Semi Colon ) after the Statement")

        if assign_token_type == TokenType.ASSIGN:
            expression = expr_right_side
        else:
            expression = Binary(VarReference(name), Token(op_token_type), expr_right_side)

        return VarUpdate(name, expression)

    # ===== Conditional Statements ======
    def __if_statement(self) -> Stmt:
        self.__consume(TokenType.OPEN_PARENTHESES, "Expected ( '(' Open Parentheses ) to assign If Statement condition")
        condition = self.__expression()
        self.__consume(TokenType.CLOSE_PARENTHESES,
                       "Expected ( ')' Close Parentheses ) after ( '(' Open Parentheses ) in If Statement condition")

        self.__consume(TokenType.OPEN_BRACE, "Expected ( '{' Open Brace ) to assign If Statement block")
        block = []
        while not self.__is_at_end() and not self.__check(TokenType.CLOSE_BRACE):
            block.append(self.__parse_statement())
        self.__consume(TokenType.CLOSE_BRACE, "Expected ( '{' Close Brace ) to assign If Statement block")

        return IfStmt(condition, tuple(block))

    # ========= Loop Statements =========
    def __while_statement(self) -> Stmt:
        if self.__is_loop_block:
            is_nested_loop = True
        else:
            self.__is_loop_block = True
            is_nested_loop = False

        self.__consume(TokenType.OPEN_PARENTHESES,
                       "Expected ( '(' Open Parentheses ) to assign While Statement condition")
        condition = self.__expression()
        self.__consume(TokenType.CLOSE_PARENTHESES,
                       "Expected ( ')' Close Parentheses ) after ( '(' Open Parentheses ) in While Statement condition")

        self.__consume(TokenType.OPEN_BRACE, "Expected ( '{' Open Brace ) to assign While Statement block")
        block = []
        while not self.__is_at_end() and not self.__check(TokenType.CLOSE_BRACE):
            block.append(self.__parse_statement())
        self.__consume(TokenType.CLOSE_BRACE, "Expected ( '{' Close Brace ) to assign While Statement block")

        if not is_nested_loop:
            self.__is_loop_block = False

        return WhileStmt(condition, tuple(block))

    def __for_statement(self) -> Stmt:
        pass

    def __break_statement(self) -> Stmt:
        if not self.__is_loop_block:
            raise RuntimeError("Break Statement should be included inside a While or For loop")
        self.__consume(TokenType.SEMI_COLON, "Expected ( ';' Semi Colon ) after the Statement")
        return BreakStmt()

    def __continue_statement(self) -> Stmt:
        if not self.__is_loop_block:
            raise RuntimeError("Continue Statement should be included inside a While or For loop")
        self.__consume(TokenType.SEMI_COLON, "Expected ( ';' Semi Colon ) after the Statement")
        return ContinueStmt()

    # =============== Expression Parsing ===============
    def __expression(self) -> Expr:
        working_expr = self.__comparison()

        while self.__match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self.__peek(-1)
            parsed_expression = self.__comparison()

            working_expr = Binary(working_expr, operator, parsed_expression)

        return working_expr

    def __comparison(self) -> Expr:
        working_expr = self.__term()

        while self.__match(TokenType.LESS_THAN, TokenType.GREATER_THAN, TokenType.LESS_THAN_EQUAL,
                           TokenType.GREATER_THAN_EQUAL):
            operator = self.__peek(-1)
            parsed_expression = self.__term()

            working_expr = Binary(working_expr, operator, parsed_expression)

        return working_expr

    def __term(self) -> Expr:
        working_expr = self.__factor()

        while self.__match(TokenType.PLUS, TokenType.MINUS):
            operator = self.__peek(-1)
            parsed_expression = self.__factor()

            working_expr = Binary(working_expr, operator, parsed_expression)

        return working_expr

    def __factor(self) -> Expr:
        working_expr = self.__exponent()

        while self.__match(TokenType.MULTIPLY, TokenType.DIVIDE):
            operator = self.__peek(-1)
            parsed_term = self.__exponent()

            working_expr = Binary(working_expr, operator, parsed_term)

        return working_expr

    def __exponent(self) -> Expr:
        working_expr = self.__unary()

        while self.__match(TokenType.EXPONENT):
            operator = self.__peek(-1)
            parsed_expression = self.__unary()

            working_expr = Binary(working_expr, operator, parsed_expression)

        return working_expr

    def __unary(self) -> Expr:
        while self.__match(TokenType.MINUS):
            operator = self.__peek(-1)
            working_expr = self.__unary()
            return Unary(working_expr, operator)

        while self.__match(TokenType.PLUS):
            working_expr = self.__unary()
            return working_expr

        working_expr = self.__primary()
        return working_expr

    def __primary(self) -> Expr:
        token = self.__peek()

        # '(' Expression ')'
        if self.__match(TokenType.OPEN_PARENTHESES):
            expression = self.__expression()
            self.__consume(TokenType.CLOSE_PARENTHESES,
                           "Expected ( ')' Close Parentheses ) after the ( '(' Open Parentheses ) to terminate the expression")
            return expression

        # Identifier
        if self.__match(TokenType.IDENTIFIER):
            if self.__match(TokenType.OPEN_PARENTHESES):
                arguments = []
                while not self.__is_at_end() and not self.__match(TokenType.CLOSE_PARENTHESES):
                    arg = self.__expression()
                    arguments.append(arg)

                    if self.__match(TokenType.CLOSE_PARENTHESES):
                        break

                    self.__consume(TokenType.COMMA, "Expected ( ',' Comma ) ")

                return FuncCall(token.literal_value, tuple(arguments))

            return VarReference(token.literal_value)

        # Literal Values
        if self.__match(TokenType.INTEGER):
            return Integer(int(token.literal_value))
        if self.__match(TokenType.DOUBLE):
            return Double(float(token.literal_value))
        if self.__match(TokenType.STRING):
            return String(token.literal_value)
        if self.__match(TokenType.BOOLEAN):
            value = True if token.literal_value == "True" else False
            return Boolean(value)
        if self.__match(TokenType.NULL):
            return Null(None)

        raise RuntimeError(f"Unexpected Token '{token}' at: index ({self.__cur_index})")

    # ========================================= Utility Methods ==========================================
    # ================ Consuming Methods ================
    def __match(self, *expected_types) -> bool:
        for expected in expected_types:
            if self.__check(expected):
                self.__advance()
                return True
        return False

    def __consume(self, expected_type: TokenType, err_msg: str) -> Token:
        if self.__check(expected_type):
            return self.__advance()
        raise RuntimeError(err_msg)

    def __advance(self) -> Token:
        self.__cur_index += 1
        return self.__peek(-1)

    # =============== Read-Only Methods ================
    def __check(self, expected_type: TokenType) -> bool:
        if self.__is_at_end():
            return self.__peek().type == TokenType.EOF
        return self.__peek().type == expected_type

    def __is_at_end(self) -> bool:
        return self.__peek().type == TokenType.EOF

    def __peek(self, offset: int = 0) -> Token:
        return self.__tokens[self.__cur_index + offset]

    # =============== Debugging Methods ================
    def __log(self, msg: str):
        if self.__enable_log:
            print(msg)


if __name__ == '__main__':
    pass
