# 词法分析器实现
# 作者：张奇
# 日期：2024-12-5

# 定义关键字列表
keywords = [
    "if", "else", "while", "do", "main", "int", "float", "double", "return",
    "const", "void", "continue", "break", "char", "unsigned", "enum",
    "long", "switch", "case", "auto", "static"
]

# 符号表（符号编号, 符号描述）
symbol_table = {
    22: '+', 23: '-', 42: 'id', 43: '整型', 44: '浮点型', 45: '二进制',
    46: '八进制', 47: '十六进制', 48: '字符串常量', 26: '=', 27: '<',
    28: '{', 29: '}', 30: ';', 31: '(', 32: ')', 33: "'", 34: '"',
    35: '==', 36: '!=', 37: '&&', 38: '||', 39: '>', 40: '>=',
    41: '<=', -1: '错误', -2: '未知符号', -3: '数字书写不规范',
    -4: '变量不是int类型', -5: '变量不是float类型', -6: '变量不是char类型'
}

# 初始化全局变量
source_code = ""       # 存储去除注释后的源代码
tokens = []            # 存储词法分析结果的列表
filename = ""          # 源代码文件名

# 清除注释的函数
def remove_comments():
    global source_code, filename
    filename = input("请输入文件名: ")
    with open(filename + ".txt", 'r', encoding='utf-8') as file:
        state = 0  # 状态变量，用于跟踪当前解析状态
        for line in file:
            for char in line:
                if state == 0:
                    if char == '/':
                        state = 1
                        continue
                    else:
                        source_code += char
                elif state == 1:
                    if char == '*':
                        state = 2
                    elif char == '/':
                        state = 4
                    else:
                        state = 0
                        source_code += '/'
                        source_code += char
                elif state == 2:
                    if char == '*':
                        state = 3
                elif state == 3:
                    if char == '/':
                        state = 0
                    elif char == '*':
                        state = 3
                    else:
                        state = 2
                elif state == 4:
                    if char == '\n':
                        state = 0
                        source_code += char
        # 处理文件结束时仍在注释状态的情况
        if state in [1, 2, 3, 4]:
            print("警告: 注释未正确关闭")
    
    # 去除主程序前的空行
    source_code = source_code.lstrip('\n')
    
    # 去除主程序中的多余空行和前导空格
    cleaned_code = []
    for line in source_code.split('\n'):
        stripped_line = line.strip()
        if stripped_line:
            cleaned_code.append(stripped_line)
    source_code = '\n'.join(cleaned_code)
    
    # 打印带行号的源代码
    print("----------- 清除注释后的源代码 --------------")
    for idx, line in enumerate(source_code.split('\n'), start=1):
        print(f"{idx}\t{line}")
    print('\n')

