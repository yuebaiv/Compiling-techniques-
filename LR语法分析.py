# SLR 语法分析器的面向对象实现
# 作者：张奇
# 日期：2024-12-05

class SLRParser:
    def __init__(self):
        # 初始化文件名和各种栈
        self.filename = ""
        self.input_stack = []
        self.symbol_stack = []
        self.state_stack = []
        self.step = 0
        self.method = ""

        # 定义动作表对应的终结符
        # 终结符顺序: id, num, mai, whi, (, ), {, }, +, -, =, <=, ;
        self.action = [0, 42, 43, 5, 3, 31, 32, 28, 29, 22, 23, 26, 41, 30]

        # 定义动作表，行对应状态，列对应终结符
        self.action_table = [["", "", "", "s2", "", "", "", "", "", "", "", "", "", ""],
                ["acc", "", "", "", "", "", "", "", "", "", "", "", "", ""],
                ["", "", "", "", "", "", "", "s4", "", "", "", "", "", ""],
                ["r1", "", "", "", "", "", "", "", "", "", "", "", "", ""],
                ["", "s10", "", "", "s9", "", "", "", "r4", "", "", "", "", ""],
                ["", "", "", "", "", "", "", "", "s6", "", "", "", "", ""],
                ["r2", "r2", "", "", "r2", "", "", "", "r2", "", "", "", "", ""],
                ["", "s10", "", "", "s9", "", "", "", "r4", "", "", "", "", ""],
                ["", "", "", "", "", "", "", "", "r3", "", "", "", "", ""],
                ["", "", "", "", "", "s11", "", "", "", "", "", "", "", ""],
                ["", "", "", "", "", "", "", "", "", "", "", "s12", "", ""],
                ["", "s18", "s19", "", "", "", "", "", "", "", "", "", "", ""],
                ["", "s18", "s19", "", "", "", "", "", "", "", "", "", "", ""],
                ["", "", "", "", "", "", "", "", "", "", "", "", "s14", ""],
                ["", "s18", "s19", "", "", "", "", "", "", "", "", "", "", ""],
                ["", "", "", "", "", "", "s16", "", "", "", "", "", "", ""],
                ["", "", "", "", "", "", "", "s4", "", "", "", "", "", ""],
                ["", "r7", "", "", "r7", "", "", "", "r7", "", "", "", "", ""],
                ["", "r10", "r10", "", "", "", "r10", "", "", "r10", "r10", "", "r10", "r10"],
                ["", "r11", "r11", "", "", "", "r11", "", "", "r11", "r11", "", "r11", "r11"],
                ["", "", "", "", "", "", "", "", "", "s21", "s23", "", "", ""],
                ["", "s18", "s19", "", "", "", "", "", "", "", "", "", "", ""],
                ["", "", "", "", "", "", "r8", "", "", "", "", "", "r8", "r8"],
                ["", "s18", "s19", "", "", "", "", "", "", "", "", "", "", ""],
                ["", "", "", "", "", "", "r9", "", "", "", "", "", "r9", "r9"],
                ["", "", "", "", "", "", "", "", "", "s21", "s23", "", "", "s26"],
                ["", "r6", "", "", "r6", "", "", "", "r6", "", "", "", "", ""],
                ["", "", "", "", "", "", "", "", "", "", "", "", "", "s28"],
                ["", "r5", "", "", "r5", "", "", "", "r5", "", "", "", "", ""]]

        # 定义 goto 表的非终结符
        self.goto = ["prog", "block", "stmts", "stmt", "E", "F"]

        # 定义 goto 表，行对应状态，列对应非终结符
        self.goto_table = [[1, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0],
             [0, 3, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0],
             [0, 0, 5, 7, 0, 0],
             [0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0],
             [0, 0, 8, 7, 0, 0],
             [0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 13, 20],
             [0, 0, 0, 0, 27, 25],
             [0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 15, 20],
             [0, 0, 0, 0, 0, 0],
             [0, 17, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 22],
             [0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 24],
             [0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0]]
        # 定义语法的产生式规则
        self.productions = [["prog", "main", "block"],
            ["block", "{", "stmts", "}"],
            ["stmts", "stmt", "stmts"],
            ["stmts"],
            ["stmt", "id", "=", "E", ";"],
            ["stmt", "id", "=", "F", ";"],
            ["stmt", "while", "(", "E", "<=", "E", ")", "block"],
            ["E", "F", "+", "F"],
            ["E", "F", "-", "F"],
            ["F", "id"],
            ["F", "num"]]

        # 产生式规则的字符串表示，用于显示
        self.production_strings =["prog -> main block",
                   "block -> { stmts }",
                   "stmts -> stmt stmts",
                   "stmts -> @",
                   "stmt -> id = E ;",
                   "stmt -> id = F ;",
                   "stmt -> while ( E <= E ) block",
                   "E -> F + F",
                   "E -> F - F",
                   "F -> id",
                   "F -> num"]



    def read_input(self):
        """
        读取输入文件并填充输入栈。
        文件中的每一行应包含用逗号分隔的标记信息。
        """
        self.filename = input("请输入文件名: ")
        try:
            with open(self.filename + ".txt", 'r', encoding='utf-8') as f:
                for line in f:
                    # 将每行按逗号分割，并取前两个元素作为标记
                    token = line.strip().split(',')[:2]
                    self.input_stack.append(token)
        except FileNotFoundError:
            print(f"文件 {self.filename}.txt 未找到。")
            exit(1)

    def display_info(self):
        """
        显示解析器当前的状态，包括栈和动作。
        """
        print(f'-----步骤: {self.step}-----')
        # 显示状态栈
        print("状态栈：", end='')
        for state in self.state_stack:
            print(state, end=' ')
        print()
        # 显示符号栈
        print("符号栈：", end='')
        for symbol in self.symbol_stack:
            print(symbol, end=' ')
        print()
        # 显示输入栈
        print("输入串：", end='')
        for token in self.input_stack:
            print(token[1], end=' ')
        print()
        # 显示当前动作
        print(f'动作：{self.method}')
        print()
        self.step += 1

    def analyze(self):
        """
        执行 SLR 语法分析算法。
        返回 True 表示输入字符串成功解析，否则返回 False。
        """
        # 初始化栈
        self.step = 1
        self.state_stack = [0]  # 状态栈初始化为状态0
        self.symbol_stack = ["#"]  # 符号栈初始化为结束符
        self.input_stack.append(["0", "#"])  # 在输入栈末尾添加结束符
        self.method = ""

        while True:
            current_state = self.state_stack[-1]
            # 获取当前输入标记的动作索引
            try:
                action_idx = self.action.index(int(self.input_stack[0][0]))
            except ValueError:
                # 如果标记的动作索引未找到，则为错误
                self.method = "错误：无效的标记。"
                self.display_info()
                return False

            # 从动作表中获取对应的动作
            action_entry = self.action_table[current_state][action_idx]

            if action_entry == "":
                # 找不到有效动作，解析错误
                self.method = "错误：无效的动作。"
                self.display_info()
                return False
            elif action_entry.startswith("s"):
                # 移进动作
                try:
                    next_state = int(action_entry[1:])
                except ValueError:
                    self.method = "错误：无效的移进状态。"
                    self.display_info()
                    return False
                self.method = f"{action_entry} 移进 {self.input_stack[0][1]}，状态转到 {next_state}"
                self.display_info()
                # 将状态和符号推入对应的栈
                self.state_stack.append(next_state)
                self.symbol_stack.append(self.input_stack[0][1])
                # 移除输入栈中的标记
                self.input_stack.pop(0)
            elif action_entry.startswith("r"):
                # 归约动作
                try:
                    production_number = int(action_entry[1:])
                except ValueError:
                    self.method = "错误：无效的归约动作。"
                    self.display_info()
                    return False
                if production_number < 1 or production_number > len(self.productions):
                    self.method = "错误：归约动作对应的产生式编号超出范围。"
                    self.display_info()
                    return False
                production = self.productions[production_number - 1]
                production_str = self.production_strings[production_number - 1]
                self.method = f"{action_entry} 用第 {production_number} 个产生式 {production_str} 进行归约"
                self.display_info()
                # 计算右部长度，弹出相应数量的符号和状态
                rhs_length = len(production) - 1
                for _ in range(rhs_length):
                    if self.state_stack:
                        self.state_stack.pop()
                    if self.symbol_stack:
                        self.symbol_stack.pop()
                # 将左部非终结符压入符号栈
                lhs = production[0]
                self.symbol_stack.append(lhs)
                # 从 goto 表中获取下一个状态
                current_state = self.state_stack[-1]
                try:
                    goto_index = self.goto.index(lhs)
                except ValueError:
                    self.method = "错误：goto 表中找不到对应的非终结符。"
                    self.display_info()
                    return False
                next_state = self.goto_table[current_state][goto_index]
                if next_state == 0:
                    # 无效的 goto 状态
                    self.method = "错误：无效的 goto 状态。"
                    self.display_info()
                    return False
                self.state_stack.append(next_state)
            elif action_entry == "acc":
                # 接受动作
                self.method = "接受！"
                self.display_info()
                return True
            else:
                # 未定义的动作
                self.method = "错误：未定义的动作。"
                self.display_info()
                return False

    def run(self):
        """
        执行解析器，通过读取输入并进行分析。
        """
        self.read_input()
        print("-----------步骤 1 语法分析--------------")
        if self.analyze():
            print("成功！该语句有效，所用产生式如上。")
        else:
            print("错误！")
        print("SLR 语法分析结束。")


if __name__ == "__main__":
    parser = SLRParser()
    parser.run()
