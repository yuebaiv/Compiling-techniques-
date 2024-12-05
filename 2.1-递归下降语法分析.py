# 递归下降分析器实现
# 作者：张奇
# 日期：2024-12-05

# 全局变量
filename = ""
vt_table = []
read_vt_index = 0
error_flag = 0
step = 1
stack = []
method = ""

# 定义词法类型映射（根据您的词法表调整）
symbol_type_map = {
    'id': '42',
    'num': ['43', '44', '45', '46', '47'],  # 所有数字类型
    '{': '28',
    '}': '29',
    '(': '31',
    ')': '32',
    ';': '30',
    '=': '26',
    '<=': '41',
    '>=': '40',
    '<': '33',  # 添加小于运算符
    '>': '34',  # 添加大于运算符
    '+': '22',
    '-': '23',  # 假设 '-' 为 '23'
    '*': '24',
    '/': '25',
    'while': '3',
    'if': '4',
    'else': '5',
    'do': '6',
    'break': '7',
    'int': '8',    # 新增 'int' 类型编号
    'EOF': '0'
}

def info():
    global step, stack, method
    print(f'-----Step: {step}-----')
    print("识别串：=>", end=' ')
    for symbol in stack:
        print(symbol, end=' ')
    print()
    print(f'动作：{method}')
    print()
    step += 1

def Read():
    global filename
    filename = input("请输入文件名: ")
    try:
        with open(filename + ".txt", encoding='utf-8') as f1:
            for line in f1:
                tokens = line.strip().split(',')
                if len(tokens) >= 2:
                    vt_table.append(tokens[:2])
        # 添加EOF标记
        if vt_table[-1][1] != 'EOF':
            vt_table.append(['0', 'EOF'])
        print("\n词法表读取成功，内容如下：")
        for idx, token in enumerate(vt_table):
            print(f"{idx}: {token}")
        print()
    except FileNotFoundError:
        print(f"文件 {filename}.txt 未找到。")
        exit(1)
    except Exception as e:
        print(f"读取文件时出错: {e}")
        exit(1)

def match(expected_type):
    global read_vt_index, error_flag
    if error_flag:
        return
    if read_vt_index >= len(vt_table):
        error()
        print(f'匹配失败：已达到词法表末尾，无法匹配 {expected_type}')
        return
    current_type = vt_table[read_vt_index][0]
    current_symbol = vt_table[read_vt_index][1]
    print(f"匹配: 需要的类型 '{expected_type}'，当前类型 '{current_type}'（符号 '{current_symbol}'，索引 {read_vt_index}）")
    if isinstance(expected_type, list):
        if current_type not in expected_type:
            error()
            print(f'当前类型 "{current_type}" 与需要的类型 "{expected_type}" 不匹配')
            return
    else:
        if expected_type != current_type:
            error()
            print(f'当前类型 "{current_type}" 与需要的类型 "{expected_type}" 不匹配')
            return
    read_vt_index += 1

def program():
    global error_flag, method, stack
    if error_flag:
        return
    method = "program\t-->\tblock"
    info()
    index = len(stack) - stack[::-1].index("program") - 1
    stack = stack[:index] + ["block"] + stack[index+1:]
    block()

def block():
    global error_flag, method, stack
    if error_flag:
        return
    method = "block\t-->\t{ stmts }"
    info()
    try:
        index = len(stack) - stack[::-1].index("block") - 1
    except ValueError:
        print("错误：stack 中找不到 'block'")
        error()
        return
    stack = stack[:index] + ["{", "stmts", "}"] + stack[index+1:]
    match(symbol_type_map['{'])
    stmts()
    match(symbol_type_map['}'])

