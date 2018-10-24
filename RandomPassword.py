import random
from libs.json2gui import *
from libs.Util import TextSection


LOW_LEVEL = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

MEDIUM_LEVEL = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

HIGH_LEVEL = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
              'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
              'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
              'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
              '!', '@', '#', '$', '%', '^', '&', '*', '-', '_', '=',
              '+', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']


# 根据密码长度与复杂度，生成随机密码
def generate_password(length, level):
    return ''.join([random.choice(level) for i in range(0, length)])


# 窗口类
class Window(ttk.Frame):
    def __init__(self, ui_json, master=None):
        super().__init__(master)
        # 从json自动设置UI控件
        create_ui(self, ui_json)
        # 从json自动绑定事件
        create_all_binds(self, ui_json)
        set_combobox_item(self.__dict__["passLevelCombobox"], "中等", True)
        # 设置文本区右键菜单
        self.menu = tk.Menu(self, tearoff=0)
        self.set_text_section()
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

    # 弹出菜单
    def popupmenu(self, event):
        self.menu.post(event.x_root, event.y_root)

    # 设置文本选中时的右键菜单
    def set_text_section(self):
        self.section = TextSection(self, self.__dict__["resultText"])
        self.menu.add_command(label="复制", command=self.section.on_copy)
        self.menu.add_separator()
        self.menu.add_command(label="粘贴", command=self.section.on_paste)
        self.menu.add_separator()
        self.menu.add_command(label="剪切", command=self.section.on_cut)
        self.__dict__["resultText"].bind("<Button-3>", self.popupmenu)

    def generate_password_button_callback(self, event=None):
        length = int(self.__dict__["pass_length"].get())
        level = MEDIUM_LEVEL
        level_text = self.__dict__["pass_level"].get()

        if level_text == "简单":
            level = LOW_LEVEL
        elif level_text == "复杂":
            level = HIGH_LEVEL

        password = generate_password(length, level)
        self.__dict__["resultText"].insert('end', password)
        self.__dict__["resultText"].insert('end', "\n")


if __name__ == '__main__':
    app = Window("RandomPasswordUI.json")
    # 设置窗口标题:
    app.master.title("随机密码生成器")
    app.master.minsize(600, 30)
    # 主消息循环:
    app.mainloop()