# 获取下一个记号的函数
def get_token():
    global source_code, tokens, current_pos, is_in_string, token_buffer, symbol, line, column
    token_buffer = ""
    
    # 处理字符串常量
    if not is_in_string and source_code[current_pos - 1] == '\"':
        is_in_string = True
        symbol = 48  # 字符串常量
        while current_pos < len(source_code):
            char = source_code[current_pos]
            token_buffer += char
            current_pos += 1
            if char == '\"':
                is_in_string = False
                break
        return
    
    # 跳过空白字符
    while current_pos < len(source_code) and source_code[current_pos] in [' ', '\t']:
        current_pos += 1
        column += 1
    
    # 处理换行符
    if current_pos < len(source_code) and source_code[current_pos] == '\n':
        line += 1
        column = 1
        current_pos += 1
    
    if current_pos >= len(source_code):
        return
    
    char = source_code[current_pos]
    
    # 处理标识符和关键字
    if char.isalpha() or char == '_':
        symbol = 42  # id
        while current_pos < len(source_code) and (source_code[current_pos].isalnum() or source_code[current_pos] == '_'):
            token_buffer += source_code[current_pos]
            current_pos += 1
            column += 1
        if token_buffer in keywords:
            symbol = keywords.index(token_buffer) + 1
        return
    
    # 处理数字
    if char.isdigit():
        token_buffer += char
        current_pos += 1
        column += 1
        if char == '0' and current_pos < len(source_code):
            next_char = source_code[current_pos].lower()
            if next_char == 'b':
                symbol = 45  # 二进制
                token_buffer += next_char
                current_pos += 1
                column += 1
                while current_pos < len(source_code) and source_code[current_pos] in ['0', '1']:
                    token_buffer += source_code[current_pos]
                    current_pos += 1
                    column += 1
            elif next_char == 'o':
                symbol = 46  # 八进制
                token_buffer += next_char
                current_pos += 1
                column += 1
                while current_pos < len(source_code) and source_code[current_pos] in '01234567':
                    token_buffer += source_code[current_pos]
                    current_pos += 1
                    column += 1
            elif next_char == 'x':
                symbol = 47  # 十六进制
                token_buffer += next_char
                current_pos += 1
                column += 1
                while current_pos < len(source_code) and (source_code[current_pos].isdigit() or source_code[current_pos].lower() in 'abcdef'):
                    token_buffer += source_code[current_pos]
                    current_pos += 1
                    column += 1
            elif next_char == '.':
                symbol = 44  # 浮点型
                token_buffer += next_char
                current_pos += 1
                column += 1
                while current_pos < len(source_code) and source_code[current_pos].isdigit():
                    token_buffer += source_code[current_pos]
                    current_pos += 1
                    column += 1
            else:
                symbol = 43  # 整型
        else:
            while current_pos < len(source_code) and source_code[current_pos].isdigit():
                token_buffer += source_code[current_pos]
                current_pos += 1
                column += 1
            if current_pos < len(source_code) and source_code[current_pos] == '.':
                symbol = 44  # 浮点型
                token_buffer += '.'
                current_pos += 1
                column += 1
                while current_pos < len(source_code) and source_code[current_pos].isdigit():
                    token_buffer += source_code[current_pos]
                    current_pos += 1
                    column += 1
            else:
                symbol = 43  # 整型
        return
    
    # 处理其他符号
    if char in ['+', '-', '*', '/', '=', '<', '>', '{', '}', ';', '(', ')', '\'', '\"', '!', '&', '|']:
        if char == '+':
            symbol = 22
            token_buffer = '+'
            current_pos += 1
            column += 1
        elif char == '-':
            symbol = 23
            token_buffer = '-'
            current_pos += 1
            column += 1
        elif char == '*':
            symbol = 24
            token_buffer = '*'
            current_pos += 1
            column += 1
        elif char == '/':
            symbol = 25
            token_buffer = '/'
            current_pos += 1
            column += 1
        elif char == '=':
            current_pos += 1
            column += 1
            if current_pos < len(source_code) and source_code[current_pos] == '=':
                symbol = 35  # ==
                token_buffer = '=='
                current_pos += 1
                column += 1
            else:
                symbol = 26  # =
                token_buffer = '='
        elif char == '<':
            current_pos += 1
            column += 1
            if current_pos < len(source_code) and source_code[current_pos] == '=':
                symbol = 41  # <=
                token_buffer = '<='
                current_pos += 1
                column += 1
            else:
                symbol = 27  # <
                token_buffer = '<'
        elif char == '>':
            current_pos += 1
            column += 1
            if current_pos < len(source_code) and source_code[current_pos] == '=':
                symbol = 40  # >=
                token_buffer = '>='
                current_pos += 1
                column += 1
            else:
                symbol = 39  # >
                token_buffer = '>'
        elif char == '{':
            symbol = 28
            token_buffer = '{'
            current_pos += 1
            column += 1
        elif char == '}':
            symbol = 29
            token_buffer = '}'
            current_pos += 1
            column += 1
        elif char == ';':
            symbol = 30
            token_buffer = ';'
            current_pos += 1
            column += 1
        elif char == '(':
            symbol = 31
            token_buffer = '('
            current_pos += 1
            column += 1
        elif char == ')':
            symbol = 32
            token_buffer = ')'
            current_pos += 1
            column += 1
        elif char == '\'':
            symbol = 33
            token_buffer = '\''
            current_pos += 1
            column += 1
        elif char == '\"':
            symbol = 34
            token_buffer = '\"'
            current_pos += 1
            column += 1
        elif char == '!':
            current_pos += 1
            column += 1
            if current_pos < len(source_code) and source_code[current_pos] == '=':
                symbol = 36  # !=
                token_buffer = '!='
                current_pos += 1
                column += 1
            else:
                symbol = -2  # 未知符号
        elif char == '&':
            current_pos += 1
            column += 1
            if current_pos < len(source_code) and source_code[current_pos] == '&':
                symbol = 37  # &&
                token_buffer = '&&'
                current_pos += 1
                column += 1
            else:
                symbol = -2  # 未知符号
        elif char == '|':
            current_pos += 1
            column += 1
            if current_pos < len(source_code) and source_code[current_pos] == '|':
                symbol = 38  # ||
                token_buffer = '||'
                current_pos += 1
                column += 1
            else:
                symbol = -2  # 未知符号
        return
    
    # 处理未知符号
    symbol = -2  # 未知符号
    token_buffer = char
    current_pos += 1
    column += 1
    return

