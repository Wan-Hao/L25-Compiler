以下是将PDF内容转换为Markdown格式的版本，保留了纯文本内容和基本格式：

---

# 2025 年《编译原理与实践》大作业要求

下面是用EBNF描述的L25语言，使用到的EBNF元符号含义同教材P13，所有的终结符用双引号括起表示。

```ebnf
<program> = "program" <ident> "{" { <func_def> } "main" "{" <stmt_list> "}" "}"

<func_def> = "func" <ident> "(" [ <param_list> ] ")" "{" <stmt_list> "return" <expr> ";" "}"

<param_list> = <ident> { "," <ident> }

<stmt_list> = <stmt> ";" { <stmt> ";" }

<stmt> = <declare_stmt> | <assign_stmt> | <if_stmt> | <while_stmt> | <input_stmt> | <output_stmt> | <func_call>

<declare_stmt> = "let" <ident> [ "=" <expr> ]

<assign_stmt> = <ident> "=" <expr>

<if_stmt> = "if" "(" <bool_expr> ")" "{" <stmt_list> "}" [ "else" "{" <stmt_list> "}" ]

<while_stmt> = "while" "(" <bool_expr> ")" "{" <stmt_list> "}"

<func_call> = <ident> "(" [ <arg_list> ] ")"

<arg_list> = <expr> { "," <expr> }

<input_stmt> = "input" "(" <ident> { "," <ident> } ")"

<output_stmt> = "output" "(" <expr> { "," <expr> } ")"

<bool_expr> = <expr> ("==" | "!=" | "<" | "<=" | ">" | ">=") <expr>

<expr> = [ "+" | "-" ] <term> { ("+" | "-") <term> }

<term> = <factor> { ("*" | "/") <factor> }

<factor> = <ident> | <number> | "(" <expr> ")" | <func_call>

<ident> = <letter> { <letter> | <digit> }

<number> = <digit> { <digit> }

<letter> = "a" | "b" | ... | "z" | "A" | "B" | ... | "Z"

<digit> = "0" | "1" | ... | "9"
```

示例代码：
```c
program MyApp {
    func add(a, b) {
        let sum = a + b;
        return sum;
    }
    func square(x) {
        let result = x * x;
        return result;
    }
    main {
        let x = 5;
        let y = add(x, 10);
        let z = square(y);
        if (z > 50) {
            output(z);
        } else {
            output(0);
        };
    }
}
```

注意L25语言的语法要求为：

1. `func`体里最后必须有`return`；
2. `main`或普通语句块里不能使用`return`；
3. 每个`stmt_list`至少有一条语句。

## 作业要求：

1. 要求每位同学对（扩展后的）L25语言，使用C/C++/Java/Python/flex/bison编写其编译器，要求完成词法分析、语法分析、出错处理、代码生成和解释程序。满分为100分。
2. 用该语言编写至少三个有一定逻辑功能的程序（如求一个整数的阶乘等），用自己编写的编译器对程序进行编译，输出正确的结果。
3. 文档及程序皆不能抄袭其他同学的，抄袭者与被抄袭者将获得同样的结果，所以同学们有保护自己的劳动成果不被他人窃取的权力与义务。同时，这门课鼓励同学们发表意见，并进行交流与讨论，这与抄袭是不同的。

## 作业提交：

此次作业需要提交到FTP服务器上（不需要在超星上提交）。分为三个子目录：文档、程序和测试。文档中需要对编译器的设计和运行方式进行说明，包括给出（扩展后）文法定义、代码结构、运行方式、测试结果截图等。程序目录下需包含源程序和可执行程序。测试目录下包含测试用例。

## 作业检查：

检查时间为每周三上午上机时间，地点在机房，历时4周。作业由教师和助教检查，被检查者会被要求执行自己准备的测试用例，也可能需要执行教师或助教给出的测试用例，执行测试用例必须得到正确的结果，被检查者需要就源程序及文档回答一些问题，如被检查者不能正确完成上述任务，则不能够通过检查。

为了避免检查冲突，将把大家分成若干组，通过发送邮件的方式确定各人分组情况（具体请注意各班任课教师通知）。每组必须完成对该语言的指定扩展（自行修改EBNF描述，但不能改变原语言的主体结构）。分组及指定扩展要求如下：

