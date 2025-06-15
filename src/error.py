class CompilerError(Exception):
    """Base class for exceptions in the compiler."""
    pass

class ParserError(CompilerError):
    """Exception raised for errors in the parser."""
    def __init__(self, message, token=None):
        self.message = message
        self.token = token
        super().__init__(self.message)

    def __str__(self):
        if self.token:
            return f'[Line {self.token.line}:{self.token.column}] ParserError: {self.message}'
        return f'ParserError: {self.message}'

class InterpreterError(CompilerError):
    """Exception raised for errors during interpretation."""
    def __init__(self, message, token=None):
        self.message = message
        self.token = token
        super().__init__(self.message)

    def __str__(self):
        if self.token:
            return f'[Line {self.token.line}:{self.token.column}] InterpreterError: {self.message}'
        return f'InterpreterError: {self.message}'