# 主程序
if __name__ == "__main__":
    print("----------- Step 1: 删除注释 --------------")
    remove_comments()
    
    print("----------- Step 2: 词法分析 --------------")
    line = 1          # 当前行号
    column = 1        # 当前列号
    is_in_string = False  # 是否在字符串中
    current_pos = 0   # 当前解析位置
    
    while current_pos < len(source_code):
        token_buffer = ""
        symbol = 0
        get_token()
        
        # 错误检测
        if len(tokens) > 0:
            last_symbol = tokens[-1][0]
            if last_symbol in [6, 7, 8, 11, 14, 15, 16, 17]:
                if symbol == 43:
                    print(f"错误: 变量名不能以数字开头 at line {line}, column {column}")
                    symbol = -1
                elif symbol not in [5, 42]:
                    print(f"错误: 缺少变量名 at line {line}, column {column}")
                    symbol = -2
            elif last_symbol in [43, 44, 45, 46, 47]:
                if symbol in [42, 43, 44, 45, 46, 47]:
                    print(f"错误: 数字书写不规范 at line {line}, column {column}")
                    symbol = -3
        if len(tokens) > 2:
            third_last_symbol = tokens[-3][0]
            if third_last_symbol == 6:  # int
                if symbol not in [32, 43, 45, 46, 47]:
                    print(f"错误: 变量不是int类型 at line {line}, column {column}")
                    symbol = -4
            elif third_last_symbol in [7, 8]:  # float, double
                if symbol != 44:
                    print(f"错误: 变量不是float类型 at line {line}, column {column}")
                    symbol = -5
        if len(tokens) > 3:
            fourth_last_symbol = tokens[-4][0]
            if fourth_last_symbol == 14:  # char
                if symbol != 48:
                    print(f"错误: 变量不是char类型 at line {line}, column {column}")
                    symbol = -6
        
        # 打印记号
        print(f'({symbol:>2},{token_buffer:^8})\tline:{line}, column:{column}')
        tokens.append([symbol, token_buffer, line, column])
        column += len(token_buffer)
    
    # 检查引号和括号是否匹配
    token_strings = [token[1] for token in tokens]
    if token_strings.count('\'') % 2 == 1:
        print("错误: 单引号数量不匹配")
    if token_strings.count('\"') % 2 == 1:
        print("错误: 双引号数量不匹配")
    if token_strings.count('(') != token_strings.count(')'):
        print("错误: 小括号数量不匹配")
    if token_strings.count('{') != token_strings.count('}'):
        print("错误: 大括号数量不匹配")
    
    # 将词法分析结果写入文件
    output_filename = filename + "-out.txt"
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        for token in tokens:
            outfile.write(','.join(map(str, token)) + '\n')
    print(f"词法分析结束，结果已存入文件 {output_filename}")
