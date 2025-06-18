# L25 编译器技术实现细节

本文档旨在深入剖析 L25 编译器的内部实现原理，逐一解析核心模块的设计思路与关键代码逻辑。

## 文件 1: `src/lexer.py` - 词法分析器

#### **1. 核心职责**
词法分析器的任务是将原始的、无结构的L25源代码字符串，转化为一个有序的、结构化的 **Token（记号）序列**。它是编译流程的第一步，为后续的语法分析做准备。

#### **2. 实现机制：单遍扫描**
本词法分析器采用**单遍扫描**（Single-Pass）的方法，从头到尾逐个字符地读取源代码，具有高效、简单的优点。

*   **主循环**: `get_next_token()` 方法是词法分析的核心。它在一个 `while` 循环中持续运行，只要未读到文件末尾（`self.current_char is not None`），就会不断生成新的Token。
*   **字符分类与分发**: 在循环内部，通过一连串的 `if/elif` 条件判断来识别当前字符的类型，并调用相应的处理函数。
    *   **空白字符**: `if self.current_char.isspace()` 会直接跳过所有空白符（空格、制表符、换行符）。
    *   **数字**: `if self.current_char.isdigit()` 会触发 `number()` 方法，该方法会持续读取所有连续的数字字符，将它们拼接成一个字符串，最后转换为整数，并返回一个 `NUMBER`类型的Token。
    *   **字符串字面量**: `if self.current_char == '"'` 会触发 `string()` 方法，该方法会读取两个双引号之间的所有字符，并返回一个 `STRING`类型的Token。
    *   **标识符与关键字**: `if self.current_char.isalnum() or self.current_char == '_'` 会触发 `identifier()` 方法。该方法会读取所有连续的字母、数字和下划线。读取完毕后，它会将得到的字符串在一个预定义的关键字字典 `token_map` 中进行查找。如果找到了，就返回对应的关键字Token（如 `PROGRAM`、`IF`）；如果没找到，就将其作为普通的 `IDENT` (标识符) Token返回。
    *   **操作符**: 对于 `=`、`!`、`<`、`>` 等可能构成双字符操作符的符号，词法分析器会进行**“向前看（Lookahead）”**操作。例如，当读到 `!` 时，它会检查下一个字符是否为 `=`。如果是，则消耗两个字符并生成一个 `NEQ` (`!=`) Token；如果不是，则忽略这个无效的 `!` 字符。对于简单的单字符操作符，则直接在 `single_char_tokens` 字典中查找并返回。

## 文件 2: `src/ast.py` - 抽象语法树

#### **1. 核心职责**
此文件的唯一职责是**定义数据结构**。它不包含任何执行逻辑。文件中的每一个类都代表了L25语言中的一种语法结构（如一条语句、一个表达式等），它们是语法分析阶段的输出，也是解释执行阶段的输入。

#### **2. 实现机制：节点类**
*   **基类**: 所有的节点类都继承自一个空基类 `ASTNode`，这为我们后续进行类型检查或实现访问者模式提供了便利。
*   **结构映射**: AST节点的结构严格映射了代码的逻辑层级。例如，`let sum = a + b;` 这行代码会被解析成如下的树状结构：
    ```
    DeclareStmt(
        ident=Identifier(token=Token(IDENT, 'sum')),
        expr=BinaryOp(
            left=Identifier(token=Token(IDENT, 'a')),
            op=Token(PLUS, '+'),
            right=Identifier(token=Token(IDENT, 'b'))
        )
    )
    ```
    这种树状结构清晰地表达了原始代码的运算优先级和组成关系。

## 文件 3: `src/parser.py` - 语法分析器

#### **1. 核心职责**
语法分析器的任务是消费词法分析器生成的Token序列，并根据L25的EBNF文法规则，构建起一棵完整的抽象语法树(AST)。**这是验证代码语法正确性的核心步骤。**

#### **2. 实现机制：递归下降分析**
本解析器采用经典的**递归下降（Recursive Descent）**方法，为EBNF中的每个主要非终结符（如 `program`、`stmt`、`expr`）都编写了一个对应的解析函数。

*   **核心方法 `eat()`**: 这个辅助方法是解析器的基石。它检查 `self.current_token` 是否是预期的类型。如果是，它就“吃掉”（消费）这个Token，并将Token流的指针向前移动一位；如果不是，则抛出 `ParserError`，报告一个语法错误。
*   **递归调用**: 解析过程是一个自顶向下的递归调用链。`parse()` 调用 `program()`，`program()` 调用 `stmt_list()`，`stmt_list()` 调用 `stmt()`，而 `stmt()` 则根据当前Token的类型，选择调用 `if_stmt()`、`while_stmt()` 或其他语句的解析函数。
*   **处理表达式优先级**:
    *   L25语言中，`*` 和 `/` 的优先级高于 `+` 和 `-`。这是通过将表达式解析拆分成 `expr()`、`term()` 和 `factor()` 三个层次的函数来实现的。
    *   `expr()`: 负责处理最低优先级的 `+` 和 `-`。它会循环调用 `term()` 来获取操作数。
    *   `term()`: 负责处理更高优先级的 `*` 和 `/`。它会循环调用 `factor()` 来获取操作数。
    *   `factor()`: 负责处理最高优先级的元素，如单个数字、变量、括号内的表达式等。
    *   这个结构确保了在计算一个如 `a + b * c` 的表达式时，`b * c` 会先在 `term()` 层面被解析和组合成一个 `BinaryOp` 节点，然后这个节点才会作为 `+` 的右操作数在 `expr()` 层面被处理。
