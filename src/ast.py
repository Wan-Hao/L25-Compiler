from src.lexer import Token

class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, name, struct_defs, func_defs, main_block):
        self.name = name
        self.struct_defs = struct_defs
        self.func_defs = func_defs
        self.main_block = main_block

class FuncDef(ASTNode):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

# Group 3: Struct Definition
class StructDef(ASTNode):
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields

class StmtList(ASTNode):
    def __init__(self, stmts):
        self.stmts = stmts

class DeclareStmt(ASTNode):
    def __init__(self, ident, expr=None):
        self.ident = ident
        self.expr = expr

class AssignStmt(ASTNode):
    def __init__(self, left, expr):
        self.left = left # Can be Identifier, MemberAccess, or ArrayAccess
        self.expr = expr

class IfStmt(ASTNode):
    def __init__(self, bool_expr, if_block, else_block=None):
        self.bool_expr = bool_expr
        self.if_block = if_block
        self.else_block = else_block

class WhileStmt(ASTNode):
    def __init__(self, bool_expr, body):
        self.bool_expr = bool_expr
        self.body = body

class InputStmt(ASTNode):
    def __init__(self, idents):
        self.idents = idents

class OutputStmt(ASTNode):
    def __init__(self, exprs):
        self.exprs = exprs

class ReturnStmt(ASTNode):
    def __init__(self, expr):
        self.expr = expr

class FuncCall(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class TryCatch(ASTNode):
    def __init__(self, try_block, catch_block):
        self.try_block = try_block
        self.catch_block = catch_block

class BoolExpr(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class BinaryOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOp(ASTNode):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class Identifier(ASTNode):
    def __init__(self, token: Token):
        self.token = token
        self.value = token.value

class Number(ASTNode):
    def __init__(self, token: Token):
        self.token = token
        self.value = token.value

# Group 2: String Literal
class String(ASTNode):
    def __init__(self, token: Token):
        self.token = token
        self.value = token.value

# Group 3: Array Literal
class ArrayLiteral(ASTNode):
    def __init__(self, elements):
        self.elements = elements

# Group 3: Array Access (e.g., my_array[0])
class ArrayAccess(ASTNode):
    def __init__(self, ident, index_expr):
        self.ident = ident
        self.index_expr = index_expr

# Group 3: Struct Initialization (e.g., Point(1, 2))
class StructInit(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args

# Group 3: Member Access (e.g., my_struct.field)
class MemberAccess(ASTNode):
    def __init__(self, struct_expr, member_ident):
        self.struct_expr = struct_expr
        self.member_ident = member_ident