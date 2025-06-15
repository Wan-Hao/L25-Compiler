import unittest
from src.lexer import Lexer
from src.parser import Parser
from src.ast import Program, DeclareStmt, BinaryOp, Number, Identifier
from src.error import ParserError

class TestParser(unittest.TestCase):

    def helper_get_ast(self, code):
        lexer = Lexer(code)
        parser = Parser(lexer.tokens())
        return parser.parse()

    def test_simple_program(self):
        code = """
        program Test {
            main {
                let x = 1 + 2;
            }
        }
        """
        tree = self.helper_get_ast(code)
        self.assertIsInstance(tree, Program)
        self.assertEqual(tree.name.value, "Test")
        
        main_block = tree.main_block
        self.assertEqual(len(main_block.stmts), 1)
        
        decl_stmt = main_block.stmts[0]
        self.assertIsInstance(decl_stmt, DeclareStmt)
        self.assertEqual(decl_stmt.ident.value, "x")
        
        bin_op = decl_stmt.expr
        self.assertIsInstance(bin_op, BinaryOp)
        self.assertIsInstance(bin_op.left, Number)
        self.assertEqual(bin_op.left.value, 1)
        self.assertIsInstance(bin_op.right, Number)
        self.assertEqual(bin_op.right.value, 2)

    def test_operator_precedence(self):
        code = "program P{main{let x = 1 + 2 * 3;}}"
        tree = self.helper_get_ast(code)
        
        # AST should be: let x = (1 + (2 * 3));
        assignment_expr = tree.main_block.stmts[0].expr
        self.assertIsInstance(assignment_expr, BinaryOp)
        # self.assertEqual(assignment_expr.op.type, TokenType.PLUS)
        
        right_side = assignment_expr.right
        self.assertIsInstance(right_side, BinaryOp)
        # self.assertEqual(right_side.op.type, TokenType.MULTIPLY)
        self.assertEqual(right_side.left.value, 2)
        self.assertEqual(right_side.right.value, 3)

    def test_syntax_error(self):
        # Missing semicolon after statement
        code = "program P{main{let x = 1}}"
        with self.assertRaises(ParserError):
            self.helper_get_ast(code)
            
        # if without parenthesis
        code = "program P{main{if 1 > 0 { let y=1; };}}"
        with self.assertRaises(ParserError):
            self.helper_get_ast(code)

if __name__ == '__main__':
    unittest.main()