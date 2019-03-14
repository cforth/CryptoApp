import tkinter as tk
import tkinter.ttk as ttk
from libs.Util import TextSection


# 窗口类
class CFText(ttk.Frame):
    def __init__(self, master=None, title="", width=60, height=20):
        super().__init__(master, padding=2)
        self.width = width
        self.height = height
        self.title_label = ttk.Label(self, text=title)
        self.text_widget = tk.Text(self, width=self.width, height=self.height, wrap="none")
        self.ysb = tk.Scrollbar(self, orient='vertical', command=self.text_widget.yview)
        self.xsb = tk.Scrollbar(self, orient='horizontal', command=self.text_widget.xview)
        self.text_widget['xscrollcommand'] = self.xsb.set
        self.text_widget['yscrollcommand'] = self.ysb.set
        # 设置文本区右键菜单
        self.menu = tk.Menu(self, tearoff=0)
        self.set_text_section()
        # 布局
        self.title_label.grid(row=0, column=0, sticky=tk.E + tk.W)
        self.text_widget.grid(row=1, column=0, sticky=tk.N + tk.S + tk.E + tk.W)
        self.ysb.grid(row=1, column=1, sticky=tk.N + tk.S)
        self.xsb.grid(row=2, column=0, sticky=tk.E + tk.W)
        self.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    # 弹出菜单
    def popupmenu(self, event):
        self.menu.post(event.x_root, event.y_root)

    # 设置文本选中时的右键菜单
    def set_text_section(self):
        self.section = TextSection(self, self.text_widget)
        self.menu.add_command(label="复制", command=self.section.on_copy)
        self.menu.add_separator()
        self.menu.add_command(label="粘贴", command=self.section.on_paste)
        self.menu.add_separator()
        self.menu.add_command(label="剪切", command=self.section.on_cut)
        self.text_widget.bind("<Button-3>", self.popupmenu)

    # 显示指定的文本
    def show(self, string):
        self.text_widget.insert('end', string)


if __name__ == '__main__':
    app = CFText(title="test_title")
    # 主消息循环:
    app.mainloop()
