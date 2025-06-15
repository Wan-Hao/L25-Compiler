import enum
import re

class TokenType(enum.Enum):
    # Keywords
    PROGRAM = 'program'
    FUNC = 'func'
    MAIN = 'main'
    LET = 'let'
    IF = 'if'
    ELSE = 'else'
    WHILE = 'while'
    RETURN = 'return'
    INPUT = 'input'
    OUTPUT = 'output'
    TRY = 'try'
    CATCH = 'catch'

    # Identifiers and literals
    IDENT = 'IDENT'
    NUMBER = 'NUMBER'
    STRING = 'STRING'

    # Keywords (Group 2 & 3 extensions)
    STRUCT = 'struct'

    # Operators
    ASSIGN = '='
    PLUS = '+'
    MINUS = '-'
    MULTIPLY = '*'
    DIVIDE = '/'
    EQ = '=='
    NEQ = '!='
    LT = '<'
    LTE = '<='
    GT = '>'
    GTE = '>='
    DOT = '.'

    # Punctuation
    LPAREN = '('
    RPAREN = ')'
    LBRACE = '{'
    RBRACE = '}'
    LBRACKET = '['
    RBRACKET = ']'
    COMMA = ','
    SEMICOLON = ';'

    # End of file
    EOF = 'EOF'

class Token:
    def __init__(self, type, value, line=0, column=0):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)}, line={self.line}, column={self.column})'

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
        self.line = 1
        self.column = 1

    def advance(self):
        if self.current_char == '\n':
            self.line += 1
            self.column = 0

        self.pos += 1
        self.column += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def identifier(self):
        result = ''
        # Allow underscores in identifiers
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        
        token_map = {
            'program': TokenType.PROGRAM,
            'func': TokenType.FUNC,
            'main': TokenType.MAIN,
            'let': TokenType.LET,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'return': TokenType.RETURN,
            'input': TokenType.INPUT,
            'output': TokenType.OUTPUT,
            'try': TokenType.TRY,
            'catch': TokenType.CATCH,
            'struct': TokenType.STRUCT,
        }
        
        token_type = token_map.get(result, TokenType.IDENT)
        return Token(token_type, result, self.line, self.column)

    def string(self):
        result = ''
        self.advance() # Skip opening quote
        while self.current_char is not None and self.current_char != '"':
            result += self.current_char
            self.advance()
        self.advance() # Skip closing quote
        return result

    def get_next_token(self):
        while self.current_char is not None:
            start_line = self.line
            start_column = self.column

            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            if self.current_char == '"':
                return Token(TokenType.STRING, self.string(), start_line, start_column)

            if self.current_char.isdigit():
                return Token(TokenType.NUMBER, self.number(), start_line, start_column)

            # This now handles identifiers with underscores
            if self.current_char.isalnum() or self.current_char == '_':
                return self.identifier()
            
            if self.current_char == '=':
                if self.pos + 1 < len(self.text) and self.text[self.pos+1] == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.EQ, '==', start_line, start_column)
                self.advance()
                return Token(TokenType.ASSIGN, '=', start_line, start_column)
            
            if self.current_char == '!':
                if self.pos + 1 < len(self.text) and self.text[self.pos+1] == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.NEQ, '!=', start_line, start_column)
                self.advance()

            if self.current_char == '<':
                if self.pos + 1 < len(self.text) and self.text[self.pos+1] == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.LTE, '<=', start_line, start_column)
                self.advance()
                return Token(TokenType.LT, '<', start_line, start_column)

            if self.current_char == '>':
                if self.pos + 1 < len(self.text) and self.text[self.pos+1] == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.GTE, '>=', start_line, start_column)
                self.advance()
                return Token(TokenType.GT, '>', start_line, start_column)

            single_char_tokens = {
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.MULTIPLY,
                '/': TokenType.DIVIDE,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                '[': TokenType.LBRACKET,
                ']': TokenType.RBRACKET,
                ',': TokenType.COMMA,
                ';': TokenType.SEMICOLON,
                '.': TokenType.DOT,
            }
            if self.current_char in single_char_tokens:
                token_type = single_char_tokens[self.current_char]
                char = self.current_char
                self.advance()
                return Token(token_type, char, start_line, start_column)
            
            raise Exception(f"Invalid character '{self.current_char}' at line {self.line} column {self.column}")

        return Token(TokenType.EOF, None, self.line, self.column)

    def tokens(self):
        tokens = []
        while (token := self.get_next_token()).type != TokenType.EOF:
            tokens.append(token)
        tokens.append(token) # append EOF
        return tokens