- 第一组：无扩展
- 第二组：支持字符串与字符串基本运算。增加`str`类型定义，支持字符串字面量，如`"hello world"`，`str`的基本运算符有`"+"`和`"*"`：两个字符串之间的`"+"`运算得到它们之间的连接，字符串与整数之间的`"+"`运算定义为将整数转化为字符串后得到的串；字符串`str`与整数`n`之间的`"*"`，定义为`n`个`str`相连接。
- 第三组：支持一维静态数组和结构体（`struct`）的声明、赋值和访问使用。
- 第四组：引入`try-catch`语句，在程序运行（解释执行）时，遇到`try`块中的任何除法运算，如果发现分母是0，则报出错误提醒并跳转到最近的`catch`块继续执行。

## 评分规则

1. 文档、程序、测试用例齐全，并完成所在分组的指定扩展点，成绩为75分（无界面）~80分（有良好的用户界面）。
2. 实现以下功能或要求的，需申请由教师进行检查，根据实际情况给予1~25分的加分（加到100分为止）。申请加分的同学需在文档中标注加分项目，并在检查时主动演示。平行班任课老师将在检查完毕后沟通各班级完成情况，共同评判确定加分值：
    - 支持指针类型的定义和使用，可以参考C语言中的指针概念，但不强制实现完整的内存管理；
    - 支持`map`（字典）和`set`（集合）类型的定义和使用，基本操作包括插入、删除、查找和遍历等；
    - 在编译器的实现中使用本课程未介绍过的业界编译工具/框架，如ANTLR、JavaCC、LLVM和仓颉等，在使用这些编译工具或框架时可以使用新的中间表示。
3. 不合格。以下任何一项都将导致最终成绩不合格：
    - 超过规定期限未上传作业到FTP上的；
    - 未接受作业检查的；
    - 有抄袭行为的；
    - 不能提供源程序的；
    - 无文档说明的。

其他未尽事宜，以任课老师的规定为准。

## 详情
作为 第四组 的作业，我需要你完成上述对应的要求。

---

## 更新后的 EBNF
```ebnf
(*)<program>      = "program" <ident> "{" { <struct_def> | <func_def> } "main" "{" <stmt_list> "}" "}"

   <func_def>      = "func" <ident> "(" [ <param_list> ] ")" "{" <stmt_list> "return" <expr> ";" "}"

(*)<struct_def>    = "struct" <ident> "{" <param_list> "}" ";"

   <param_list>    = <ident> { "," <ident> }

   <stmt_list>     = <stmt> ";" { <stmt> ";" }

(*)<stmt>          = <declare_stmt> | <assign_stmt> | <if_stmt> | <while_stmt>
                  | <input_stmt> | <output_stmt> | <func_call> | <try_catch_stmt>

(*)<try_catch_stmt> = "try" "{" <stmt_list> "}" "catch" "{" <stmt_list> "}"

   <declare_stmt>  = "let" <ident> [ "=" <expr> ]

(*)<assign_stmt>   = <lvalue> "=" <expr>

(*)<lvalue>        = <ident> { "." <ident> | "[" <expr> "]" }

   <if_stmt>       = "if" "(" <bool_expr> ")" "{" <stmt_list> "}" [ "else" "{" <stmt_list> "}" ]

   <while_stmt>    = "while" "(" <bool_expr> ")" "{" <stmt_list> "}"

(*)<func_call>     = <ident_path> "(" [ <arg_list> ] ")"
                   (* 注意: func_call现在可以是 a.b() 这样的形式 *)

   <arg_list>      = <expr> { "," <expr> }

   <input_stmt>    = "input" "(" <ident> { "," <ident> } ")"

   <output_stmt>   = "output" "(" <expr> { "," <expr> } ")"

   <bool_expr>     = <expr> ("==" | "!=" | "<" | "<=" | ">" | ">=") <expr>

   <expr>          = [ "+" | "-" ] <term> { ("+" | "-") <term> }

   <term>          = <factor> { ("*" | "/") <factor> }

(*)<factor>        = <primary> { <accessor> }

(*)<primary>       = <ident> | <number> | <string_literal> | <array_literal> | "(" <expr> ")"

(*)<accessor>      = "." <ident>             (* Member Access *)
                  | "[" <expr> "]"          (* Array Access *)
                  | "(" [ <arg_list> ] ")"  (* Function Call / Struct Init *)

(*)<array_literal> = "[" [ <arg_list> ] "]"

(*)<ident_path>    = <ident> { "." <ident> } (* 用于 a.b 这样的函数调用路径 *)

   <ident>         = <letter> { <letter> | <digit> | "_" }
   <number>        = <digit> { <digit> }
(*)<string_literal> = "\"" { <any_char_except_quote> } "\""
```

