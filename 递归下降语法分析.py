# 递归下降分析器实现
# 作者：张奇
# 日期：2024-12-05

import sys


class RecursiveDescentParser:
    def __init__(self):
        # 词法表及相关变量
        self.filename = ""
        self.vt_table = []
        self.read_vt_index = 0
        self.error_flag = False
        self.step = 1
        self.stack = []
        self.method = ""

        # 定义词法类型映射
        self.symbol_type_map = {
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
            '<': '33',
            '>': '34',
            '+': '22',
            '-': '23',
            '*': '24',
            '/': '25',
            'while': '3',
            'if': '4',
            'else': '5',
            'do': '6',
            'break': '7',
            'int': '8',
            'EOF': '0'
        }

    def run(self):
        """主函数，启动语法分析过程"""
        self.read_tokens()
        print("-----------Step 1 语法分析--------------")
        self.stack.append("program")
        self.program()
        if not self.error_flag:
            print("递归下降语法分析成功完成。")
        else:
            print("递归下降语法分析失败。")

    def read_tokens(self):
        """读取词法表文件，并存储在vt_table中"""
        self.filename = input("请输入文件名: ")
        try:
            with open(f"{self.filename}.txt", encoding='utf-8') as file:
                for line in file:
                    tokens = line.strip().split(',')
                    if len(tokens) >= 2:
                        self.vt_table.append(tokens[:2])
            # 添加EOF标记
            if self.vt_table[-1][1] != 'EOF':
                self.vt_table.append(['0', 'EOF'])
            print("\n词法表读取成功，内容如下：")
            for idx, token in enumerate(self.vt_table):
                print(f"{idx}: {token}")
            print()
        except FileNotFoundError:
            print(f"文件 {self.filename}.txt 未找到。")
            sys.exit(1)
        except Exception as e:
            print(f"读取文件时出错: {e}")
            sys.exit(1)

    def info(self):
        """打印当前分析步骤的信息"""
        print(f'-----Step: {self.step}-----')
        print("识别串：=>", ' '.join(self.stack))
        print(f'动作：{self.method}\n')
        self.step += 1

    def match(self, expected_type):
        """
        匹配当前符号类型是否与预期类型一致。
        如果匹配成功，指针前移；否则，报告错误。
        """
        if self.error_flag:
            return
        if self.read_vt_index >= len(self.vt_table):
            self.error(f"匹配失败：已达到词法表末尾，无法匹配 {expected_type}")
            return

        current_type, current_symbol = self.vt_table[self.read_vt_index]
        print(
            f"匹配: 需要的类型 '{expected_type}'，当前类型 '{current_type}'（符号 '{current_symbol}'，索引 {self.read_vt_index}）")

        if isinstance(expected_type, list):
            if current_type not in expected_type:
                self.error(f'当前类型 "{current_type}" 与需要的类型 "{expected_type}" 不匹配')
                return
        else:
            if expected_type != current_type:
                self.error(f'当前类型 "{current_type}" 与需要的类型 "{expected_type}" 不匹配')
                return
        self.read_vt_index += 1

    def error(self, message="出错！"):
        """设置错误标志并打印错误信息"""
        if not self.error_flag:
            self.error_flag = True
            print(message)

    def replace_stack(self, target, replacements):
        """
        在栈中找到目标元素并用替换列表替换。
        如果未找到目标元素，报告错误。
        """
        try:
            index = len(self.stack) - self.stack[::-1].index(target) - 1
            self.stack = self.stack[:index] + replacements + self.stack[index + 1:]
        except ValueError:
            self.error(f"错误：stack 中找不到 '{target}'")

    def program(self):
        """解析程序入口"""
        if self.error_flag:
            return
        self.method = "program\t-->\tblock"
        self.info()
        self.replace_stack("program", ["block"])
        self.block()

    def block(self):
        """解析代码块"""
        if self.error_flag:
            return
        self.method = "block\t-->\t{ stmts }"
        self.info()
        self.replace_stack("block", ["{", "stmts", "}"])
        self.match(self.symbol_type_map['{'])
        self.stmts()
        self.match(self.symbol_type_map['}'])

    def stmts(self):
        """解析语句序列"""
        if self.error_flag:
            return
        if self.read_vt_index >= len(self.vt_table):
            self.error("错误：stmts 中读取超出范围")
            return

        current_type = self.vt_table[self.read_vt_index][0]

        if current_type in [self.symbol_type_map['EOF'], self.symbol_type_map['}']]:
            self.method = "stmts\t-->\tnull"
            self.info()
            self.replace_stack("stmts", [])
            return
        elif current_type == self.symbol_type_map['int']:
            self.method = "stmts\t-->\tdecl stmts"
            self.info()
            self.replace_stack("stmts", ["decl", "stmts"])
            self.decl()
            self.stmts()
        else:
            self.method = "stmts\t-->\tstmt stmts"
            self.info()
            self.replace_stack("stmts", ["stmt", "stmts"])
            self.stmt()
            self.stmts()

    def stmt(self):
        """解析单个语句"""
        if self.error_flag:
            return
        if self.read_vt_index >= len(self.vt_table):
            self.error("错误：stmt 中读取超出范围")
            return

        current_type, current_symbol = self.vt_table[self.read_vt_index]

        if current_type == self.symbol_type_map['id']:
            # 处理赋值语句：id = expr ;
            self.method = "stmt\t-->\tid = expr ;"
            self.info()
            self.replace_stack("stmt", ["id", "=", "expr", ";"])
            self.match(self.symbol_type_map['id'])
            self.match(self.symbol_type_map['='])
            self.expr()
            self.match(self.symbol_type_map[';'])
        elif current_symbol == "while":
            # 处理while循环：while ( boolean ) stmt
            self.method = "stmt\t-->\twhile ( boolean ) stmt"
            self.info()
            self.replace_stack("stmt", ["while", "(", "boolean", ")", "stmt"])
            self.match(self.symbol_type_map['while'])
            self.match(self.symbol_type_map['('])
            self.boolean()
            self.match(self.symbol_type_map[')'])
            self.stmt()
        elif current_symbol == "if":
            # 处理if语句：if ( boolean ) stmt [else stmt]
            self.method = "stmt\t-->\tif ( boolean ) stmt [else stmt]"
            self.info()
            self.replace_stack("stmt", ["if", "(", "boolean", ")", "stmt"])
            self.match(self.symbol_type_map['if'])
            self.match(self.symbol_type_map['('])
            self.boolean()
            self.match(self.symbol_type_map[')'])
            self.stmt()
            # 检查是否有else
            if (self.read_vt_index < len(self.vt_table) and
                    self.vt_table[self.read_vt_index][1] == "else"):
                self.method = "stmt\t-->\tif ( boolean ) stmt else stmt"
                self.info()
                self.replace_stack("stmt", ["else", "stmt"])
                self.match(self.symbol_type_map['else'])
                self.stmt()
        elif current_symbol == "do":
            # 处理do-while循环：do stmt while ( boolean )
            self.method = "stmt\t-->\tdo stmt while ( boolean )"
            self.info()
            self.replace_stack("stmt", ["do", "stmt", "while", "(", "boolean", ")"])
            self.match(self.symbol_type_map['do'])
            self.stmt()
            self.match(self.symbol_type_map['while'])
            self.match(self.symbol_type_map['('])
            self.boolean()
            self.match(self.symbol_type_map[')'])
        elif current_symbol == "break":
            # 处理break语句：break ;
            self.method = "stmt\t-->\tbreak ;"
            self.info()
            self.replace_stack("stmt", ["break", ";"])
            self.match(self.symbol_type_map['break'])
            self.match(self.symbol_type_map[';'])
        else:
            # 处理块语句
            self.method = "stmt\t-->\tblock"
            self.info()
            self.replace_stack("stmt", ["block"])
            self.block()

    def decl(self):
        """解析变量声明"""
        # decl -> int id [= expr] ;
        self.method = "decl\t-->\tint id [= expr] ;"
        self.info()
        self.replace_stack("decl", ["int", "id", "[= expr]", ";"])
        self.match(self.symbol_type_map['int'])
        self.match(self.symbol_type_map['id'])
        # 检查是否有初始化
        if (self.read_vt_index < len(self.vt_table) and
                self.vt_table[self.read_vt_index][1] == "="):
            self.match(self.symbol_type_map['='])
            self.expr()
        self.match(self.symbol_type_map[';'])

    def boolean(self):
        """解析布尔表达式"""
        # boolean -> expr [comp_op expr]
        self.method = "boolean --> expr [comp_op expr]"
        self.info()
        self.replace_stack("boolean", ["expr"])

        # 处理第一个表达式
        self.expr()

        # 检查是否有比较运算符
        if self.read_vt_index < len(self.vt_table):
            current_symbol = self.vt_table[self.read_vt_index][1]
            if current_symbol in ['<', '<=', '>', '>=']:
                self.method = f"boolean --> expr {current_symbol} expr"
                self.info()
                self.replace_stack("expr", [current_symbol, "expr"])
                self.match(self.symbol_type_map[current_symbol])
                self.expr()

    def expr(self):
        """解析表达式"""
        # expr -> term expr1
        self.method = "expr\t-->\tterm expr1"
        self.info()
        self.replace_stack("expr", ["term", "expr1"])
        self.term()
        self.expr1()

    def expr1(self):
        """解析表达式的递归部分，处理加减运算"""
        if self.error_flag:
            return
        if self.read_vt_index >= len(self.vt_table):
            self.error("错误：expr1 中读取超出范围")
            return

        current_symbol = self.vt_table[self.read_vt_index][1]

        if current_symbol == "+":
            # expr1 -> + term expr1
            self.method = "expr1\t-->\t + term expr1"
            self.info()
            self.replace_stack("expr1", ["+", "term", "expr1"])
            self.match(self.symbol_type_map['+'])
            self.term()
            self.expr1()
        elif current_symbol == "-":
            # expr1 -> - term expr1
            self.method = "expr1\t-->\t - term expr1"
            self.info()
            self.replace_stack("expr1", ["-", "term", "expr1"])
            self.match(self.symbol_type_map['-'])
            self.term()
            self.expr1()
        elif current_symbol in ['<', '<=', '>', '>=']:
            # expr1 -> 比较运算符 term
            self.method = f"expr1\t-->\t {current_symbol} term"
            self.info()
            self.replace_stack("expr1", [current_symbol, "term"])
            self.match(self.symbol_type_map[current_symbol])
            self.term()
        else:
            # expr1 -> null
            self.method = "expr1\t-->\tnull"
            self.info()
            self.replace_stack("expr1", [])

    def term(self):
        """解析项"""
        # term -> factor term1
        self.method = "term\t-->\tfactor term1"
        self.info()
        self.replace_stack("term", ["factor", "term1"])
        self.factor()
        self.term1()

    def term1(self):
        """解析项的递归部分，处理乘除运算"""
        if self.error_flag:
            return
        if self.read_vt_index >= len(self.vt_table):
            self.error("错误：term1 中读取超出范围")
            return

        current_symbol = self.vt_table[self.read_vt_index][1]

        if current_symbol == "*":
            # term1 -> * factor term1
            self.method = "term1\t-->\t * factor term1"
            self.info()
            self.replace_stack("term1", ["*", "factor", "term1"])
            self.match(self.symbol_type_map['*'])
            self.factor()
            self.term1()
        elif current_symbol == "/":
            # term1 -> / factor term1
            self.method = "term1\t-->\t / factor term1"
            self.info()
            self.replace_stack("term1", ["/", "factor", "term1"])
            self.match(self.symbol_type_map['/'])
            self.factor()
            self.term1()
        else:
            # term1 -> null
            self.method = "term1\t-->\tnull"
            self.info()
            self.replace_stack("term1", [])

    def factor(self):
        """解析因子"""
        if self.error_flag:
            return
        if self.read_vt_index >= len(self.vt_table):
            self.error("错误：factor 中读取超出范围")
            return

        current_type, current_symbol = self.vt_table[self.read_vt_index]

        if current_symbol == "(":
            # factor -> ( expr )
            self.method = "factor\t-->\t(expr)"
            self.info()
            self.replace_stack("factor", ["(", "expr", ")"])
            self.match(self.symbol_type_map['('])
            self.expr()
            self.match(self.symbol_type_map[')'])
        elif current_type in self.symbol_type_map['num']:
            # factor -> num
            self.method = "factor\t-->\tnum"
            self.info()
            self.replace_stack("factor", ["num"])
            if current_type in self.symbol_type_map['num']:
                self.match(current_type)
            else:
                self.error(f"factor: 无效的数字类型 '{current_type}'")
        elif current_type == self.symbol_type_map['id']:
            # factor -> id
            self.method = "factor\t-->\tid"
            self.info()
            self.replace_stack("factor", ["id"])
            self.match(self.symbol_type_map['id'])
        else:
            self.error(f"factor: 未识别的符号 '{current_symbol}'")


if __name__ == "__main__":
    parser = RecursiveDescentParser()
    parser.run()