def stmts():
    global read_vt_index, error_flag, method, stack
    if error_flag:
        return
    if read_vt_index >= len(vt_table):
        error()
        print("错误：stmts 中读取超出范围")
        return
    current_type = vt_table[read_vt_index][0]
    if current_type == symbol_type_map['EOF'] or current_type == symbol_type_map['}']:
        method = "stmts\t-->\tnull"
        info()
        try:
            index = len(stack) - stack[::-1].index("stmts") - 1
        except ValueError:
            print("错误：stack 中找不到 'stmts'")
            error()
            return
        stack = stack[:index] + stack[index + 1:]
        return
    elif current_type == symbol_type_map['int']:
        method = "stmts\t-->\tdecl stmts"
        info()
        try:
            index = len(stack) - stack[::-1].index("stmts") - 1
        except ValueError:
            print("错误：stack 中找不到 'stmts'")
            error()
            return
        stack = stack[:index] + ["decl", "stmts"] + stack[index + 1:]
        decl()
        stmts()
    else:
        method = "stmts\t-->\tstmt stmts"
        info()
        try:
            index = len(stack) - stack[::-1].index("stmts") - 1
        except ValueError:
            print("错误：stack 中找不到 'stmts'")
            error()
            return
        stack = stack[:index] + ["stmt", "stmts"] + stack[index + 1:]
        stmt()
        stmts()

def stmt():
    global read_vt_index, error_flag, method, stack
    if error_flag:
        return
    if read_vt_index >= len(vt_table):
        error()
        print("错误：stmt 中读取超出范围")
        return
    current_type = vt_table[read_vt_index][0]
    current_symbol = vt_table[read_vt_index][1]

    if current_type == symbol_type_map['id']:  # id
        method = "stmt\t-->\tid = expr ;"
        info()
        try:
            index = len(stack) - stack[::-1].index("stmt") - 1
        except ValueError:
            print("错误：stack 中找不到 'stmt'")
            error()
            return
        stack = stack[:index] + ["id", "=", "expr", ";"] + stack[index + 1:]
        match(symbol_type_map['id'])
        match(symbol_type_map['='])
        expr()
        match(symbol_type_map[';'])
    elif current_symbol == "while":
        method = "stmt\t-->\twhile ( boolean ) stmt"
        info()
        try:
            index = len(stack) - stack[::-1].index("stmt") - 1
        except ValueError:
            print("错误：stack 中找不到 'stmt'")
            error()
            return
        stack = stack[:index] + ["while", "(", "boolean", ")", "stmt"] + stack[index + 1:]
        match(symbol_type_map['while'])
        match(symbol_type_map['('])
        boolean()  # 调用修改后的 boolean 函数
        match(symbol_type_map[')'])
        stmt()
    elif current_symbol == "if":
        method = "stmt\t-->\tif ( boolean ) stmt [else stmt]"
        info()
        try:
            index = len(stack) - stack[::-1].index("stmt") - 1
        except ValueError:
            print("错误：stack 中找不到 'stmt'")
            error()
            return
        stack = stack[:index] + ["if", "(", "boolean", ")", "stmt"] + stack[index + 1:]
        match(symbol_type_map['if'])
        match(symbol_type_map['('])
        boolean()
        match(symbol_type_map[')'])
        stmt()
        # 检查是否有 else
        if read_vt_index < len(vt_table) and vt_table[read_vt_index][1] == "else":
            method = "stmt\t-->\tif ( boolean ) stmt else stmt"
            info()
            try:
                index = len(stack) - stack[::-1].index("stmt") - 1
            except ValueError:
                print("错误：stack 中找不到 'stmt'")
                error()
                return
            stack = stack[:index] + ["else", "stmt"] + stack[index + 1:]
            match(symbol_type_map['else'])
            stmt()
    elif current_symbol == "do":
        method = "stmt\t-->\tdo stmt while ( boolean )"
        info()
        try:
            index = len(stack) - stack[::-1].index("stmt") - 1
        except ValueError:
            print("错误：stack 中找不到 'stmt'")
            error()
            return
        stack = stack[:index] + ["do", "stmt", "while", "(", "boolean", ")"] + stack[index + 1:]
        match(symbol_type_map['do'])
        stmt()
        match(symbol_type_map['while'])
        match(symbol_type_map['('])
        boolean()
        match(symbol_type_map[')'])
    elif current_symbol == "break":
        method = "stmt\t-->\tbreak ;"
        info()
        try:
            index = len(stack) - stack[::-1].index("stmt") - 1
        except ValueError:
            print("错误：stack 中找不到 'stmt'")
            error()
            return
        stack = stack[:index] + ["break", ";"] + stack[index + 1:]
        match(symbol_type_map['break'])
        match(symbol_type_map[';'])
    else:
        method = "stmt\t-->\tblock"
        info()
        try:
            index = len(stack) - stack[::-1].index("stmt") - 1
        except ValueError:
            print("错误：stack 中找不到 'stmt'")
            error()
            return
        stack = stack[:index] + ["block"] + stack[index + 1:]
        block()

