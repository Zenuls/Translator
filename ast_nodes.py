from dataclasses import dataclass
from typing import List, Tuple, Optional, Any

# AST Nodes
class ASTNode:
    pass

@dataclass
class Program(ASTNode):
    decls: List[ASTNode]

@dataclass
class IncludeDirective(ASTNode):
    filename: str

@dataclass
class Parameter:
    param_type: str
    name: str
    default_value: Optional[ASTNode] = None

# Обновим FunctionDecl
@dataclass
class FunctionDecl(ASTNode):
    return_type: str
    name: str
    params: List[Parameter]  # Изменяем тип на List[Parameter]
    body: 'Block'

@dataclass
class VariableDecl(ASTNode):
    var_type: str
    name: str
    init_value: Optional[ASTNode]

@dataclass
class Block(ASTNode):
    statements: List[ASTNode]

@dataclass
class IfStatement(ASTNode):
    condition: ASTNode
    then_branch: Block
    else_branch: Optional[Block]

@dataclass
class WhileStatement(ASTNode):
    condition: ASTNode
    body: Block

@dataclass
class ForStatement(ASTNode):
    init: Optional[ASTNode]
    condition: Optional[ASTNode]
    increment: Optional[ASTNode]
    body: Block

@dataclass
class DoWhileStatement(ASTNode):
    body: Block
    condition: ASTNode

@dataclass
class ReturnStatement(ASTNode):
    value: Optional[ASTNode]

@dataclass
class ExpressionStatement(ASTNode):
    expr: ASTNode

@dataclass
class BinaryOperation(ASTNode):
    operator: str
    left: ASTNode
    right: ASTNode

@dataclass
class UnaryOperation(ASTNode):
    operator: str
    operand: ASTNode
    is_postfix: bool = False

@dataclass
class Literal(ASTNode):
    value: Any
    literal_type: str

@dataclass
class VariableReference(ASTNode):
    name: str

@dataclass
class FunctionCall(ASTNode):
    name: str
    arguments: List[ASTNode]

@dataclass
class CoutStatement(ASTNode):
    expressions: List[ASTNode]

@dataclass
class CinStatement(ASTNode):
    variables: List[ASTNode]

@dataclass
class TernaryOperation(ASTNode):
    condition: ASTNode
    then_expr: ASTNode
    else_expr: ASTNode

@dataclass
class ArrayDecl(ASTNode):
    var_type: str
    name: str
    size: Optional[ASTNode]
    init_values: List[ASTNode]

@dataclass
class ArrayAccess(ASTNode):
    array: ASTNode
    index: ASTNode

@dataclass
class StringLiteral(ASTNode):
    value: str