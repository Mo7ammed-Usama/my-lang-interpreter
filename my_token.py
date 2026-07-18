from dataclasses import dataclass
from enum import Enum

class TokenType(Enum):
    OPEN_PARENTHESES = "("
    CLOSE_PARENTHESES = ")"
    OPEN_BRACE = "{"
    CLOSE_BRACE = "}"
    OPEN_BRACKET = "["
    CLOSE_BRACKET = "]"


    MULTIPLY = "*"
    DIVIDE = "/"
    PLUS = "+"
    MINUS = "-"
    EXPONENT = "**"
    FLOOR_DIVIDE = "//"

    EQUAL = "=="
    NOT_EQUAL = "!="
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_THAN_EQUAL = "<="
    GREATER_THAN_EQUAL = ">="

    ASSIGN = "="
    PLUS_PLUS = "++"
    MINUS_MINUS = "--"
    PLUS_EQUAL = "+="
    MINUS_EQUAL = "-="
    MULTIPLY_EQUAL = "*="
    DIVIDE_EQUAL = "/="
    EXPONENT_EQUAL = "**="
    FLOOR_DIVIDE_EQUAL = "//="

    SEMI_COLON = ";"
    COMMA = ","


    VAR = "var"
    IF = "if"
    WHILE = "while"
    FOR = "for"
    BREAK = "break"
    CONTINUE = "continue"
    FUNC = "func"
    RETURN = "return"

    NULL = "Null"
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    INTEGER = "INTEGER"
    DOUBLE = "DOUBLE"

    EOF = "EOF"

    def __repr__(self) -> str:
        return self.name

@dataclass(slots=True)
class Token:
    type: TokenType
    literal_value: str = None


ASSIGNING_TOKENS = (
    TokenType.ASSIGN,
    TokenType.PLUS_PLUS,
    TokenType.MINUS_MINUS,
    TokenType.PLUS_EQUAL,
    TokenType.MINUS_EQUAL,
    TokenType.MULTIPLY_EQUAL,
    TokenType.DIVIDE_EQUAL,
    TokenType.EXPONENT_EQUAL,
    TokenType.FLOOR_DIVIDE_EQUAL
)

ASSIGNING_TOKENS_TO_BASIC = {
    TokenType.ASSIGN             : TokenType.ASSIGN,
    TokenType.PLUS_PLUS          : TokenType.PLUS,
    TokenType.MINUS_MINUS        : TokenType.MINUS,
    TokenType.PLUS_EQUAL         : TokenType.PLUS,
    TokenType.MINUS_EQUAL        : TokenType.MINUS,
    TokenType.MULTIPLY_EQUAL     : TokenType.MULTIPLY,
    TokenType.DIVIDE_EQUAL       : TokenType.DIVIDE,
    TokenType.EXPONENT_EQUAL     : TokenType.EXPONENT,
    TokenType.FLOOR_DIVIDE_EQUAL : TokenType.FLOOR_DIVIDE
}