def decl():
    global read_vt_index, error_flag, method, stack
    # decl -> int id [= expr] ;
    method = "decl\t-->\tint id [= expr] ;"
    info()
    try:
        index = len(stack) - stack[::-1].index("decl") - 1
    except ValueError:
        print("错误：stack 中找不到 'decl'")
        error()
        return
    stack = stack[:index] + ["int", "id", "[= expr]", ";"] + stack[index + 1:]
    match(symbol_type_map['int'])
    match(symbol_type_map['id'])
    # Check for optional initialization
    if read_vt_index < len(vt_table) and vt_table[read_vt_index][1] == "=":
        match(symbol_type_map['='])
        expr()
    match(symbol_type_map[';'])

def boolean():
    global read_vt_index, error_flag, method, stack
    if error_flag:
        return

    method = "boolean --> expr [comp_op expr]"
    info()
    try:
        index = len(stack) - stack[::-1].index("boolean") - 1
    except ValueError:
        print("错误：stack 中找不到 'boolean'")
        error()
        return

    # 首先处理第一个表达式
    stack = stack[:index] + ["expr"] + stack[index + 1:]
    expr()

    # 检查是否有比较运算符
    if read_vt_index < len(vt_table):
        current_symbol = vt_table[read_vt_index][1]
        if current_symbol in ['<', '<=', '>', '>=']:
            comp_type = symbol_type_map[current_symbol]
            match(comp_type)
            # 处理比较运算符后的第二个表达式
            try:
                index = len(stack) - stack[::-1].index("expr") - 1
            except ValueError:
                stack.append("expr")
                index = len(stack) - 1
            expr()


def expr():
    global read_vt_index, error_flag, method, stack
    if error_flag:
        return
    method = "expr\t-->\tterm expr1"
    info()
    try:
        index = len(stack) - stack[::-1].index("expr") - 1
    except ValueError:
        print("错误：stack 中找不到 'expr'")
        error()
        return
    stack = stack[:index] + ["term", "expr1"] + stack[index + 1:]
    term()
    expr1()


def expr1():
    global read_vt_index, error_flag, method, stack
    if error_flag:
        return
    if read_vt_index >= len(vt_table):
        error()
        print("错误：expr1 中读取超出范围")
        return
    current_symbol = vt_table[read_vt_index][1]

    # 处理算术运算符
    if current_symbol == "+":
        method = "expr1\t-->\t + term expr1"
        info()
        try:
            index = len(stack) - stack[::-1].index("expr1") - 1
        except ValueError:
            print("错误：stack 中找不到 'expr1'")
            error()
            return
        stack = stack[:index] + ["+", "term", "expr1"] + stack[index + 1:]
        match(symbol_type_map['+'])
        term()
        expr1()
    elif current_symbol == "-":
        method = "expr1\t-->\t - term expr1"
        info()
        try:
            index = len(stack) - stack[::-1].index("expr1") - 1
        except ValueError:
            print("错误：stack 中找不到 'expr1'")
            error()
            return
        stack = stack[:index] + ["-", "term", "expr1"] + stack[index + 1:]
        match(symbol_type_map['-'])
        term()
        expr1()
    # 处理比较运算符
    elif current_symbol in ['>=', '<=', '>', '<']:
        method = f"expr1\t-->\t {current_symbol} term"
        info()
        try:
            index = len(stack) - stack[::-1].index("expr1") - 1
        except ValueError:
            print("错误：stack 中找不到 'expr1'")
            error()
            return
        stack = stack[:index] + [current_symbol, "term"] + stack[index + 1:]
        match(symbol_type_map[current_symbol])
        term()
    else:
        method = "expr1\t-->\tnull"
        info()
        try:
            index = len(stack) - stack[::-1].index("expr1") - 1
        except ValueError:
            print("错误：stack 中找不到 'expr1'")
            error()
            return
        stack = stack[:index] + stack[index + 1:]
