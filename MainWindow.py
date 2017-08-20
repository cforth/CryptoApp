import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as filedialog
import datetime, math
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
        self.populate_comboboxes()
        self.passwordLabel = ttk.Label(self, text="密码:")
        self.passwordEntry = ttk.Entry(self, width=100, show="*")
        self.passwordShowButton = ttk.Button(self, text="显隐密码", command=self.password_show)
        self.textFromLabel = ttk.Label(self, text="输入:")
        self.textFromEntry = ttk.Entry(self, width=100)
        self.textToLabel = ttk.Label(self, text="输出:")
        self.textToEntry = ttk.Entry(self, width=100)
        self.fileFromChooseButton = ttk.Button(self, text="选择文件/文件夹", state="disable", command=self.file_from_choose)
        self.fileToChooseButton = ttk.Button(self, text="选择文件夹", state="disable", command=self.file_to_choose)
        self.button = ttk.Button(self, text="执行", command=self.converter)
        # 进度条
        self.progressBar = ttk.Progressbar(self, orient='horizontal', mode='determinate', value=0)
        # 文件浏览器
        self.tree = ttk.Treeview(self, show="headings", height=18, columns=("a", "b", "c", "d", "e"))
        self.vbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.vbar.set)
        self.tree.column("a", width=50, anchor="w")
        self.tree.column("b", width=200, anchor="w")
        self.tree.column("c", width=200, anchor="w")
        self.tree.column("d", width=200, anchor="w")
        self.tree.column("e", width=200, anchor="w")
        self.tree.heading("a", text="编号")
        self.tree.heading("b", text="名称")
        self.tree.heading("c", text="修改时间")
        self.tree.heading("d", text="类型")
        self.tree.heading("e", text="大小")


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
        self.progressBar.grid(row=3, column=0, columnspan=4, **pad_w_e)
        self.tree.grid(row=4, column=0, columnspan=4, **pad_w_e)
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
        self.cryptOptionCombobox.bind("<<ComboboxSelected>>", self.crypt_choose_event)
        # 绑定自定义事件给主窗口
        self.bind("<<DisableCrypto>>", self.disable_crypto_button)
        self.bind("<<AllowCrypto>>", self.allow_crypto_button)

    # 填充下拉列表选项
    def populate_comboboxes(self):
        self.cryptOptionCombobox.state(('readonly',))
        self.dataOptionCombobox.state(('readonly',))
        self.cryptOptionCombobox.config(values=["加密", "解密", "加密预览", "解密预览"])
        self.dataOptionCombobox.config(values=["字符串", "文件", "文件夹"])
        set_combobox_item(self.cryptOptionCombobox, "加密", True)
        set_combobox_item(self.dataOptionCombobox, "字符串", True)

    # 禁用加密解密按钮，开启进度条
    def disable_crypto_button(self, event=None):
        # 进度条显示
        self.progressBar.start()
        self.button["state"] = "disable"
        self.button["text"] = "处理中"

    # 启用加密解密按钮，关闭进度条
    def allow_crypto_button(self, event=None):
        # 进度条停止
        self.progressBar.stop()
        self.button["state"] = "normal"
        self.button["text"] = "执行"

    # 设置文件选择按钮是否可用
    def data_choose_event(self, event=None):
        if self.dataOption.get() == "字符串":
            self.fileFromChooseButton["state"] = "disable"
            self.fileToChooseButton["state"] = "disable"
        elif self.dataOption.get() == "文件" or self.dataOption.get() == "文件夹":
            self.fileFromChooseButton["state"] = "normal"
            self.fileToChooseButton["state"] = "normal"

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

    # 在文件浏览器中显示路径下的文件
    def explorer_file_show(self, file_path, name_handle_func):
        # 先清空内容
        [self.tree.delete(item) for item in self.tree.get_children()]
        f_path = os.path.realpath(file_path)
        f_name = name_handle_func(os.path.basename(f_path))
        f_mtime = os.path.getmtime(f_path)
        f_date = datetime.datetime.fromtimestamp(f_mtime).strftime('%Y/%m/%d %H:%M:%S')
        f_type = "文件"
        f_size = os.path.getsize(f_path)
        f_kb_size = str(math.ceil(f_size / 1024)) + "KB"
        self.tree.insert("", "end", values=("", f_name, f_date, f_type, f_kb_size))

    # 在文件浏览器中显示路径下的所有文件或文件夹
    def explorer_dir_show(self, dir_path, name_handle_func):
        sub_files = sorted(os.listdir(dir_path))
        length = len(sub_files)
        # 先清空内容
        [self.tree.delete(item) for item in self.tree.get_children()]
        for i in range(0, length):
            f_name = name_handle_func(sub_files[i])
            f_path = os.path.realpath(os.path.join(dir_path, sub_files[i]))
            f_mtime = os.path.getmtime(f_path)
            f_date = datetime.datetime.fromtimestamp(f_mtime).strftime('%Y/%m/%d %H:%M:%S')
            f_type = "文件夹" if os.path.isdir(f_path) else "文件"
            f_size = os.path.getsize(f_path)
            f_kb_size = str(math.ceil(f_size/1024)) + "KB" if f_type != "文件夹" else ""
            self.tree.insert("", "end", values=(i+1, f_name, f_date, f_type, f_kb_size))

    # 文件/文件夹输入选择
    def file_from_choose(self):
        file_path = ""
        if self.dataOption.get() == "文件":
            file_path = filedialog.askopenfilename()
            # 选择输入文件路径后，在文件浏览器中选中的文件
            if file_path:
                self.explorer_file_show(file_path, lambda x: x)
        elif self.dataOption.get() == "文件夹":
            file_path = filedialog.askdirectory()
            # 选择输入文件夹路径后，在文件浏览器中显示路径下的内容
            if file_path:
                self.explorer_dir_show(file_path, lambda x: x)
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
        if crypto_option == "加密预览":
            if validate("密码", password) and validate("输入", input_text):
                if data_option == "文件":
                    self.explorer_file_show(input_text, lambda x: text_encrypt(x, password))
                elif data_option == "文件夹":
                    self.explorer_dir_show(input_text, lambda x: text_encrypt(x, password))

        elif crypto_option == "解密预览":
            if validate("密码", password) and validate("输入", input_text):
                if data_option == "文件":
                    self.explorer_file_show(input_text, lambda x: text_decrypt(x, password))
                elif data_option == "文件夹":
                    self.explorer_dir_show(input_text, lambda x: text_decrypt(x, password))

        elif data_option == "字符串":
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
                if os.path.exists(input_text):
                    # 为了不阻塞窗口主程序，使用多线程加密或解密文件
                    if crypto_option == "加密":
                        FileHandle(self, "encrypt", input_text, output_text, password).start()
                    elif crypto_option == "解密":
                        FileHandle(self, "decrypt", input_text, output_text, password).start()
                    else:
                        return
                else:
                    path_error_msg(input_text)

        elif data_option == "文件夹":
            if validate("密码", password) \
                    and validate("输入", input_text) and validate("输出", output_text):
                if os.path.exists(input_text):
                    if crypto_option == "加密":
                        DirHandle(self, "encrypt", input_text, output_text, password).start()
                    elif crypto_option == "解密":
                        DirHandle(self, "decrypt", input_text, output_text, password).start()
                    else:
                        return
                else:
                    path_error_msg(input_text)
