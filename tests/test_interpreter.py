import unittest
import io
import sys
from unittest.mock import patch

from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.error import InterpreterError

class TestInterpreter(unittest.TestCase):

    def helper_run_code(self, code, inputs=None):
        # Mock stdin if inputs are provided
        if inputs:
            input_patch = patch('builtins.input', side_effect=inputs)
            input_mock = input_patch.start()
            self.addCleanup(input_patch.stop)

        # Redirect stdout to capture output
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        error = None
        try:
            lexer = Lexer(code)
            parser = Parser(lexer.tokens())
            interpreter = Interpreter(parser)
            interpreter.interpret()
        except Exception as e:
            error = e
        finally:
            # Restore stdout and get the value
            output_string = captured_output.getvalue()
            sys.stdout = old_stdout

        if error:
            raise error
            
        return output_string.strip()

    def test_arithmetic_and_variables(self):
        code = "program P{main{let x=10; let y=x*2+5; output(y);}}"
        output = self.helper_run_code(code)
        self.assertEqual(output, "25")

    def test_if_else(self):
        code = "program P{main{if(10 > 5){output(1);} else {output(0);}}}"
        output = self.helper_run_code(code)
        self.assertEqual(output, "1")
        
        code = "program P{main{if(1 > 5){output(1);} else {output(0);}}}"
        output = self.helper_run_code(code)
        self.assertEqual(output, "0")

    def test_while_loop(self):
        code = "program P{main{let i=0; while(i<3){i=i+1;}; output(i);}}"
        output = self.helper_run_code(code)
        self.assertEqual(output, "3")

    def test_functions(self):
        code = """
        program P {
            func add(a, b) {
                return a + b;
            }
            main {
                output(add(15, 27));
            }
        }
        """
        output = self.helper_run_code(code)
        self.assertEqual(output, "42")
        
    def test_string_operations(self):
        code = 'program P{main{let s = "foo" * 3; output(s + "bar");}}'
        output = self.helper_run_code(code)
        self.assertEqual(output, "foofoofoobar")
        
    def test_arrays_and_structs(self):
        code = """
        program P {
            struct Point { x, y };
            main {
                let p = Point(10, 20);
                let arr = [1, p];
                arr[0] = 5;
                p.y = arr[0] + p.y;
                output(p.y);
            }
        }
        """
        output = self.helper_run_code(code)
        self.assertEqual(output, "25")

    def test_try_catch(self):
        code = "program P{main{try{output(1/0);}catch{output(99);}}}"
        output = self.helper_run_code(code)
        self.assertIn("99", output) # Should execute catch block

        # Test fatal error without try-catch
        code_no_catch = "program P{main{output(1/0);}}"
        with self.assertRaises(InterpreterError):
            self.helper_run_code(code_no_catch)
            
    def test_input_statement(self):
        code = "program P{main{let x; input(x); output(x+1);}}"
        output = self.helper_run_code(code, inputs=['123'])
        self.assertEqual(output, "124")

if __name__ == '__main__':
    unittest.main()