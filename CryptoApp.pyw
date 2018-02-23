import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import ImgLook
import Cryptor


class TopWindow(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.menubar = tk.Menu(self)
        self.ImgLookWindow = None
        self.CryptoWindow = None
        self.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.master.minsize(100, 40)

        option_menu = tk.Menu(self.menubar, tearoff=0)
        option_menu.add_command(label="图片查看", command=self.img_look)
        option_menu.add_command(label="加密解密", command=self.crypto)
        option_menu.add_separator()
        option_menu.add_command(label="退出", command=self.master.quit)

        # 创建“帮助”下拉菜单
        help_menu = tk.Menu(self.menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self.help_about)

        # 将前面菜单加到菜单栏
        self.menubar.add_cascade(label="功能", menu=option_menu)
        self.menubar.add_cascade(label="帮助", menu=help_menu)

        # 最后再将菜单栏整个加到窗口 root
        self.master.config(menu=self.menubar)

    def clear_window(self):
        if self.ImgLookWindow:
            self.ImgLookWindow.destroy()
            self.ImgLookWindow = None
        elif self.CryptoWindow:
            self.CryptoWindow.destroy()
            self.CryptoWindow = None

    def img_look(self):
        self.clear_window()
        self.ImgLookWindow = ImgLook.Window("ImgLookUI.json", self)
        self.master.title("图片查看器")

    def crypto(self):
        self.clear_window()
        self.CryptoWindow = Cryptor.Window(self)
        self.master.title("加密解密器")

    def help_about(self):
        messagebox.showinfo('关于', 'CF工具箱V1.0')  # 弹出消息提示框

def main():
    master = tk.Tk()
    mb = TopWindow(master)
    mb.crypto()
    master.mainloop()

main()