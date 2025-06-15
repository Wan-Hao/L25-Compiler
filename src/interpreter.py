from src.ast import (
    Program, FuncDef, StructDef, StmtList, DeclareStmt, AssignStmt, IfStmt, WhileStmt,
    InputStmt, OutputStmt, ReturnStmt, FuncCall, StructInit, MemberAccess,
    ArrayLiteral, ArrayAccess, TryCatch, BoolExpr, BinaryOp, UnaryOp,
    Identifier, Number, String
)
from src.lexer import TokenType
from src.error import InterpreterError

class ReturnValue(Exception):
    """Exception used to unwind the stack and return a value from a function."""
    def __init__(self, value):
        self.value = value

class StructDefinition:
    """Represents the blueprint of a struct."""
    def __init__(self, name, fields):
        self.name = name
        self.fields = [field.value for field in fields]

class StructInstance:
    """Represents an instance of a struct."""
    def __init__(self, type_name):
        self.type_name = type_name
        self.members = {}
    def __repr__(self):
        return f"<Struct {self.type_name}: {self.members}>"


class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.variables = {}

    def get(self, name):
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        return None

    def set(self, name, value):
        if name in self.variables:
            self.variables[name] = value
        elif self.parent:
            self.parent.set(name, value)
        else:
            raise InterpreterError(f"Variable '{name}' not defined before assignment.")

    def declare(self, name, value):
        self.variables[name] = value