*   **处理复杂表达式（函数调用、数组成员访问等）**: 为了正确解析如 `my_func(a, b).field[i]` 这样的链式调用，解析器引入了 `call_access()` 和 `primary()` 两个函数。`primary()` 负责解析最基础的单元（如一个`IDENT`或一个数字），而 `call_access()` 则在一个 `while` 循环中处理后续的 `.`、`[` 或 `(`，不断地将前一个解析结果包装成新的、更复杂的AST节点（如 `MemberAccess`, `ArrayAccess`, `FuncCall`）。

## 文件 4: `src/interpreter.py` - 解释器

#### **1. 核心职责**
解释器的任务是接收语法分析器生成的AST，**遍历**这棵树，并根据每个节点的语义来**执行**代码逻辑，最终得出程序的运行结果。

#### **2. 实现机制：AST遍历与动态分发**
*   **访问者模式 (Visitor Pattern)**: 解释器为每一种AST节点都实现了一个 `visit_NodeTypeName` 方法（例如 `visit_IfStmt`, `visit_BinaryOp`）。主 `visit()` 方法接收一个AST节点，然后通过 `getattr()` 动态地查找并调用与该节点类型匹配的 `visit_...` 方法。这种设计使得代码结构清晰，易于扩展。
*   **作用域管理 (`Scope` 类)**:
    *   `Scope` 类是实现变量查找、函数定义等功能的关键。每个 `Scope` 实例代表一个作用域（如全局作用域、函数作用域）。
    *   它内部包含一个指向**父作用域**的 `parent` 指针。当进入一个新函数时，会创建一个新的 `Scope`，并将其 `parent` 设置为全局作用域，从而形成一条**作用域链**。
    *   **变量查找**: `get()` 方法实现了变量的查找逻辑。它首先在当前作用域的 `variables` 字典中查找。如果找不到，它会通过 `self.parent.get()` 递归地到父作用域中去查找，直至最顶层的全局作用域。
*   **函数调用与返回**:
    *   **调用**: 当解释器访问一个 `FuncCall` 节点时，它会：1) 查找函数定义；2) 创建一个新的函数作用域(`func_scope`)；3) 计算所有参数表达式的值；4) 在 `func_scope` 中将参数名与计算出的值绑定；5) 调用 `visit()` 方法开始执行函数体的AST。
    *   **返回**: 函数的 `return` 语句是通过**抛出异常**这一巧妙的机制实现的。当访问 `ReturnStmt` 节点时，解释器会抛出一个特殊的 `ReturnValue` 异常，该异常对象中携带着返回值。这个异常会被 `visit_FuncCall` 方法中的 `try...except ReturnValue` 块捕获。这样做的好处是，`return` 可以立即中断深层嵌套的执行流，并将返回值直接传递给调用处，而无需在每一层 `visit` 调用中都手动传递返回值。
*   **Try-Catch 实现**:
    *   解释器维护一个布尔标志 `self.is_in_try_block`。
    *   当进入 `visit_TryCatch` 方法时，它首先在一个Python的 `try...finally` 块中将这个标志位设为 `True`，然后开始访问 `try` 块的AST。
    *   在 `visit_BinaryOp` 方法中，当进行除法运算时，如果发现除数为零，它会检查 `self.is_in_try_block` 标志。如果为 `True`，它就抛出一个带有特定信息的 `InterpreterError`。
    *   这个 `InterpreterError` 会被 `visit_TryCatch` 中的 `except InterpreterError` 块捕获。捕获后，解释器不会向上抛出错误，而是转而去访问 `catch` 块的AST，从而实现了流程的跳转。`finally` 块确保无论是否发生异常，`is_in_try_block` 标志位最终都会被恢复。

## 文件 5: `app.py` - Web 应用服务

#### **1. 核心职责**
提供一个基于Flask的HTTP服务，作为Web界面的后端，处理前端的编译请求。

#### **2. 实现机制**
*   **Flask 路由**: 使用 `@app.route()` 装饰器定义了两个URL端点：
    *   `/`: 处理根URL的GET请求，使用 `render_template()` 函数渲染 `index.html` 并将其返回给浏览器。在渲染前，它会从文件中加载所有示例代码，并通过模板变量传递给HTML。
    *   `/compile`: 处理POST请求。这是执行编译的核心API。
*   **输出捕获**: L25语言的 `output()` 语句在解释器中是靠Python的 `print()` 函数实现的。为了在Web应用中捕获这些输出，`/compile` 接口使用了一个精巧的技巧：
    1.  `old_stdout = sys.stdout`: 保存原始的系统标准输出流。
    2.  `sys.stdout = captured_output = io.StringIO()`: 将 `sys.stdout` 重定向到一个内存中的字符串缓冲区 `StringIO`。
    3.  在此之后，任何对 `print()` 的调用，其输出内容都会被写入这个 `captured_output` 对象中，而不是打印在服务器的控制台。
    4.  `try...finally` 块确保在请求处理结束时，`sys.stdout = old_stdout` 会被执行，将标准输出恢复原状，避免对服务器造成影响。
*   **JSON通信**: `/compile` 接口接收JSON格式的请求体（`{"code": "..."}`），在处理完毕后，也返回JSON格式的响应（`{"output": "...", "error": "..."}`）。这种前后端分离的通信方式是现代Web开发的标准实践。

## 补充：运算符优先级处理
```c++
expr() ← term() ← factor() ← call_access() ← primary()
 ↑        ↑         ↑           ↑            ↑
+,-     *,/      一元+,-    .[]()访问      基本元素
```