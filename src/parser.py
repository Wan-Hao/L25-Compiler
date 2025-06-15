from src.lexer import TokenType
from src.ast import (
    Program, FuncDef, StructDef, StmtList, DeclareStmt, AssignStmt, IfStmt, WhileStmt,
    InputStmt, OutputStmt, ReturnStmt, FuncCall, StructInit, MemberAccess,
    ArrayLiteral, ArrayAccess, TryCatch, BoolExpr, BinaryOp, UnaryOp,
    Identifier, Number, String
)
from src.error import ParserError

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos]
        self.struct_names = set() # Keep track of defined struct types

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None # Should be EOF token

    def error(self, message):
        raise ParserError(message, self.current_token)

    def eat(self, token_type):
        if self.current_token and self.current_token.type == token_type:
            token = self.current_token
            self.advance()
            return token
        else:
            self.error(f"Expected {token_type}, but got {self.current_token.type if self.current_token else 'None'}")

    def parse(self):
        return self.program()

    def program(self):
        self.eat(TokenType.PROGRAM)
        name = Identifier(self.eat(TokenType.IDENT))
        self.eat(TokenType.LBRACE)
        
        struct_defs = []
        func_defs = []
        while self.current_token.type in (TokenType.FUNC, TokenType.STRUCT):
            if self.current_token.type == TokenType.STRUCT:
                struct_defs.append(self.struct_def())
            else:
                func_defs.append(self.func_def())

        self.eat(TokenType.MAIN)
        self.eat(TokenType.LBRACE)
        main_block = self.stmt_list()
        self.eat(TokenType.RBRACE)
        self.eat(TokenType.RBRACE)
        
        return Program(name, struct_defs, func_defs, main_block)
    
    def struct_def(self):
        self.eat(TokenType.STRUCT)
        name_token = self.eat(TokenType.IDENT)
        name = Identifier(name_token)
        self.struct_names.add(name.value)
        self.eat(TokenType.LBRACE)
        fields = self.param_list() # Reuse param_list for field names
        self.eat(TokenType.RBRACE)
        self.eat(TokenType.SEMICOLON)
        return StructDef(name, fields)

    def func_def(self):
        self.eat(TokenType.FUNC)
        name = Identifier(self.eat(TokenType.IDENT))
        self.eat(TokenType.LPAREN)
        params = []
        if self.current_token.type == TokenType.IDENT:
            params = self.param_list()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LBRACE)
        
        body = self.stmt_list()
        
        self.eat(TokenType.RETURN)
        return_expr = self.expr()
        self.eat(TokenType.SEMICOLON)
        
        body.stmts.append(ReturnStmt(return_expr))
        self.eat(TokenType.RBRACE)
        return FuncDef(name, params, body)

    def param_list(self):
        params = [Identifier(self.eat(TokenType.IDENT))]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            params.append(Identifier(self.eat(TokenType.IDENT)))
        return params

    def stmt_list(self):
        stmts = [self.stmt()]
        self.eat(TokenType.SEMICOLON)
        while self.current_token.type != TokenType.RBRACE and self.current_token.type != TokenType.RETURN:
            stmts.append(self.stmt())
            self.eat(TokenType.SEMICOLON)
        return StmtList(stmts)

    def stmt(self):
        token_type = self.current_token.type
        if token_type == TokenType.LET:
            return self.declare_stmt()
        if token_type == TokenType.IF:
            return self.if_stmt()
        if token_type == TokenType.WHILE:
            return self.while_stmt()
        if token_type == TokenType.INPUT:
            return self.input_stmt()
        if token_type == TokenType.OUTPUT:
            return self.output_stmt()
        if token_type == TokenType.TRY:
            return self.try_catch_stmt()
        
        # It's an assignment or a standalone function call.
        # Both start with an identifier and can have complex access chains.
        left_node = self.call_access()

        if self.current_token.type == TokenType.ASSIGN:
            self.eat(TokenType.ASSIGN)
            right_expr = self.expr()
            
            if not isinstance(left_node, (Identifier, MemberAccess, ArrayAccess)):
                self.error("Invalid target for assignment.")
            
            return AssignStmt(left_node, right_expr)
        
        # If it's not an assignment, it must be a standalone function call.
        if isinstance(left_node, FuncCall):
            return left_node
            
        self.error(f"Invalid statement. Expected assignment or function call.")

    def declare_stmt(self):
        self.eat(TokenType.LET)
        ident = Identifier(self.eat(TokenType.IDENT))
        expr = None
        if self.current_token.type == TokenType.ASSIGN:
            self.eat(TokenType.ASSIGN)
            expr = self.expr()
        return DeclareStmt(ident, expr)

    def if_stmt(self):
        self.eat(TokenType.IF)
        self.eat(TokenType.LPAREN)
        bool_expr_node = self.bool_expr()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LBRACE)
        if_block = self.stmt_list()
        self.eat(TokenType.RBRACE)
        
        else_block = None
        if self.current_token.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            self.eat(TokenType.LBRACE)
            else_block = self.stmt_list()
            self.eat(TokenType.RBRACE)
        
        return IfStmt(bool_expr_node, if_block, else_block)

    def while_stmt(self):
        self.eat(TokenType.WHILE)
        self.eat(TokenType.LPAREN)
        bool_expr_node = self.bool_expr()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LBRACE)
        body = self.stmt_list()
        self.eat(TokenType.RBRACE)
        return WhileStmt(bool_expr_node, body)

    def try_catch_stmt(self):
        self.eat(TokenType.TRY)
        self.eat(TokenType.LBRACE)
        try_block = self.stmt_list()
        self.eat(TokenType.RBRACE)
        self.eat(TokenType.CATCH)
        self.eat(TokenType.LBRACE)
        catch_block = self.stmt_list()
        self.eat(TokenType.RBRACE)
        return TryCatch(try_block, catch_block)

    def arg_list(self):
        args = [self.expr()]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            args.append(self.expr())
        return args

    def input_stmt(self):
        self.eat(TokenType.INPUT)
        self.eat(TokenType.LPAREN)
        idents = [Identifier(self.eat(TokenType.IDENT))]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            idents.append(Identifier(self.eat(TokenType.IDENT)))
        self.eat(TokenType.RPAREN)
        return InputStmt(idents)

    def output_stmt(self):
        self.eat(TokenType.OUTPUT)
        self.eat(TokenType.LPAREN)
        exprs = self.arg_list() if self.current_token.type != TokenType.RPAREN else []
        self.eat(TokenType.RPAREN)
        return OutputStmt(exprs)

    def bool_expr(self):
        left = self.expr()
        op_token = self.current_token
        if op_token.type not in [TokenType.EQ, TokenType.NEQ, TokenType.LT, TokenType.LTE, TokenType.GT, TokenType.GTE]:
            self.error("Invalid boolean operator")
        self.eat(op_token.type)
        right = self.expr()
        return BoolExpr(left, op_token, right)

    def expr(self):
        node = self.term()
        while self.current_token and self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.eat(self.current_token.type)
            node = BinaryOp(left=node, op=op, right=self.term())
        return node

    def term(self):
        node = self.factor()
        while self.current_token and self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            op = self.eat(self.current_token.type)
            node = BinaryOp(left=node, op=op, right=self.factor())
        return node

    def factor(self):
        token = self.current_token
        if token.type == TokenType.PLUS:
            self.eat(TokenType.PLUS)
            return UnaryOp(op=token, expr=self.factor())
        elif token.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            return UnaryOp(op=token, expr=self.factor())
        else:
            return self.call_access()
            
    def call_access(self):
        node = self.primary()
        while self.current_token.type in (TokenType.LPAREN, TokenType.LBRACKET, TokenType.DOT):
            if self.current_token.type == TokenType.LPAREN:
                self.eat(TokenType.LPAREN)
                args = self.arg_list() if self.current_token.type != TokenType.RPAREN else []
                self.eat(TokenType.RPAREN)
                # Check if it's a struct initialization or a function call
                if isinstance(node, Identifier) and node.value in self.struct_names:
                    node = StructInit(node, args)
                else:
                    node = FuncCall(node, args)
            elif self.current_token.type == TokenType.LBRACKET:
                self.eat(TokenType.LBRACKET)
                index_expr = self.expr()
                self.eat(TokenType.RBRACKET)
                node = ArrayAccess(node, index_expr)
            elif self.current_token.type == TokenType.DOT:
                self.eat(TokenType.DOT)
                member_ident = Identifier(self.eat(TokenType.IDENT))
                node = MemberAccess(node, member_ident)
        return node

    def primary(self):
        token = self.current_token
        if token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return Number(token)
        if token.type == TokenType.STRING:
            self.eat(TokenType.STRING)
            return String(token)
        if token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        if token.type == TokenType.IDENT:
            return Identifier(self.eat(TokenType.IDENT))
        if token.type == TokenType.LBRACKET:
            return self.array_literal()
        
        self.error("Invalid syntax for expression.")

    def array_literal(self):
        self.eat(TokenType.LBRACKET)
        elements = self.arg_list() if self.current_token.type != TokenType.RBRACKET else []
        self.eat(TokenType.RBRACKET)
        return ArrayLiteral(elements)