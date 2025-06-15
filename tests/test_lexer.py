from src.lexer import Lexer, TokenType

# 创建词法分析器
lexer = Lexer('let x = 5;')

# 获取所有tokens
tokens = lexer.tokens()

# 或者逐个获取token
while True:
    token = lexer.get_next_token()
    if token.type == TokenType.EOF:
        break
    print(token)