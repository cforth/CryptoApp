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
        self.nameOption = tk.StringVar()
        self.process_var = tk.DoubleVar()
        self.process_label_var = tk.StringVar()

    # 创建控件
    def create_widgets(self):
        self.cryptOptionCombobox = ttk.Combobox(self, width=10, textvariable=self.cryptOption)
        self.dataOptionCombobox = ttk.Combobox(self, width=10, textvariable=self.dataOption)
        # 选择文件夹选项时是否加密解密文件名
        self.nameCryptoOptionCombobox = ttk.Combobox(self, width=10, textvariable=self.nameOption)
        self.populate_comboboxes()
        self.passwordEntry = ttk.Entry(self, width=40, show="*")
        self.passwordShowButton = ttk.Button(self, text="密码", width=5, command=self.password_show)
        self.textFromEntry = ttk.Entry(self, width=40)
        self.textToEntry = ttk.Entry(self, width=40)
        self.fileFromChooseButton = ttk.Button(self, text="来源", state="disable", width=10,
                                               command=self.file_from_choose)
        self.fileToChooseButton = ttk.Button(self, text="目标", state="disable", width=10, command=self.file_to_choose)
        self.button = ttk.Button(self, text="执行", command=self.converter)
        # 进度条
        self.progressBar = ttk.Progressbar(self, orient='horizontal', mode='determinate', value=0)
        self.progressBar['variable'] = self.process_var
        self.progressLabel = ttk.Label(self, textvariable=self.process_label_var)
        # 文件浏览器
        self.tree = ttk.Treeview(self, height=20)
        self.ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.xsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=self.ysb.set, xscroll=self.xsb.set)
        self.tree.heading('#0', text="预览窗口", anchor='w')
        self.tree.column("#0", anchor="w")

    # 将控件布局
    def create_layout(self):
        pad_w_e = dict(sticky=(tk.W, tk.E), padx="0.5m", pady="0.5m")
        self.passwordShowButton.grid(row=0, column=0, **pad_w_e)
        self.passwordEntry.grid(row=0, column=1, columnspan=3, **pad_w_e)
        self.fileFromChooseButton.grid(row=1, column=0, **pad_w_e)
        self.textFromEntry.grid(row=1, column=1, columnspan=3, **pad_w_e)
        self.fileToChooseButton.grid(row=2, column=0, **pad_w_e)
        self.textToEntry.grid(row=2, column=1, columnspan=3, **pad_w_e)
        self.cryptOptionCombobox.grid(row=3, column=0, **pad_w_e)
        self.dataOptionCombobox.grid(row=3, column=1, **pad_w_e)
        self.nameCryptoOptionCombobox.grid(row=3, column=2, **pad_w_e)
        self.button.grid(row=3, column=3, **pad_w_e)
        self.progressBar.grid(row=4, column=0, columnspan=4, **pad_w_e)
        self.progressLabel.grid(row=5, column=0, columnspan=4, **pad_w_e)
        self.tree.grid(row=6, column=0, columnspan=4, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.ysb.grid(row=6, column=4, sticky=(tk.N, tk.S))
        self.xsb.grid(row=7, column=0, columnspan=5, **pad_w_e)
        self.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.columnconfigure(2, weight=1)
        self.rowconfigure(6, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

    # 绑定事件
    def create_bindings(self):
        self.dataOptionCombobox.bind("<<ComboboxSelected>>", self.data_choose_event)
        self.cryptOptionCombobox.bind("<<ComboboxSelected>>", self.crypt_choose_event)
        # 绑定自定义事件给主窗口
        self.bind("<<DisableCrypto>>", self.disable_crypto_button)
        self.bind("<<AllowCrypto>>", self.allow_crypto_button)

    # 填充下拉列表选项
    def populate_comboboxes(self):
        self.cryptOptionCombobox.state(('readonly',))
        self.dataOptionCombobox.state(('readonly',))
        self.nameCryptoOptionCombobox.state(('readonly',))
        self.cryptOptionCombobox.config(values=["加密", "解密", "加密预览", "解密预览"])
        self.dataOptionCombobox.config(values=["字符串", "文件", "文件夹"])
        self.nameCryptoOptionCombobox.config(values=["修改文件名", "保持文件名"])
        set_combobox_item(self.cryptOptionCombobox, "加密", True)
        set_combobox_item(self.dataOptionCombobox, "字符串", True)
        set_combobox_item(self.nameCryptoOptionCombobox, "修改文件名", True)
        self.nameCryptoOptionCombobox["state"] = "disable"

    # 禁用加密解密按钮
    def disable_crypto_button(self, event=None):
        self.button["state"] = "disable"
        self.button["text"] = "处理中"

    # 启用加密解密按钮
    def allow_crypto_button(self, event=None):
        self.button["state"] = "normal"
        self.button["text"] = "执行"

    # 设置文件选择按钮是否可用
    def data_choose_event(self, event=None):
        if self.dataOption.get() == "字符串":
            self.fileFromChooseButton["state"] = "disable"
            self.fileToChooseButton["state"] = "disable"
            self.nameCryptoOptionCombobox["state"] = "disable"
        elif self.dataOption.get() == "文件" or self.dataOption.get() == "文件夹":
            self.fileFromChooseButton["state"] = "normal"
            self.fileToChooseButton["state"] = "normal"
            self.nameCryptoOptionCombobox["state"] = "readonly"

    # 设置路径输入是否可用
    def crypt_choose_event(self, event=None):
        if self.cryptOption.get() == "加密" or self.cryptOption.get() == "解密":
            self.textToEntry["state"] = "normal"
        elif self.cryptOption.get() == "加密预览" or self.cryptOption.get() == "解密预览":
            self.textToEntry.delete(0, len(self.textToEntry.get()))
            self.textToEntry["state"] = "disable"

    # 显示或隐藏密码
    def password_show(self):
        if self.passwordEntry["show"] == "*":
            self.passwordEntry["show"] = ""
        else:
            self.passwordEntry["show"] = "*"

    # 文件/文件夹输入选择
    def file_from_choose(self):
        file_path = ""
        if self.dataOption.get() == "文件":
            file_path = filedialog.askopenfilename()
            # 选择输入文件路径后，在文件浏览器中选中的文件
            if file_path:
                DirShowHandle(self, self.tree, file_path, lambda x: x).start()
        elif self.dataOption.get() == "文件夹":
            file_path = filedialog.askdirectory()
            # 选择输入文件夹路径后，在文件浏览器中显示路径下的内容
            if file_path:
                DirShowHandle(self, self.tree, file_path, lambda x: x).start()
        self.textFromEntry.delete(0, len(self.textFromEntry.get()))
        self.textFromEntry.insert(0, file_path)

    # 文件夹输出选择
    def file_to_choose(self):
        file_path = filedialog.askdirectory()
        self.textToEntry.delete(0, len(self.textToEntry.get()))
        self.textToEntry.insert(0, file_path)

    # 执行加密或者解密
    def converter(self):
        input_text = self.textFromEntry.get()
        output_text = self.textToEntry.get()
        password = self.passwordEntry.get()
        crypto_option = self.cryptOption.get()
        data_option = self.dataOption.get()
        is_handle_name = True if self.nameOption.get() == "修改文件名" else False

        if not password:
            tkmessagebox.showerror("错误", "密码不能为空！")
            return
        if not input_text:
            tkmessagebox.showerror("错误", "来源不能为空！")
            return

        if crypto_option == "加密预览":
            if data_option == "文件" or data_option == "文件夹":
                DirShowHandle(self, self.tree, input_text, lambda x: text_encrypt(x, password)).start()

        elif crypto_option == "解密预览":
            if data_option == "文件" or data_option == "文件夹":
                DirShowHandle(self, self.tree, input_text, lambda x: text_decrypt(x, password)).start()

        elif data_option == "字符串":
            if crypto_option == "加密":
                output_text = text_encrypt(input_text, password)
            elif crypto_option == "解密":
                output_text = text_decrypt(input_text, password)
            else:
                return
            self.textToEntry.delete(0, len(self.textToEntry.get()))
            self.textToEntry.insert(0, output_text)

        elif data_option == "文件":
            if not output_text:
                tkmessagebox.showerror("错误", "目标不能为空！")
                return
            # 为了不阻塞窗口主程序，使用多线程加密或解密文件
            if crypto_option == "加密":
                FileHandle(self, "encrypt", input_text, output_text, password, is_handle_name).start()
            elif crypto_option == "解密":
                FileHandle(self, "decrypt", input_text, output_text, password, is_handle_name).start()

        elif data_option == "文件夹":
            if not output_text:
                tkmessagebox.showerror("错误", "目标不能为空！")
                return
            if crypto_option == "加密":
                DirHandle(self, "encrypt", input_text, output_text, password, is_handle_name).start()
            elif crypto_option == "解密":
                DirHandle(self, "decrypt", input_text, output_text, password, is_handle_name).start()


if __name__ == '__main__':
    app = Window()
    # 设置窗口标题:
    app.master.title("CF加密解密器")
    # 主消息循环:
    app.mainloop()