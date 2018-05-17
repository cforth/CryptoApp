import os
from threading import Thread
import tkinter.filedialog as filedialog
from libs.json2gui import *
from libs.CFCrypto import get_file_md5


# 窗口类
class Window(ttk.Frame):
    def __init__(self, ui_json, master=None):
        super().__init__(master)
        # 从json自动设置UI控件
        create_ui(self, ui_json)
        # 从json自动绑定事件
        create_all_binds(self, ui_json)
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

    # 禁用按钮
    def disable_button(self):
        self.__dict__["MD5GenerateButton"]["state"] = "disable"
        self.__dict__["MD5GenerateButton"]["text"] = "处理中"

    # 启用按钮
    def allow_button(self):
        self.__dict__["MD5GenerateButton"]["state"] = "normal"
        self.__dict__["MD5GenerateButton"]["text"] = "MD5生成"

    def md5_generate(self, file_name):
        result_text = get_file_md5(file_name)
        self.__dict__["MD5ResultText"].insert('end', "文件路径: " + file_name)
        self.__dict__["MD5ResultText"].insert('end', "\n")
        self.__dict__["MD5ResultText"].insert('end', "MD5值: ")
        self.__dict__["MD5ResultText"].insert('end', result_text)
        self.__dict__["MD5ResultText"].insert('end', "\n\n")
        self.allow_button()

    def file_from_button_callback(self, event=None):
        self.__dict__["file_from_path"].set(filedialog.askopenfilename())

    def md5_generate_button_callback(self, event=None):
        file_name = self.__dict__["file_from_path"].get()
        if not os.path.isfile(file_name):
            return
        else:
            self.disable_button()
            md5_gen_thread = Thread(target=self.md5_generate, args=(file_name,))
            md5_gen_thread.start()


if __name__ == '__main__':
    app = Window("MD5GenerateUI.json")
    # 设置窗口标题:
    app.master.title("MD5值生成器")
    app.master.minsize(600, 30)
    # 主消息循环:
    app.mainloop()
