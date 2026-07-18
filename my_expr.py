from abc import ABC
from dataclasses import dataclass
from my_token import Token


class Expr(ABC):
    __slots__ = ()
    pass

# ======================================== Binary Expression =========================================
@dataclass(slots=True)
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr
# ====================================================================================================


# =================================== Function Calling Expression ====================================
@dataclass(slots=True)
class FuncCall(Expr):
    name: str
    args: tuple[str, ...]
# ====================================================================================================


# ================================= Variable Referencing Expression ==================================
@dataclass(slots=True)
class VarReference(Expr):
    name: str
# ====================================================================================================


# ======================================= Literal Expressions ========================================
class Literal(Expr, ABC):
    pass

@dataclass(slots=True)
class Integer(Literal):
    value: int

@dataclass(slots=True)
class Double(Literal):
    value: float

@dataclass(slots=True)
class String(Literal):
    value: str

@dataclass(slots=True)
class Boolean(Literal):
    value: bool

@dataclass(slots=True)
class Null(Literal):
    value: None
# ====================================================================================================


TOKEN_TO_EXPRESSION = {
    None
}