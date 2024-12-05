# 词法分析器实现
# 作者：张奇
# 日期：2024-12-05

import sys


class LexicalAnalyzer:
    def __init__(self):
        # 定义关键字列表
        self.keywords = [
            "if", "else", "while", "do", "main", "int", "float", "double", "return",
            "const", "void", "continue", "break", "char", "unsigned", "enum",
            "long", "switch", "case", "auto", "static"
        ]

        # 符号表（符号编号, 符号描述）
        self.symbol_table = {
            22: '+', 23: '-', 42: 'id', 43: '整型', 44: '浮点型', 45: '二进制',
            46: '八进制', 47: '十六进制', 48: '字符串常量', 26: '=', 27: '<',
            28: '{', 29: '}', 30: ';', 31: '(', 32: ')', 33: "'", 34: '"',
            35: '==', 36: '!=', 37: '&&', 38: '||', 39: '>', 40: '>=',
            41: '<=', -1: '错误', -2: '未知符号', -3: '数字书写不规范',
            -4: '变量不是int类型', -5: '变量不是float类型', -6: '变量不是char类型'
        }

        # 初始化全局变量
        self.source_code = ""  # 存储去除注释后的源代码
        self.tokens = []  # 存储词法分析结果的列表
        self.filename = ""  # 源代码文件名

        # 词法分析状态变量
        self.line = 1
        self.column = 1
        self.current_pos = 0
        self.is_in_string = False

    def run(self):
        """主函数，启动词法分析过程"""
        self.remove_comments()
        print("----------- Step 2: 词法分析 --------------")
        self.lexical_analysis()
        self.check_balances()
        self.write_tokens_to_file()
        print(f"词法分析结束，结果已存入文件 {self.filename}-out.txt")

    def remove_comments(self):
        """清除源代码中的注释，并存储在self.source_code中"""
        self.filename = input("请输入文件名: ")
        try:
            with open(f"{self.filename}.txt", 'r', encoding='utf-8') as file:
                state = 0  # 状态变量，用于跟踪当前解析状态
                for line in file:
                    for char in line:
                        if state == 0:
                            if char == '/':
                                state = 1
                                continue
                            else:
                                self.source_code += char
                        elif state == 1:
                            if char == '*':
                                state = 2
                            elif char == '/':
                                state = 4
                            else:
                                state = 0
                                self.source_code += '/'
                                self.source_code += char
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
                                self.source_code += char
                # 处理文件结束时仍在注释状态的情况
                if state in [1, 2, 3, 4]:
                    print("警告: 注释未正确关闭")
        except FileNotFoundError:
            print(f"文件 {self.filename}.txt 未找到。")
            sys.exit(1)
        except Exception as e:
            print(f"读取文件时出错: {e}")
            sys.exit(1)

        # 去除主程序前的空行
        self.source_code = self.source_code.lstrip('\n')

        # 去除主程序中的多余空行和前导空格
        cleaned_code = []
        for line in self.source_code.split('\n'):
            stripped_line = line.strip()
            if stripped_line:
                cleaned_code.append(stripped_line)
        self.source_code = '\n'.join(cleaned_code)

        # 打印带行号的源代码
        print("----------- 清除注释后的源代码 --------------")
        for idx, line in enumerate(self.source_code.split('\n'), start=1):
            print(f"{idx}\t{line}")
        print('\n')

    def lexical_analysis(self):
        """执行词法分析，将源代码转换为记号列表"""
        while self.current_pos < len(self.source_code):
            token_buffer = ""
            symbol = 0
            self.get_token()

            # 错误检测
            self.detect_errors()

            # 打印记号，保持原始输出格式
            if len(self.tokens) > 0:
                last_token = self.tokens[-1]
                symbol = last_token[0]
                token_buffer = last_token[1]
            print(f'({symbol:>2},{token_buffer:^8})\tline:{self.line}, column:{self.column}')
            self.column += len(token_buffer)

    def get_token(self):
        """获取下一个记号，并更新symbol和token_buffer"""
        token_buffer = ""
        symbol = 0

        # 处理字符串常量
        if self.is_in_string:
            symbol = 48  # 字符串常量
            while self.current_pos < len(self.source_code):
                char = self.source_code[self.current_pos]
                token_buffer += char
                self.current_pos += 1
                self.column += 1
                if char == '\"':
                    self.is_in_string = False
                    break
            self.tokens.append([symbol, token_buffer, self.line, self.column])
            return

        # 跳过空白字符
        while self.current_pos < len(self.source_code) and self.source_code[self.current_pos] in [' ', '\t']:
            self.current_pos += 1
            self.column += 1

        # 处理换行符
        if self.current_pos < len(self.source_code) and self.source_code[self.current_pos] == '\n':
            self.line += 1
            self.column = 1
            self.current_pos += 1

        if self.current_pos >= len(self.source_code):
            return

        char = self.source_code[self.current_pos]

        # 处理标识符和关键字
        if char.isalpha() or char == '_':
            symbol = 42  # id
            while self.current_pos < len(self.source_code) and (
                    self.source_code[self.current_pos].isalnum() or self.source_code[self.current_pos] == '_'):
                token_buffer += self.source_code[self.current_pos]
                self.current_pos += 1
                self.column += 1
            if token_buffer in self.keywords:
                symbol = self.keywords.index(token_buffer) + 1
            self.tokens.append([symbol, token_buffer, self.line, self.column])
            return

        # 处理数字
        if char.isdigit():
            token_buffer += char
            self.current_pos += 1
            self.column += 1
            if char == '0' and self.current_pos < len(self.source_code):
                next_char = self.source_code[self.current_pos].lower()
                if next_char == 'b':
                    symbol = 45  # 二进制
                    token_buffer += next_char
                    self.current_pos += 1
                    self.column += 1
                    while self.current_pos < len(self.source_code) and self.source_code[self.current_pos] in ['0', '1']:
                        token_buffer += self.source_code[self.current_pos]
                        self.current_pos += 1
                        self.column += 1
                elif next_char == 'o':
                    symbol = 46  # 八进制
                    token_buffer += next_char
                    self.current_pos += 1
                    self.column += 1
                    while self.current_pos < len(self.source_code) and self.source_code[self.current_pos] in '01234567':
                        token_buffer += self.source_code[self.current_pos]
                        self.current_pos += 1
                        self.column += 1
                elif next_char == 'x':
                    symbol = 47  # 十六进制
                    token_buffer += next_char
                    self.current_pos += 1
                    self.column += 1
                    while self.current_pos < len(self.source_code) and (
                            self.source_code[self.current_pos].isdigit() or self.source_code[
                        self.current_pos].lower() in 'abcdef'):
                        token_buffer += self.source_code[self.current_pos]
                        self.current_pos += 1
                        self.column += 1
                elif next_char == '.':
                    symbol = 44  # 浮点型
                    token_buffer += next_char
                    self.current_pos += 1
                    self.column += 1
                    while self.current_pos < len(self.source_code) and self.source_code[self.current_pos].isdigit():
                        token_buffer += self.source_code[self.current_pos]
                        self.current_pos += 1
                        self.column += 1
                else:
                    symbol = 43  # 整型
            else:
                while self.current_pos < len(self.source_code) and self.source_code[self.current_pos].isdigit():
                    token_buffer += self.source_code[self.current_pos]
                    self.current_pos += 1
                    self.column += 1
                if self.current_pos < len(self.source_code) and self.source_code[self.current_pos] == '.':
                    symbol = 44  # 浮点型
                    token_buffer += '.'
                    self.current_pos += 1
                    self.column += 1
                    while self.current_pos < len(self.source_code) and self.source_code[self.current_pos].isdigit():
                        token_buffer += self.source_code[self.current_pos]
                        self.current_pos += 1
                        self.column += 1
                else:
                    symbol = 43  # 整型
            self.tokens.append([symbol, token_buffer, self.line, self.column])
            return

        # 处理其他符号
        if char in ['+', '-', '*', '/', '=', '<', '>', '{', '}', ';', '(', ')', '\'', '\"', '!', '&', '|']:
            token_buffer = char
            self.current_pos += 1
            self.column += 1
            if char == '+':
                symbol = 22
            elif char == '-':
                symbol = 23
            elif char == '*':
                symbol = 24
            elif char == '/':
                symbol = 25
            elif char == '=':
                if self.current_pos < len(self.source_code) and self.source_code[self.current_pos] == '=':
                    symbol = 35  # ==
                    token_buffer += '='
                    self.current_pos += 1
                    self.column += 1
                else:
                    symbol = 26  # =
            elif char == '<':
                if self.current_pos < len(self.source_code) and self.source_code[self.current_pos] == '=':
                    symbol = 41  # <=
                    token_buffer += '='
                    self.current_pos += 1
                    self.column += 1
                else:
                    symbol = 27  # <
            elif char == '>':
                if self.current_pos < len(self.source_code) and self.source_code[self.current_pos] == '=':
                    symbol = 40  # >=
                    token_buffer += '='
                    self.current_pos += 1
                    self.column += 1
                else:
                    symbol = 39  # >
            elif char == '{':
                symbol = 28
            elif char == '}':
                symbol = 29
            elif char == ';':
                symbol = 30
            elif char == '(':
                symbol = 31
            elif char == ')':
                symbol = 32
            elif char == '\'':
                symbol = 33
            elif char == '\"':
                symbol = 34
                self.is_in_string = True
            elif char == '!':
                if self.current_pos < len(self.source_code) and self.source_code[self.current_pos] == '=':
                    symbol = 36  # !=
                    token_buffer += '='
                    self.current_pos += 1
                    self.column += 1
                else:
                    symbol = -2  # 未知符号
            elif char == '&':
                if self.current_pos < len(self.source_code) and self.source_code[self.current_pos] == '&':
                    symbol = 37  # &&
                    token_buffer += '&'
                    self.current_pos += 1
                    self.column += 1
                else:
                    symbol = -2  # 未知符号
            elif char == '|':
                if self.current_pos < len(self.source_code) and self.source_code[self.current_pos] == '|':
                    symbol = 38  # ||
                    token_buffer += '|'
                    self.current_pos += 1
                    self.column += 1
                else:
                    symbol = -2  # 未知符号
            self.tokens.append([symbol, token_buffer, self.line, self.column])
            return

        # 处理未知符号
        symbol = -2  # 未知符号
        token_buffer = char
        self.current_pos += 1
        self.column += 1
        self.tokens.append([symbol, token_buffer, self.line, self.column])
        return

    def detect_errors(self):
        """检测词法分析中的错误，并进行相应处理"""
        if not self.tokens:
            return

        last_symbol = self.tokens[-1][0]
        symbol = self.tokens[-1][0]
        token_buffer = self.tokens[-1][1]

        # 错误检测逻辑
        if len(self.tokens) > 0:
            last_symbol = self.tokens[-1][0]
            if last_symbol in [6, 7, 8, 11, 14, 15, 16, 17]:
                if symbol == 43:
                    print(f"错误: 变量名不能以数字开头 at line {self.line}, column {self.column}")
                    self.tokens[-1][0] = -1
                elif symbol not in [5, 42]:
                    print(f"错误: 缺少变量名 at line {self.line}, column {self.column}")
                    self.tokens[-1][0] = -2

        if len(self.tokens) > 2:
            third_last_symbol = self.tokens[-3][0]
            if third_last_symbol == 6:  # int
                if symbol not in [32, 43, 45, 46, 47]:
                    print(f"错误: 变量不是int类型 at line {self.line}, column {self.column}")
                    self.tokens[-1][0] = -4
            elif third_last_symbol in [7, 8]:  # float, double
                if symbol != 44:
                    print(f"错误: 变量不是float类型 at line {self.line}, column {self.column}")
                    self.tokens[-1][0] = -5

        if len(self.tokens) > 3:
            fourth_last_symbol = self.tokens[-4][0]
            if fourth_last_symbol == 14:  # char
                if symbol != 48:
                    print(f"错误: 变量不是char类型 at line {self.line}, column {self.column}")
                    self.tokens[-1][0] = -6

    def check_balances(self):
        """检查引号和括号是否匹配"""
        token_strings = [token[1] for token in self.tokens]
        if token_strings.count('\'') % 2 == 1:
            print("错误: 单引号数量不匹配")
        if token_strings.count('\"') % 2 == 1:
            print("错误: 双引号数量不匹配")
        if token_strings.count('(') != token_strings.count(')'):
            print("错误: 小括号数量不匹配")
        if token_strings.count('{') != token_strings.count('}'):
            print("错误: 大括号数量不匹配")

    def write_tokens_to_file(self):
        """将词法分析结果写入输出文件，保持原始格式"""
        output_filename = f"{self.filename}-out.txt"
        try:
            with open(output_filename, 'w', encoding='utf-8') as outfile:
                for token in self.tokens:
                    outfile.write(','.join(map(str, token)) + '\n')
        except Exception as e:
            print(f"写入文件时出错: {e}")
            sys.exit(1)


if __name__ == "__main__":
    analyzer = LexicalAnalyzer()
    print("----------- Step 1: 删除注释 --------------")
    analyzer.remove_comments()

    print("----------- Step 2: 词法分析 --------------")
    analyzer.lexical_analysis()

    print("----------- Step 3: 检查平衡符号 --------------")
    analyzer.check_balances()

    analyzer.write_tokens_to_file()
    print(f"词法分析结束，结果已存入文件 {analyzer.filename}-out.txt")