def term():
    global read_vt_index, error_flag, method, stack
    if error_flag:
        return
    method = "term\t-->\tfactor term1"
    info()
    try:
        index = len(stack) - stack[::-1].index("term") - 1
    except ValueError:
        print("错误：stack 中找不到 'term'")
        error()
        return
    stack = stack[:index] + ["factor", "term1"] + stack[index + 1:]
    factor()
    term1()

def term1():
    global read_vt_index, error_flag, method, stack
    if error_flag:
        return
    if read_vt_index >= len(vt_table):
        error()
        print("错误：term1 中读取超出范围")
        return
    current_symbol = vt_table[read_vt_index][1]
    if current_symbol == "*":
        method = "term1\t-->\t * factor term1"
        info()
        try:
            index = len(stack) - stack[::-1].index("term1") - 1
        except ValueError:
            print("错误：stack 中找不到 'term1'")
            error()
            return
        stack = stack[:index] + ["*", "factor", "term1"] + stack[index + 1:]
        match(symbol_type_map['*'])
        factor()
        term1()
    elif current_symbol == "/":
        method = "term1\t-->\t / factor term1"
        info()
        try:
            index = len(stack) - stack[::-1].index("term1") - 1
        except ValueError:
            print("错误：stack 中找不到 'term1'")
            error()
            return
        stack = stack[:index] + ["/", "factor", "term1"] + stack[index + 1:]
        match(symbol_type_map['/'])
        factor()
        term1()
    else:
        method = "term1\t-->\tnull"
        info()
        try:
            index = len(stack) - stack[::-1].index("term1") - 1
        except ValueError:
            print("错误：stack 中找不到 'term1'")
            error()
            return
        stack = stack[:index] + stack[index + 1:]

def factor():
    global read_vt_index, error_flag, method, stack
    if error_flag:
        return
    if read_vt_index >= len(vt_table):
        error()
        print("错误：factor 中读取超出范围")
        return
    current_type = vt_table[read_vt_index][0]
    current_symbol = vt_table[read_vt_index][1]
    if current_symbol == "(":
        method = "factor\t-->\t(expr)"
        info()
        try:
            index = len(stack) - stack[::-1].index("factor") - 1
        except ValueError:
            print("错误：stack 中找不到 'factor'")
            error()
            return
        stack = stack[:index] + ["(", "expr", ")"] + stack[index + 1:]
        match(symbol_type_map['('])
        expr()
        match(symbol_type_map[')'])
    elif current_type in symbol_type_map['num']:
        method = "factor\t-->\tnum"
        info()
        try:
            index = len(stack) - stack[::-1].index("factor") - 1
        except ValueError:
            print("错误：stack 中找不到 'factor'")
            error()
            return
        stack = stack[:index] + ["num"] + stack[index + 1:]
        # 由于 'num' 有多个类型编号，这里需要匹配任意一个
        if current_type in ['43', '44', '45', '46', '47']:
            match(current_type)
        else:
            error()
    elif current_type == symbol_type_map['id']:
        method = "factor\t-->\tid"
        info()
        try:
            index = len(stack) - stack[::-1].index("factor") - 1
        except ValueError:
            print("错误：stack 中找不到 'factor'")
            error()
            return
        stack = stack[:index] + ["id"] + stack[index + 1:]
        match(symbol_type_map['id'])
    else:
        error()
        print(f"factor: 未识别的符号 '{current_symbol}'")

def error():
    global error_flag
    if not error_flag:
        error_flag = 1
        print("出错！")

if __name__ == "__main__":
    Read()
    print("-----------Step 1 语法分析--------------")
    stack.append("program")
    program()
    if not error_flag:
        print("递归下降语法分析成功完成。")
    else:
        print("递归下降语法分析失败。")
