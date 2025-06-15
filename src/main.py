import argparse
import sys
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.error import CompilerError

def main():
    arg_parser = argparse.ArgumentParser(description='L25 Compiler and Interpreter')
    arg_parser.add_argument('file_path', help='Path to the L25 source file')
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

        # 3. Interpretation
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