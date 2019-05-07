import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import TextLook
import ImgLook
import Cryptor
import FileSplit
import RandomPassword
import MD5Generate


class RootWindow(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.menubar = tk.Menu(self)
        self.ChildWindow = None
        self.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        option_menu = tk.Menu(self.menubar, tearoff=0)
        option_menu.add_command(label="文本查看", command=self.text_look)
        option_menu.add_command(label="图片查看", command=self.img_look)
        option_menu.add_command(label="随机密码", command=self.random_password)
        option_menu.add_command(label="文件分割", command=self.file_split)
        option_menu.add_command(label="MD5值", command=self.md5_gen)
        option_menu.add_command(label="加密解密", command=self.crypto)
        option_menu.add_separator()
        option_menu.add_command(label="退出", command=self.quit_program)

        # 创建“帮助”下拉菜单
        help_menu = tk.Menu(self.menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self.help_about)

        # 绑定最顶层窗口的关闭按钮事件
        self.master.protocol("WM_DELETE_WINDOW", self.quit_program)

        # 将前面菜单加到菜单栏
        self.menubar.add_cascade(label="功能", menu=option_menu)
        self.menubar.add_cascade(label="帮助", menu=help_menu)

        # 最后再将菜单栏整个加到窗口 root
        self.master.config(menu=self.menubar)

    def clear_window(self):
        if self.ChildWindow:
            # 确保图片已经清空
            if isinstance(self.ChildWindow, ImgLook.Window):
                self.ChildWindow.cancel_img()
            self.ChildWindow.destroy()
            self.ChildWindow = None

    def text_look(self):
        self.clear_window()
        self.ChildWindow = TextLook.Window(self)
        self.master.title("文本查看器")
        self.master.minsize(600, 30)

    def img_look(self):
        self.clear_window()
        self.ChildWindow = ImgLook.Window()
        self.master.bind("<Key>", self.ChildWindow.key_event)
        self.master.title("图片查看器")
        self.master.minsize(600, 600)

    def random_password(self):
        self.clear_window()
        self.ChildWindow = RandomPassword.Window("RandomPasswordUI.json", self)
        self.master.title("随机密码生成器")
        self.master.minsize(600, 30)

    def file_split(self):
        self.clear_window()
        self.ChildWindow = FileSplit.Window("FileSplitUI.json", self)
        self.master.title("文件分割合并器")
        self.master.minsize(600, 30)

    def md5_gen(self):
        self.clear_window()
        self.ChildWindow = MD5Generate.Window("MD5GenerateUI.json")
        self.master.title("MD5值生成器")
        self.master.minsize(600, 30)

    def crypto(self):
        self.clear_window()
        self.ChildWindow = Cryptor.Window(self)
        self.master.title("加密解密器")
        self.master.minsize(400, 500)

    def help_about(self):
        messagebox.showinfo('关于', 'Crypto工具箱\n'
                            '简单的加密解密GUI程序，使用Python3+Tkinter实现。\n'
                            'https://github.com/cforth/CryptoApp')  # 弹出消息提示框

    def quit_program(self):
        quit_result = tk.messagebox.askokcancel('提示', '真的要退出吗？')
        if quit_result:
            self.master.quit()


if __name__ == '__main__':
    master = tk.Tk()
    mb = RootWindow(master)
    mb.crypto()
    try:
        # 设置窗口图标
        mb.master.iconbitmap('CryptoApp.ico')
    except Exception as e:
        # 忽略图片设置的错误
        pass
    master.mainloop()
