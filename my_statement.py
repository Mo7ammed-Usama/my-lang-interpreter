from abc import ABC
from dataclasses import dataclass
from my_expr import Expr
from my_token import TokenType


class Stmt(ABC):
    __slots__ = ()

# ============================= Expression Statement (Default statement) =============================
@dataclass(slots=True)
class ExprStmt(Stmt):
    expression: Expr
# ====================================================================================================


# ================================== Variable Assigning Statements ===================================
@dataclass(slots=True)
class VarDeclaration(Stmt):
    name: str
    value: Expr


@dataclass(slots=True)
class VarUpdate(Stmt):
    name: str
    new_value: Expr
# ====================================================================================================


# ====================================== Conditional Statements ======================================
@dataclass(slots=True)
class IfStmt(Stmt):
    condition: Expr
    block: tuple[Stmt, ...]
# ====================================================================================================


# ========================================= Loop Statements ==========================================
@dataclass(slots=True)
class WhileStmt(Stmt):
    condition: Expr
    block: tuple[Stmt, ...]


@dataclass(slots=True)
class ForStmt(Stmt):
    iterable: None
    block: tuple[Stmt, ...]


@dataclass(slots=True)
class BreakStmt(Stmt):
    pass


@dataclass(slots=True)
class ContinueStmt(Stmt):
    pass
# ====================================================================================================


# ======================================== Function Statements =======================================
@dataclass(slots=True)
class FuncDeclaration(Stmt):
    name: str
    param_names: tuple[str, ...]
    block: tuple[Stmt, ...]


@dataclass(slots=True)
class ReturnStmt(Stmt):
    value: Expr
# ====================================================================================================
