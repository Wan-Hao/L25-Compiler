# L25 编译器设计与使用手册

## 1. 项目引言

本项目是为《编译原理与实践》课程设计并实现的一个L25语言编译器。该编译器使用 **Python 3** 从零开始编写，不依赖任何第三方解析器生成工具。

**核心功能与完成度：**
1.  **完整实现**：编译器完整支持了课程定义的L25基础语言规范。
2.  **全面扩展**：集成了课程要求的**第二、三、四组全部扩展功能**，包括：
    *   **字符串**：支持字符串字面量、拼接(`+`)与重复(`*`)运算。
    *   **复合类型**：支持一维静态**数组**和**结构体**的定义、声明、赋值与访问。
    *   **异常处理**：支持 `try-catch` 语句，用于捕获并处理运行时的除零错误。
3.  **双重交互模式**：
    *   提供了传统的**命令行界面(CLI)**，可直接运行 `.l25` 源文件。
    *   构建了一个现代化的**Web用户界面(UI)**，允许用户在浏览器中实时编写、运行代码并查看结果。

## 2. 扩展后的L25语言文法 (EBNF)

为了支持字符串、数组、结构体等新特性，我们对原始的L25文法进行了扩展。以下是本编译器当前所实现的、最完整的EBNF描述：

```ebnf
<program> ::= "program" <ident> "{" { <struct_def> } { <func_def> } "main" "{" <stmt_list> "}" "}"

<struct_def> ::= "struct" <ident> "{" <param_list> "}" ";"

<func_def> ::= "func" <ident> "(" [ <param_list> ] ")" "{" <stmt_list> "return" <expr> ";" "}"

<param_list> ::= <ident> { "," <ident> }

<stmt_list> ::= <stmt> ";" { <stmt> ";" }

<stmt> ::= <declare_stmt> | <assign_stmt> | <if_stmt> | <while_stmt> | <input_stmt> | <output_stmt> | <func_call> | <try_catch_stmt>

<declare_stmt> ::= "let" <ident> [ "=" <expr> ]

<assign_stmt> ::= <lvalue> "=" <expr>

<try_catch_stmt> ::= "try" "{" <stmt_list> "}" "catch" "{" <stmt_list> "}"

(* 左值(lvalue)可以是变量、数组成员或结构体成员 *)
<lvalue> ::= <ident> | <array_access> | <member_access>

<if_stmt> ::= "if" "(" <bool_expr> ")" "{" <stmt_list> "}" [ "else" "{" <stmt_list> "}" ]

<while_stmt> ::= "while" "(" <bool_expr> ")" "{" <stmt_list> "}"

<input_stmt> ::= "input" "(" <ident> { "," <ident> } ")"

<output_stmt> ::= "output" "(" <arg_list> ")"

<func_call> ::= <ident> "(" [ <arg_list> ] ")"

<arg_list> ::= <expr> { "," <expr> }

<bool_expr> ::= <expr> ("==" | "!=" | "<" | "<=" | ">" | ">=") <expr>

<expr> ::= <term> { ("+" | "-") <term> }

<term> ::= <factor> { ("*" | "/") <factor> }

(* 因子(factor)被大幅扩展以支持新语法 *)
<factor> ::= <primary> { "." <ident> | "[" <expr> "]" | "(" [ <arg_list> ] ")" }

<primary> ::= <number> | <string> | <ident> | <array_literal> | "(" <expr> ")"

<string> ::= "\"" { <any_char_except_quote> } "\""

<array_literal> ::= "[" [ <arg_list> ] "]"

<ident> ::= <letter> { <letter> | <digit> | "_" }
```

## 3. 编译器设计与实现

本项目采用经典的模块化设计，将编译器分为词法分析、语法分析、解释执行等多个阶段。

### 3.1 总体架构

编译器的工作流如下：
`源代码字符串 -> 词法分析器 -> Token流 -> 语法分析器 -> 抽象语法树(AST) -> 解释器 -> 程序输出`

### 3.2 核心模块详解

*   **`src/lexer.py` - 词法分析器**
    *   **职责**：将源代码文本分解成一个个独立的“单词”，即Token（记号）。例如，将字符串 `let x = 10;` 转换为 `[LET, IDENT('x'), ASSIGN, NUMBER(10), SEMICOLON]`。
    *   **实现**：通过逐字符扫描代码实现。当遇到数字、字母、操作符等不同类型的字符时，进入相应的处理函数（如`number()`、`identifier()`）来构建完整的Token。支持了下划线 `_` 作为标识符的一部分。

*   **`src/ast.py` - 抽象语法树 (AST)**
    *   **职责**：定义一系列Python类，用于在内存中表示代码的结构。例如，一个 `if` 语句会被表示成一个 `IfStmt` 对象，它包含 `condition`、`if_block`、`else_block` 三个子节点。
    *   **实现**：所有AST节点都继承自基类 `ASTNode`。为支持扩展功能，新增了 `String`、`ArrayLiteral`、`ArrayAccess`、`StructDef`、`StructInit`、`MemberAccess` 等节点类。

