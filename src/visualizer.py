 
import uuid
from src.ast import (
    Program, FuncDef, StructDef, StmtList, DeclareStmt, AssignStmt, IfStmt, WhileStmt,
    InputStmt, OutputStmt, ReturnStmt, FuncCall, StructInit, MemberAccess,
    ArrayLiteral, ArrayAccess, TryCatch, BoolExpr, BinaryOp, UnaryOp,
    Identifier, Number, String
)

class ASTVisualizer:
    """
    Generates a Mermaid graph representation of the AST.
    Uses the visitor pattern to traverse the AST nodes.
    """
    def __init__(self, root):
        self.root = root
        # Using <br/> for newlines in Mermaid labels
        self.graph = ["graph TD"]
        self.counter = 0

    def _get_id(self):
        """Generates a unique ID for each node in the graph."""
        self.counter += 1
        return f"node{self.counter}"

    def generate(self):
        """Generates the full Mermaid graph string."""
        self._visit(self.root)
        # Join with newline characters for the final output
        return "\n".join(self.graph)

    def _add_node(self, node, label=None):
        """Adds a node to the graph definition."""
        node_id = self._get_id()
        if label is None:
            label = node.__class__.__name__
        # Mermaid requires quotes for labels, especially with special characters or spaces.
        self.graph.append(f'{node_id}["{label}"]')
        return node_id

    def _add_edge(self, from_id, to_id, label=None):
        """Adds an edge between two nodes."""
        if label:
            self.graph.append(f'{from_id} -- "{label}" --> {to_id}')
        else:
            self.graph.append(f'{from_id} --> {to_id}')

    def _visit(self, node):
        """Dispatcher that calls the appropriate visit method for a node type."""
        method_name = f'_visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self._generic_visit)
        return visitor(node)

    def _generic_visit(self, node):
        """Fallback for unhandled node types."""
        raise Exception(f"No _visit_{node.__class__.__name__} method defined")

    def _visit_Program(self, node):
        node_id = self._add_node(node, f"Program<br/>{node.name.value}")
        for s in node.struct_defs:
            child_id = self._visit(s)
            self._add_edge(node_id, child_id, "struct")
        for f in node.func_defs:
            child_id = self._visit(f)
            self._add_edge(node_id, child_id, "func")
        main_block_id = self._visit(node.main_block)
        self._add_edge(node_id, main_block_id, "main")
        return node_id

    def _visit_StructDef(self, node):
        node_id = self._add_node(node, f"StructDef<br/>{node.name.value}")
        for field in node.fields:
            child_id = self._visit(field)
            self._add_edge(node_id, child_id, "field")
        return node_id

    def _visit_FuncDef(self, node):
        node_id = self._add_node(node, f"FuncDef<br/>{node.name.value}")
        for param in node.params:
            child_id = self._visit(param)
            self._add_edge(node_id, child_id, "param")
        body_id = self._visit(node.body)
        self._add_edge(node_id, body_id, "body")
        return node_id

    def _visit_StmtList(self, node):
        node_id = self._add_node(node)
        for i, stmt in enumerate(node.stmts):
            child_id = self._visit(stmt)
            self._add_edge(node_id, child_id, f"stmt {i}")
        return node_id
    
    def _visit_ReturnStmt(self, node):
        node_id = self._add_node(node)
        expr_id = self._visit(node.expr)
        self._add_edge(node_id, expr_id, "value")
        return node_id

    def _visit_DeclareStmt(self, node):
        node_id = self._add_node(node, f"let {node.ident.value}")
        if node.expr:
            child_id = self._visit(node.expr)
            self._add_edge(node_id, child_id, "=")
        return node_id

    def _visit_AssignStmt(self, node):
        node_id = self._add_node(node, "Assign")
        left_id = self._visit(node.left)
        self._add_edge(node_id, left_id, "target")
        right_id = self._visit(node.expr)
        self._add_edge(node_id, right_id, "value")
        return node_id

    def _visit_IfStmt(self, node):
        node_id = self._add_node(node)
        cond_id = self._visit(node.bool_expr)
        self._add_edge(node_id, cond_id, "condition")
        if_block_id = self._visit(node.if_block)
        self._add_edge(node_id, if_block_id, "if_block")
        if node.else_block:
            else_block_id = self._visit(node.else_block)
            self._add_edge(node_id, else_block_id, "else_block")
        return node_id

    def _visit_WhileStmt(self, node):
        node_id = self._add_node(node)
        cond_id = self._visit(node.bool_expr)
        self._add_edge(node_id, cond_id, "condition")
        body_id = self._visit(node.body)
        self._add_edge(node_id, body_id, "body")
        return node_id

    def _visit_TryCatch(self, node):
        node_id = self._add_node(node)
        try_id = self._visit(node.try_block)
        self._add_edge(node_id, try_id, "try")
        catch_id = self._visit(node.catch_block)
        self._add_edge(node_id, catch_id, "catch")
        return node_id

    def _visit_InputStmt(self, node):
        node_id = self._add_node(node)
        for ident in node.idents:
            child_id = self._visit(ident)
            self._add_edge(node_id, child_id, "into")
        return node_id

    def _visit_OutputStmt(self, node):
        node_id = self._add_node(node)
        for expr in node.exprs:
            child_id = self._visit(expr)
            self._add_edge(node_id, child_id, "value")
        return node_id

    def _visit_FuncCall(self, node):
        node_id = self._add_node(node, "FuncCall")
        callee_id = self._visit(node.name)
        self._add_edge(node_id, callee_id, "callee")
        for i, arg in enumerate(node.args):
            child_id = self._visit(arg)
            self._add_edge(node_id, child_id, f"arg {i}")
        return node_id
    
    def _visit_StructInit(self, node):
        node_id = self._add_node(node, f"StructInit<br/>{node.name.value}")
        for i, arg in enumerate(node.args):
            child_id = self._visit(arg)
            self._add_edge(node_id, child_id, f"arg {i}")
        return node_id

    def _visit_MemberAccess(self, node):
        node_id = self._add_node(node, f". (member)")
        obj_id = self._visit(node.struct_expr)
        self._add_edge(node_id, obj_id, "object")
        member_id = self._visit(node.member_ident)
        self._add_edge(node_id, member_id, "member")
        return node_id

    def _visit_ArrayLiteral(self, node):
        node_id = self._add_node(node)
        for i, element in enumerate(node.elements):
            child_id = self._visit(element)
            self._add_edge(node_id, child_id, f"[{i}]")
        return node_id

    def _visit_ArrayAccess(self, node):
        node_id = self._add_node(node, "[] (access)")
        array_id = self._visit(node.ident)
        self._add_edge(node_id, array_id, "array")
        index_id = self._visit(node.index_expr)
        self._add_edge(node_id, index_id, "index")
        return node_id

    def _visit_BoolExpr(self, node):
        node_id = self._add_node(node, f"BoolExpr<br/>{node.op.value}")
        left_id = self._visit(node.left)
        self._add_edge(node_id, left_id, "left")
        right_id = self._visit(node.right)
        self._add_edge(node_id, right_id, "right")
        return node_id

    def _visit_BinaryOp(self, node):
        node_id = self._add_node(node, f"Op: {node.op.value}")
        left_id = self._visit(node.left)
        self._add_edge(node_id, left_id, "left")
        right_id = self._visit(node.right)
        self._add_edge(node_id, right_id, "right")
        return node_id

    def _visit_UnaryOp(self, node):
        node_id = self._add_node(node, f"UnaryOp: {node.op.value}")
        child_id = self._visit(node.expr)
        self._add_edge(node_id, child_id)
        return node_id

    def _visit_Identifier(self, node):
        return self._add_node(node, f"Id: {node.value}")

    def _visit_Number(self, node):
        return self._add_node(node, f"Num: {node.value}")

    def _visit_String(self, node):
        # Escape quotes for the label string
        value = node.value.replace('"', '&quot;')
        return self._add_node(node, f'Str: "{value}"')
