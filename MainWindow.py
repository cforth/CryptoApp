import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as filedialog
from Util import *


class Window(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master, padding=2)
        self.create_variables()
        self.create_widgets()
        self.create_layout()
        self.create_bindings()

    # 创建控件中需要用到的变量
    def create_variables(self):
        self.cryptOption = tk.StringVar()
        self.dataOption = tk.StringVar()

    # 创建控件
    def create_widgets(self):
        self.cryptOptionCombobox = ttk.Combobox(self, textvariable=self.cryptOption)
        self.dataOptionCombobox = ttk.Combobox(self, textvariable=self.dataOption)
        self.passwordLabel = ttk.Label(self, text="密码:")
        self.passwordEntry = ttk.Entry(self, width=100, show="*")
        self.passwordShowButton = ttk.Button(self, text="显隐密码", command=self.password_show)
        self.textFromLabel = ttk.Label(self, text="输入:")
        self.textFromEntry = ttk.Entry(self, width=100)
        self.textToLabel = ttk.Label(self, text="输出:")
        self.textToEntry = ttk.Entry(self, width=100)
        self.fileFromChooseButton = ttk.Button(self, text="选择文件",  state="disable", command=self.file_from_choose)
        self.fileToChooseButton = ttk.Button(self, text="选择文件",  state="disable", command=self.file_to_choose)
        self.button = ttk.Button(self, text="执行", command=self.converter)
        self.populate_comboboxes()

    # 将控件布局
    def create_layout(self):
        pad_w_e = dict(sticky=(tk.W, tk.E), padx="0.5m", pady="0.5m")
        self.cryptOptionCombobox.grid(row=0, column=0, **pad_w_e)
        self.dataOptionCombobox.grid(row=1, column=0, **pad_w_e)
        self.button.grid(row=2, column=0, **pad_w_e)
        self.passwordLabel.grid(row=0, column=1, **pad_w_e)
        self.passwordEntry.grid(row=0, column=2, **pad_w_e)
        self.passwordShowButton.grid(row=0, column=3, **pad_w_e)
        self.textFromLabel.grid(row=1, column=1, **pad_w_e)
        self.textFromEntry.grid(row=1, column=2, **pad_w_e)
        self.textToLabel.grid(row=2, column=1, **pad_w_e)
        self.textToEntry.grid(row=2, column=2, **pad_w_e)
        self.fileFromChooseButton.grid(row=1, column=3, **pad_w_e)
        self.fileToChooseButton.grid(row=2, column=3, **pad_w_e)
        self.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=2)
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.master.minsize(150, 40)

    # 绑定事件
    def create_bindings(self):
        self.dataOptionCombobox.bind("<<ComboboxSelected>>", self.data_choose_event)

    # 填充下拉列表选项
    def populate_comboboxes(self):
        self.cryptOptionCombobox.state(('readonly',))
        self.dataOptionCombobox.state(('readonly',))
        self.cryptOptionCombobox.config(values=["加密", "解密"])
        self.dataOptionCombobox.config(values=["字符串", "文件"])
        set_combobox_item(self.cryptOptionCombobox, "加密", True)
        set_combobox_item(self.dataOptionCombobox, "字符串", True)

    # 设置文件选择按钮是否可用
    def data_choose_event(self, event=None):
        if self.dataOption.get() == "字符串":
            self.fileFromChooseButton["state"] = "disable"
            self.fileToChooseButton["state"] = "disable"
        elif self.dataOption.get() == "文件":
            self.fileFromChooseButton["state"] = "normal"
            self.fileToChooseButton["state"] = "normal"

    # 显示或隐藏密码
    def password_show(self):
        if self.passwordEntry["show"] == "*":
            self.passwordEntry["show"] = ""
        else:
            self.passwordEntry["show"] = "*"

    # 文件输入选择
    def file_from_choose(self):
        file_path = filedialog.askopenfilename()
        self.textFromEntry.delete(0, len(self.textFromEntry.get()))
        self.textFromEntry.insert(0, file_path)

    # 文件输出选择
    def file_to_choose(self):
        file_path = filedialog.askdirectory()
        file_name = self.textFromEntry.get()
        file_path += file_name[file_name.rindex("/")+1:] + ".rename"
        self.textToEntry.delete(0, len(self.textToEntry.get()))
        self.textToEntry.insert(0, file_path)

    # 执行加密或者解密
    def converter(self):
        input_text = self.textFromEntry.get()
        output_text = self.textToEntry.get()
        password = self.passwordEntry.get()
        crypto_option = self.cryptOption.get()
        data_option = self.dataOption.get()
        if data_option == "字符串":
            if validate("密码", password) and validate("输入", input_text):
                if crypto_option == "加密":
                    output_text = text_encrypt(input_text, password)
                elif crypto_option == "解密":
                    output_text = text_decrypt(input_text, password)
                else:
                    return
                self.textToEntry.delete(0, len(self.textToEntry.get()))
                self.textToEntry.insert(0, output_text)

        elif data_option == "文件":
            if validate("密码", password) \
                    and validate("输入", input_text) and validate("输出", output_text):
                # 为了不阻塞窗口主程序，使用多线程加密或解密文件
                if crypto_option == "加密":
                    FileHandle("encrypt", input_text, output_text, password).start()
                elif crypto_option == "解密":
                    FileHandle("decrypt", input_text, output_text, password).start()
                else:
                    return