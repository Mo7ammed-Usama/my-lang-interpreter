from dataclasses import dataclass
from enum import Enum

class TokenType(Enum):
    OPEN_PARENTHESES = "("
    CLOSE_PARENTHESES = ")"
    OPEN_BRACE = "{"
    CLOSE_BRACE = "}"

    STAR = "*"
    SLASH = "/"
    PLUS = "+"
    MINUS = "-"
    EQUAL = "="
    DOUBLE_EQUAL = "=="
    NOT_EQUAL = "!="
    GREATER_THAN = ">"
    GREATER_THAN_EQUAL = ">="
    LESS_THAN = "<"
    LESS_THAN_EQUAL = "<="
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
    CHAR = "CHAR"
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
    literal_value: str = ""