*   **`src/parser.py` - 语法分析器**
    *   **职责**：接收词法分析器生成的Token流，并根据EBNF文法规则构建起一棵完整的抽象语法树。这是检查代码**语法是否正确**的核心环节。
    *   **实现**：采用**递归下降(Recursive Descent)**的策略。解析过程由一系列函数组成，每个函数对应EBNF中的一个非终结符（如`program()`、`stmt()`、`expr()`）。例如，`stmt()` 函数会检查当前的Token类型，来决定是调用 `if_stmt()` 还是 `while_stmt()` 等函数来解析具体的语句。
    *   **错误处理**：若Token序列不符合文法预期（如 `if` 后面没有左括号），解析器会抛出一个 `ParserError` 异常，并附带精确的行列号信息。

*   **`src/interpreter.py` - 解释器**
    *   **职责**：接收语法分析器生成的AST，并通过**遍历**这棵树来实际执行代码逻辑。
    *   **实现**：采用**访问者模式 (Visitor Pattern)**。`Interpreter` 类为每一种AST节点（如 `IfStmt`）都实现了一个对应的 `visit_IfStmt` 方法。遍历AST时，会根据当前节点的类型动态调用相应的访问方法。
    *   **作用域管理**：`Scope` 类是实现变量和函数作用域的关键。每个 `Scope` 对象内部有一个字典用于存放变量。当进入一个新的代码块（如函数调用），会创建一个新的 `Scope`，并将其父作用域设置为当前的 `Scope`。查找变量时，会先在当前作用域查找，如果找不到，则沿着父作用域链向上查找，直至全局作用域。
    *   **函数调用**：通过创建新的 `Scope` 来模拟函数调用栈帧。函数的返回值则通过抛出一个特殊的 `ReturnValue` 异常来实现，这种方式可以清晰地中断当前执行流并向上层返回结果。
    *   **扩展功能实现细节**：
        *   **字符串**：在 `visit_BinaryOp` 方法中，通过 `isinstance()` 检查操作数是否为字符串，若是，则执行字符串的拼接或重复逻辑，而非数值计算。
        *   **数组与结构体**：通过 `StructDefinition` (蓝图) 和 `StructInstance` (实例) 两个辅助类来管理结构体。L25的数组在底层被直接映射为Python的 `list`。对它们的访问和赋值（如`a.b = 1`或`arr[0] = 1`）在 `visit_AssignStmt` 方法中通过检查左侧节点的类型（是`MemberAccess`还是`ArrayAccess`）来分别处理。
        *   **Try-Catch**：解释器内有一个 `self.is_in_try_block` 标志位。进入`try`块时将其设为`True`。在 `visit_BinaryOp` 中执行除法时，若除数为零且此标志位为`True`，则抛出一个可识别的`InterpreterError`。此错误在 `visit_TryCatch` 方法中被捕获，然后解释器会转而执行 `catch` 块的AST节点，从而实现了异常处理流程。

### 3.3 Web界面

*   **`app.py`**：基于轻量级Web框架 **Flask** 搭建。它定义了两个路由：
    1.  `/`：渲染并返回主页面 `index.html`。
    2.  `/compile`：一个API接口，接收前端发来的L25代码。它通过重定向 `sys.stdout` 到一个内存中的 `StringIO` 对象来捕获所有 `output()` 语句的输出，然后将捕获到的输出和任何可能发生的错误信息打包成JSON格式返回给前端。
*   **`templates/index.html`** 和 **`static/style.css`**：共同构建了用户界面。HTML负责结构，CSS负责美化，而页面内的JavaScript负责与后端 `/compile` 接口通信，实现了无需刷新页面的异步代码执行。

## 4. 使用说明

### 4.1 环境配置

1.  **创建虚拟环境**：`python3 -m venv venv`
2.  **激活虚拟环境**：`source venv/bin/activate` (在macOS/Linux)
3.  **安装依赖**：`pip install -r requirements.txt`

### 4.2 运行方式

#### 命令行模式
```bash
# 激活虚拟环境后，使用以下命令运行.l25文件
python3 -m src.main tests/test_programs/full_features.l25
```

#### Web界面模式
```bash
# 激活虚拟环境后，使用以下命令启动Web服务器
python3 app.py
```
启动后，浏览器访问 `http://127.0.0.1:5001` 即可打开在线编译器。

## 5. 测试结果截图

**操作指南**：
1.  启动Web界面 (`python3 app.py`)。
2.  在浏览器中打开 `http://127.0.0.1:5001`。
3.  点击 "Load Example" -> "Full Features" 按钮，然后点击 "Run"。
4.  将运行结果截图，并粘贴到下方。
5.  重复以上步骤，测试 "Factorial" 示例。

**(请在此处粘贴 comprehensive_test_result.png 截图)**
*一张显示 `full_features.l25` 代码及正确运行结果的Web界面截图*

**(请在此处粘贴 factorial_test_result.png 截图)**
*一张显示 `factorial.l25` 代码及正确运行结果的Web界面截图*