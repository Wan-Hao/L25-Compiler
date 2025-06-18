import argparse
import sys
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from error import CompilerError
from visualizer import ASTVisualizer

def main():
    arg_parser = argparse.ArgumentParser(description='L25 Compiler and Interpreter')
    arg_parser.add_argument('file_path', help='Path to the L25 source file')
    arg_parser.add_argument('--visualize', action='store_true', help='Visualize the AST')
    args = arg_parser.parse_args()

    try:
        with open(args.file_path, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at '{args.file_path}'")
        sys.exit(1)

    try:
        # 1. Lexical Analysis
        lexer = Lexer(source_code)
        tokens = lexer.tokens()
        
        # 2. Parsing (Syntax Analysis)
        parser = Parser(tokens)
        
        # If visualization is requested, generate and print the AST diagram
        if args.visualize:
            ast = parser.parse()  # Get the AST without interpreting
            visualizer = ASTVisualizer(ast)
            print(visualizer.generate())
            sys.exit(0)
        
        # 3. Interpretation (only if not visualizing)
        interpreter = Interpreter(parser)
        interpreter.interpret()

    except CompilerError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()