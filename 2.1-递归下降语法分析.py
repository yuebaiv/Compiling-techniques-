# 递归下降分析器实现
# 作者：张奇
# 日期：2024-12-5

# 全局变量
filename = ""
vt_table = []
read_vt_index = 0
error_flag = 0
step = 1

def info():
    global step
    print(f'-----Step: {step}-----')
    print("当前步骤动作：", end='')
    print(method)
    print()
    step += 1

def Read():
    global filename, vt_table
    filename = input("请输入文件名: ")
    try:
        with open(filename + ".txt", 'r', encoding='utf-8') as f1:
            for line in f1:
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    vt_table.append([int(parts[0]), parts[1]])
                else:
                    print(f"警告: 无效的记号格式在行: {line}")
    except FileNotFoundError:
        print(f"错误: 文件 '{filename}.txt' 未找到。")
        exit(1)

def match(expected_vt):
    global read_vt_index, error_flag
    if error_flag:
        return
    if read_vt_index >= len(vt_table):
        error(f"Unexpected end of input, expected '{expected_vt}'")
        return
    current_token = vt_table[read_vt_index][1]
    if current_token != expected_vt:
        error(f"Expected '{expected_vt}', but found '{current_token}'")
        return
    read_vt_index += 1

def program():
    global method
    method = "program\t-->\tblock"
    info()
    block()

def block():
    global method
    method = "block\t-->\t{ stmts }"
    info()
    match("{")
    stmts()
    match("}")

def stmts():
    global method
    if read_vt_index < len(vt_table) and vt_table[read_vt_index][1] != '}':
        method = "stmts\t-->\tstmt stmts"
        info()
        stmt()
        stmts()
    else:
        method = "stmts\t-->\tnull"
        info()
        # ε 产生式，不需要进一步操作

def stmt():
    global method
    if read_vt_index >= len(vt_table):
        error("Unexpected end of input in stmt")
        return
    current_token = vt_table[read_vt_index][1]

    if current_token == "if":
        method = "stmt\t-->\tif ( bool ) stmt [else stmt]"
        info()
        match("if")
        match("(")
        boolean()
        match(")")
        stmt()
        if read_vt_index < len(vt_table) and vt_table[read_vt_index][1] == "else":
            match("else")
            stmt()
    elif current_token == "while":
        method = "stmt\t-->\twhile ( bool ) stmt"
        info()
        match("while")
        match("(")
        boolean()
        match(")")
        stmt()
    elif current_token == "do":
        method = "stmt\t-->\tdo stmt while ( bool )"
        info()
        match("do")
        stmt()
        match("while")
        match("(")
        boolean()
        match(")")
    elif current_token == "break":
        method = "stmt\t-->\tbreak"
        info()
        match("break")
    elif current_token == "{":
        method = "stmt\t-->\tblock"
        info()
        block()
    elif vt_table[read_vt_index][0] == 42:  # id
        method = "stmt\t-->\tid = expr ;"
        info()
        match("id")
        match("=")
        expr()
        match(";")
    else:
        error(f"Unexpected token '{current_token}' in stmt")

def boolean():
    global method
    method = "bool\t-->\texpr relop expr"
    info()
    expr()
    if read_vt_index < len(vt_table):
        relop = vt_table[read_vt_index][1]
        if relop in ["<", "<=", ">", ">=", "==", "!="]:
            match(relop)
            expr()
        else:
            error(f"Expected a relational operator, but found '{relop}'")
    else:
        error("Unexpected end of input in boolean expression")

def expr():
    global method
    method = "expr\t-->\tterme expr1"
    info()
    term()
    expr1()

def expr1():
    global method
    if read_vt_index < len(vt_table):
        current_token = vt_table[read_vt_index][1]
        if current_token == "+":
            method = "expr1\t-->\t+ term expr1"
            info()
            match("+")
            term()
            expr1()
        elif current_token == "-":
            method = "expr1\t-->\t- term expr1"
            info()
            match("-")
            term()
            expr1()
        else:
            method = "expr1\t-->\tnull"
            info()
            # ε 产生式，不需要进一步操作

def term():
    global method
    method = "term\t-->\tfactor term1"
    info()
    factor()
    term1()

def term1():
    global method
    if read_vt_index < len(vt_table):
        current_token = vt_table[read_vt_index][1]
        if current_token == "*":
            method = "term1\t-->\t* factor term1"
            info()
            match("*")
            factor()
            term1()
        elif current_token == "/":
            method = "term1\t-->\t/ factor term1"
            info()
            match("/")
            factor()
            term1()
        else:
            method = "term1\t-->\tnull"
            info()
            # ε 产生式，不需要进一步操作

def factor():
    global method
    if read_vt_index >= len(vt_table):
        error("Unexpected end of input in factor")
        return
    current_token = vt_table[read_vt_index][1]
    if current_token == "(":
        method = "factor\t-->\t( expr )"
        info()
        match("(")
        expr()
        match(")")
    elif vt_table[read_vt_index][0] in [43, 44, 45, 46, 47]:  # num
        method = "factor\t-->\tnum"
        info()
        match("num")
    elif vt_table[read_vt_index][0] == 42:  # id
        method = "factor\t-->\tid"
        info()
        match("id")
    else:
        error(f"Unexpected token '{current_token}' in factor")

def error(message="Syntax Error"):
    global error_flag
    error_flag = 1
    print(f"Error: {message}")

if __name__ == "__main__":
    Read()
    print("----------- Step 1: 词法分析完成，开始语法分析 --------------")
    program()

    if read_vt_index == len(vt_table) and not error_flag:
        print("递归下降语法分析成功。")
    elif not error_flag:
        print("警告: 语法分析完成，但存在未消耗的输入。")
    else:
        print("递归下降语法分析失败。")
