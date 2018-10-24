import os
import logging
import tkinter.filedialog as filedialog
import tkinter.messagebox as tkmessagebox
from libs.json2gui import *
from libs.CFCrypto import StringCrypto
from libs.Util import TextSection

logging.basicConfig(level=logging.ERROR)
TEXT_DEFAULT_SIZE = 12


# 窗口类
class Window(ttk.Frame):
    def __init__(self, ui_json, master=None):
        super().__init__(master)
        # 从json自动设置UI控件
        create_ui(self, ui_json)
        # 从json自动绑定事件
        create_all_binds(self, ui_json)
        # 设置滚动条
        set_scrollbar(self.__dict__["fileShowText"],
                      self.__dict__["TextScrollbarX"],
                      self.__dict__["TextScrollbarY"])
        # 设置下拉列表默认值
        set_combobox_item(self.__dict__["cryptoOptionCombobox"], "没有密码", True)
        set_combobox_item(self.__dict__["textSizeOptionCombobox"], "100%", True)
        self.__dict__["textSizeOptionCombobox"].bind("<<ComboboxSelected>>", self.set_text_size)
        self.text_size = TEXT_DEFAULT_SIZE
        self.current_file_path = None
        self.file_text = None
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
        self.section = TextSection(self, self.__dict__["fileShowText"])
        self.menu.add_command(label="复制", command=self.section.on_copy)
        self.menu.add_separator()
        self.menu.add_command(label="粘贴", command=self.section.on_paste)
        self.menu.add_separator()
        self.menu.add_command(label="剪切", command=self.section.on_cut)
        self.__dict__["fileShowText"].bind("<Button-3>", self.popupmenu)

    # 设置文本字体大小
    def set_text_size(self, event=None):
        text_font_info_dict = {"75%": TEXT_DEFAULT_SIZE * 0.75, "100%": TEXT_DEFAULT_SIZE,
                               "150%": TEXT_DEFAULT_SIZE * 1.5, "200%": TEXT_DEFAULT_SIZE * 2}
        self.text_size = text_font_info_dict[self.__dict__["textSizeOption"].get()]
        text_font = "sans-serif %u" % self.text_size
        self.__dict__["fileShowText"].configure(font=text_font)

    def file_from_button_callback(self, event=None):
        self.current_file_path = filedialog.askopenfilename()
        self.__dict__["filePath"].set(self.current_file_path)
        self.file_show()

    def file_save_button_callback(self, event=None):
        self.file_save(self.current_file_path)

    def file_save_new_button_callback(self, event=None):
        new_file_path = os.path.abspath(filedialog.asksaveasfilename())
        self.file_save(new_file_path)
        self.current_file_path = new_file_path
        self.__dict__["filePath"].set(self.current_file_path)

    def file_show(self):
        if not os.path.isfile(self.current_file_path) or not self.current_file_path.endswith('.txt'):
            return

        crypto_option = self.__dict__["cryptoOption"].get()
        self.__dict__["fileShowText"].delete(0.0, 'end')
        with open(self.current_file_path, "r") as f:
            self.file_text = f.read()
            self.__dict__["fileSaveStatus"].set("")
            if crypto_option == "输入密码":
                password = self.__dict__["password"].get()
                try:
                    self.file_text = StringCrypto(password).decrypt(self.file_text)
                    self.__dict__["fileCryptoStatus"].set("[已加密]")
                except Exception as e:
                    self.file_text = ""
                    self.__dict__["filePath"].set("")
                    self.__dict__["fileCryptoStatus"].set("")
                    self.__dict__["fileSaveStatus"].set("")
                    logging.error("Text Decrypt Error！！！")
                    tkmessagebox.showerror("错误", "文本格式或密码错误！")
            else:
                self.__dict__["fileCryptoStatus"].set("")

            self.__dict__["fileShowText"].insert('end', self.file_text)
            self.set_text_size()

    def file_save(self, file_path):
        if not file_path:
            tkmessagebox.showerror("错误", "文件保存路径不存在！")
            return
        crypto_option = self.__dict__["cryptoOption"].get()
        save_text = self.__dict__["fileShowText"].get(0.0, 'end')

        if crypto_option == "输入密码":
            password = self.__dict__["password"].get()
            save_text = StringCrypto(password).encrypt(save_text)
            self.__dict__["fileCryptoStatus"].set("[已加密]")
        else:
            self.__dict__["fileCryptoStatus"].set("")

        with open(file_path, "w") as f:
            f.write(save_text)

        self.__dict__["fileSaveStatus"].set("[已保存]")
        self.after(2000, self.clear_save_status)

    def clear_save_status(self):
        self.__dict__["fileSaveStatus"].set("")


if __name__ == '__main__':
    app = Window("TextLookUI.json")
    # 设置窗口标题:
    app.master.title("文本查看器")
    app.master.minsize(600, 30)
    # 主消息循环:
    app.mainloop()