class Interpreter:
    def __init__(self, parser):
        self.tree = parser.parse()
        self.global_scope = Scope()
        self.current_scope = self.global_scope
        self.is_in_try_block = False

    def interpret(self):
        return self.visit(self.tree)

    def visit(self, node, scope=None):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        
        old_scope = self.current_scope
        if scope:
            self.current_scope = scope
        
        result = visitor(node)
        
        if scope:
            self.current_scope = old_scope
            
        return result

    def generic_visit(self, node):
        raise InterpreterError(f'No visit_{type(node).__name__} method')

    def visit_Program(self, node):
        # Store struct definitions
        for struct_def in node.struct_defs:
            self.visit(struct_def)
        # Store function definitions
        for func_def in node.func_defs:
            self.global_scope.declare(func_def.name.value, func_def)
        # Execute the main block
        self.visit(node.main_block, scope=self.global_scope)

    def visit_FuncDef(self, node):
        pass # Handled in visit_Program

    def visit_StructDef(self, node):
        struct_blueprint = StructDefinition(node.name.value, node.fields)
        self.current_scope.declare(node.name.value, struct_blueprint)

    def visit_StmtList(self, node):
        for stmt in node.stmts:
            self.visit(stmt)

    def visit_DeclareStmt(self, node):
        val = None
        if node.expr:
            val = self.visit(node.expr)
        self.current_scope.declare(node.ident.value, val)

    def visit_AssignStmt(self, node):
        rvalue = self.visit(node.expr)
        
        if isinstance(node.left, Identifier):
            self.current_scope.set(node.left.value, rvalue)
        elif isinstance(node.left, MemberAccess):
            struct_instance = self.visit(node.left.struct_expr)
            if not isinstance(struct_instance, StructInstance):
                raise InterpreterError("Cannot access member of a non-struct type.", node.left.member_ident.token)
            member_name = node.left.member_ident.value
            struct_instance.members[member_name] = rvalue
        elif isinstance(node.left, ArrayAccess):
            array_obj = self.visit(node.left.ident)
            if not isinstance(array_obj, list):
                raise InterpreterError("Cannot index a non-array type.", node.left.ident.token)
            index = self.visit(node.left.index_expr)
            if not isinstance(index, int):
                raise InterpreterError("Array index must be an integer.")
            if not 0 <= index < len(array_obj):
                raise InterpreterError(f"Array index {index} out of bounds for array of size {len(array_obj)}.")
            array_obj[index] = rvalue
        else:
            raise InterpreterError("Invalid target for assignment.")

    def visit_IfStmt(self, node):
        if self.visit(node.bool_expr):
            self.visit(node.if_block)
        elif node.else_block:
            self.visit(node.else_block)

    def visit_WhileStmt(self, node):
        while self.visit(node.bool_expr):
            self.visit(node.body)

    def visit_InputStmt(self, node):
        for ident in node.idents:
            try:
                val = input()
                # Attempt to convert to int, otherwise treat as string
                try:
                    num_val = int(val)
                    self.current_scope.set(ident.value, num_val)
                except ValueError:
                    self.current_scope.set(ident.value, val)
            except Exception:
                raise InterpreterError(f"Failed to read input for '{ident.value}'", ident.token)

    def visit_OutputStmt(self, node):
        values = [str(self.visit(expr)) for expr in node.exprs]
        print(' '.join(values))

    def visit_ReturnStmt(self, node):
        raise ReturnValue(self.visit(node.expr))

    def visit_FuncCall(self, node):
        func_name = node.name.value
        func = self.current_scope.get(func_name)
        if not isinstance(func, FuncDef):
            raise InterpreterError(f"'{func_name}' is not a function", node.name.token)
        
        if len(node.args) != len(func.params):
            raise InterpreterError(f"Function '{func_name}' expects {len(func.params)} arguments but got {len(node.args)}", node.name.token)

        func_scope = Scope(parent=self.global_scope)
        for param, arg_expr in zip(func.params, node.args):
            func_scope.declare(param.value, self.visit(arg_expr))

        try:
            self.visit(func.body, scope=func_scope)
        except ReturnValue as ret:
            return ret.value
        return None

    def visit_TryCatch(self, node):
        old_try_state = self.is_in_try_block
        try:
            self.is_in_try_block = True
            self.visit(node.try_block)
        except InterpreterError as e:
            if "Division by zero" in str(e):
                print(f"Error: Division by zero detected. Jumping to catch block.")
                self.visit(node.catch_block)
            else:
                raise e
        finally:
            self.is_in_try_block = old_try_state
            
    def visit_BoolExpr(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op.type
        if op == TokenType.EQ: return left == right
        if op == TokenType.NEQ: return left != right
        if op == TokenType.LT: return left < right
        if op == TokenType.LTE: return left <= right
        if op == TokenType.GT: return left > right
        if op == TokenType.GTE: return left >= right

    def visit_BinaryOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op.type

        # Group 2: String Operations
        if isinstance(left, str) or isinstance(right, str):
            if op == TokenType.PLUS:
                return str(left) + str(right)
            if op == TokenType.MULTIPLY:
                if isinstance(left, str) and isinstance(right, int):
                    return left * right
                if isinstance(left, int) and isinstance(right, str):
                    return right * left
                raise InterpreterError("String multiplication must be between a string and an integer", node.op)

        # Standard Numeric Operations
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            if op == TokenType.PLUS: return left + right
            if op == TokenType.MINUS: return left - right
            if op == TokenType.MULTIPLY: return left * right
            if op == TokenType.DIVIDE:
                if right == 0:
                    if self.is_in_try_block:
                        raise InterpreterError("Division by zero", node.op)
                    raise InterpreterError("Fatal: Division by zero outside a try block", node.op)
                return left // right
        
        raise InterpreterError(f"Unsupported operand types for {op}: {type(left).__name__} and {type(right).__name__}", node.op)

    def visit_UnaryOp(self, node):
        val = self.visit(node.expr)
        if node.op.type == TokenType.MINUS:
            return -val
        return val

    def visit_Identifier(self, node):
        val = self.current_scope.get(node.value)
        if val is None:
            raise InterpreterError(f"Variable or struct '{node.value}' not defined.", node.token)
        return val

    def visit_Number(self, node):
        return node.value

    def visit_String(self, node):
        return node.value

    def visit_ArrayLiteral(self, node):
        return [self.visit(elem) for elem in node.elements]

    def visit_ArrayAccess(self, node):
        array_obj = self.visit(node.ident)
        if not isinstance(array_obj, list):
            raise InterpreterError("Cannot index a non-array type.", node.ident.token)
        index = self.visit(node.index_expr)
        if not isinstance(index, int):
            raise InterpreterError("Array index must be an integer.")
        if not 0 <= index < len(array_obj):
            raise InterpreterError(f"Array index {index} out of bounds for array of size {len(array_obj)}.")
        return array_obj[index]

    def visit_StructInit(self, node):
        struct_name = node.name.value
        blueprint = self.current_scope.get(struct_name)
        if not isinstance(blueprint, StructDefinition):
            raise InterpreterError(f"'{struct_name}' is not a defined struct type.", node.name.token)
        if len(node.args) != len(blueprint.fields):
            raise InterpreterError(f"Struct '{struct_name}' expects {len(blueprint.fields)} fields but got {len(node.args)}", node.name.token)
        
        instance = StructInstance(struct_name)
        for field_name, arg_expr in zip(blueprint.fields, node.args):
            instance.members[field_name] = self.visit(arg_expr)
        return instance

    def visit_MemberAccess(self, node):
        struct_instance = self.visit(node.struct_expr)
        if not isinstance(struct_instance, StructInstance):
            raise InterpreterError("Cannot access member of a non-struct type.", node.member_ident.token)
        member_name = node.member_ident.value
        if member_name not in struct_instance.members:
            raise InterpreterError(f"Struct '{struct_instance.type_name}' has no member '{member_name}'", node.member_ident.token)
        return struct_instance.members[member_name]