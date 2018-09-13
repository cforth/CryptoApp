import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as filedialog
import tkinter.messagebox as tkmessagebox
import logging
import threading
import time
from threading import Thread
from libs.Util import *
from libs.CFCrypto import *

logging.basicConfig(level=logging.INFO)


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
        # 用于记录文件处理或文件夹处理的进度值
        self.task_now_length = 0
        # 加密解密任务对象，用来改变加密解密的启停状态
        self.crypto_task = None

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
        self.run_button = ttk.Button(self, text="执行", command=self.run_task)
        self.stop_button = ttk.Button(self, text="停止", command=self.stop_task)
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
        # 文件浏览器区右键菜单
        self.tree_menu = tk.Menu(self, tearoff=0)
        self.tree_menu.add_command(label="复制地址", command=self.on_copy_file_path)
        self.tree_menu.add_separator()
        # 输入框右键菜单
        self.entry_menu = tk.Menu(self, tearoff=0)
        self.entry_menu.add_command(label="复制", command=self.on_entry_copy)
        self.entry_menu.add_separator()
        self.entry_menu.add_command(label="粘贴", command=self.on_entry_paste)
        self.entry_menu.add_separator()
        self.entry_menu.add_command(label="剪切", command=self.on_entry_cut)

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
        self.run_button.grid(row=3, column=3, **pad_w_e)
        self.progressBar.grid(row=4, column=0, columnspan=3, **pad_w_e)
        self.stop_button.grid(row=4, column=3, **pad_w_e)
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
        self.tree.bind("<Button-3>", self.pop_tree_menu)
        self.textFromEntry.bind("<FocusIn>", self.get_current_widget)
        self.textToEntry.bind("<FocusIn>", self.get_current_widget)
        self.textFromEntry.bind("<Button-3>", self.pop_entry_menu)
        self.textToEntry.bind("<Button-3>", self.pop_entry_menu)

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

    # 获取当前事件的控件
    def get_current_widget(self, event):
        self.current_widget = event.widget

    # 弹出TreeView菜单
    def pop_tree_menu(self, event):
        self.tree_menu.post(event.x_root, event.y_root)

    # 弹出输入框菜单
    def pop_entry_menu(self, event):
        self.entry_menu.post(event.x_root, event.y_root)

    # 复制选中的文件地址到剪贴板
    def on_copy_file_path(self):
        item_values = self.tree.item(self.tree.selection()[0])['values']
        file_select_path = item_values[0] if item_values else ""
        self.clipboard_clear()
        self.clipboard_append(file_select_path)

    # 剪贴板上的字符串粘贴到Entry中
    def on_entry_paste(self):
        text = ""
        try:
            text = self.clipboard_get()
        except tk.TclError:
            pass
        try:
            self.current_widget.delete(0, 'end')
        except tk.TclError:
            pass
        self.current_widget.insert(tk.INSERT, text)

    # 复制Entry中的字符串到剪贴板
    def on_entry_copy(self):
        text = self.current_widget.get()
        self.clipboard_clear()
        self.clipboard_append(text)

    # 剪切Entry中的字符串到剪贴板
    def on_entry_cut(self):
        self.on_entry_copy()
        try:
            self.current_widget.delete(0, 'end')
        except tk.TclError:
            pass

    # 禁用加密解密按钮
    def disable_crypto_button(self, event=None):
        self.run_button["state"] = "disable"
        self.run_button["text"] = "处理中"

    # 启用加密解密按钮
    def allow_crypto_button(self, event=None):
        self.run_button["state"] = "normal"
        self.run_button["text"] = "执行"

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

    # 更新文件处理或文件夹处理的进度值
    def update_task_now_length(self, obj, length):
        self.task_now_length = 0
        while True:
            time.sleep(0.5)
            crypto_status, self.task_now_length = obj.get_status()
            if not crypto_status or self.task_now_length >= length:
                logging.info("now_length:%d, length:%d" % (self.task_now_length, length))
                break
        logging.info("Done!")

    # 更新进度条
    def update_process_bar(self, max_length, max_position=100):
        # 发送消息给主窗口，禁用按钮
        self.event_generate("<<DisableCrypto>>", when="tail")
        self.process_var.set(0.0)
        self.process_label_var.set("")
        old_length = 0
        while True:
            if self.task_now_length > old_length:
                process_scale = self.task_now_length / max_length
                self.process_var.set(process_scale * max_position)
                self.process_label_var.set(str(int(process_scale * 100)) + " %   任务进行中...")
                logging.info("Old ProcessBar position: %d  New ProcessBar position: %d"
                             % (
                             old_length * max_position / max_length, self.task_now_length * max_position / max_length))
                old_length = self.task_now_length
            elif self.task_now_length == max_length:
                self.process_var.set(max_position)
                self.process_label_var.set("100%   任务已完成.")
                break
            elif self.crypto_task.if_stop():
                self.task_now_length = 0
                self.process_label_var.set("任务已被外部终止.")
                break
            time.sleep(0.5)
        self.event_generate("<<AllowCrypto>>", when="tail")

    # 使用多线程加密文件
    def file_encrypt(self, file_path, output_dir_path, password, is_encrypt_name):
        self.crypto_task = FileCrypto(password)
        input_file_name = os.path.split(file_path)[1]
        max_length = os.path.getsize(file_path)
        update_task_length_thread = Thread(target=self.update_task_now_length, args=(self.crypto_task, max_length,))
        update_process_thread = Thread(target=self.update_process_bar, args=(max_length,))
        # is_encrypt_name为False时，不加密文件名
        if is_encrypt_name:
            output_path = os.path.join(output_dir_path, StringCrypto(password).encrypt(input_file_name))
        else:
            output_path = os.path.join(output_dir_path, input_file_name)
        if os.path.exists(output_path):
            tkmessagebox.showerror("错误", "加密后输出路径下存在同名文件！")
            return
        # 为了不阻塞窗口主程序，使用多线程加密文件
        crypto_thread = Thread(target=self.crypto_task.encrypt, args=(file_path, output_path))
        crypto_thread.start()
        update_task_length_thread.start()
        update_process_thread.start()

    # 使用多线程解密文件
    def file_decrypt(self, file_path, output_dir_path, password, is_decrypt_name):
        self.crypto_task = FileCrypto(password)
        input_file_name = os.path.split(file_path)[1]
        max_length = os.path.getsize(file_path)
        update_task_length_thread = Thread(target=self.update_task_now_length, args=(self.crypto_task, max_length,))
        update_process_thread = Thread(target=self.update_process_bar, args=(max_length,))
        try:
            # is_decrypt_name为False时，不解密文件名
            if is_decrypt_name:
                output_path = os.path.join(output_dir_path, StringCrypto(password).decrypt(input_file_name))
            else:
                output_path = os.path.join(output_dir_path, input_file_name)
            if os.path.exists(output_path):
                tkmessagebox.showerror("错误", "解密后输出路径下存在同名文件！")
                return
            # 为了不阻塞窗口主程序，使用多线程解密文件
            crypto_thread = Thread(target=self.crypto_task.decrypt, args=(file_path, output_path))
            crypto_thread.start()
            update_task_length_thread.start()
            update_process_thread.start()
        except Exception as e:
            logging.warning("Convert error: ", e)
            tkmessagebox.showerror("错误", "输入文件格式或者密码错误！")
        return ""

    # 使用多线程加密文件夹
    def dir_encrypt(self, dir_path, output_dir_path, password, is_encrypt_name):
        self.crypto_task = DirFileCrypto(password)
        max_length = count_files(dir_path)
        update_task_length_thread = Thread(target=self.update_task_now_length, args=(self.crypto_task, max_length,))
        update_process_thread = Thread(target=self.update_process_bar, args=(max_length,))
        if is_encrypt_name:
            output_path = os.path.join(output_dir_path, StringCrypto(password).encrypt(os.path.split(dir_path)[1]))
        else:
            output_path = os.path.join(output_dir_path, os.path.split(dir_path)[1])
        if os.path.exists(output_path):
            tkmessagebox.showerror("错误", "加密后输出路径下存在同名文件夹！")
            return
        # is_encrypt_name为False时，不加密文件和文件夹名
        if is_encrypt_name:
            crypto_thread = Thread(target=self.crypto_task.encrypt, args=(dir_path, output_dir_path))
        else:
            crypto_thread = Thread(target=self.crypto_task.encrypt, args=(dir_path, output_dir_path, False))
        crypto_thread.start()
        update_task_length_thread.start()
        update_process_thread.start()

    # 使用多线程解密文件夹
    def dir_decrypt(self, dir_path, output_dir_path, password, is_decrypt_name):
        self.crypto_task = DirFileCrypto(password)
        max_length = count_files(dir_path)
        update_task_length_thread = Thread(target=self.update_task_now_length, args=(self.crypto_task, max_length,))
        update_process_thread = Thread(target=self.update_process_bar, args=(max_length,))
        try:
            if is_decrypt_name:
                output_path = os.path.join(output_dir_path, StringCrypto(password).decrypt(os.path.split(dir_path)[1]))
            else:
                output_path = os.path.join(output_dir_path, os.path.split(dir_path)[1])
            if os.path.exists(output_path):
                tkmessagebox.showerror("错误", "解密后输出路径下存在同名文件夹！")
                return
            # is_decrypt_name为False时，不解密文件和文件夹名
            if is_decrypt_name:
                crypto_thread = Thread(target=self.crypto_task.decrypt, args=(dir_path, output_dir_path))
            else:
                crypto_thread = Thread(target=self.crypto_task.decrypt, args=(dir_path, output_dir_path, False))
            crypto_thread.start()
            update_task_length_thread.start()
            update_process_thread.start()
        except Exception as e:
            logging.warning("Convert error: ", e)
            tkmessagebox.showerror("错误", "输入文件格式或者密码错误！")
        return ""

    # 强制停止任务
    def stop_task(self):
        if self.crypto_task:
            self.crypto_task.stop_handle()

    # 执行加密或者解密任务
    def run_task(self):
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
                DirShowHandle(self, self.tree, input_text, lambda x: StringCrypto(password).encrypt(x)).start()

        elif crypto_option == "解密预览":
            if data_option == "文件" or data_option == "文件夹":
                DirShowHandle(self, self.tree, input_text, lambda x: StringCrypto(password).decrypt(x)).start()

        elif data_option == "字符串":
            if crypto_option == "加密":
                output_text = StringCrypto(password).encrypt(input_text)
            elif crypto_option == "解密":
                try:
                    output_text = StringCrypto(password).decrypt(input_text)
                except Exception as e:
                    logging.warning("Convert error: ", e)
                    output_text = "输入格式或者密码错误！"
            else:
                return
            self.textToEntry.delete(0, len(self.textToEntry.get()))
            self.textToEntry.insert(0, output_text)

        elif data_option == "文件":
            if not output_text:
                tkmessagebox.showerror("错误", "目标不能为空！")
                return

            if not os.path.exists(input_text):
                tkmessagebox.showerror("错误", "输入路径不存在！")
                return

            if not os.path.exists(output_text):
                tkmessagebox.showerror("错误", "输出目录不存在！")
                return

            if crypto_option == "加密":
                self.file_encrypt(input_text, output_text, password, is_handle_name)
            elif crypto_option == "解密":
                self.file_decrypt(input_text, output_text, password, is_handle_name)

        elif data_option == "文件夹":
            if not output_text:
                tkmessagebox.showerror("错误", "目标不能为空！")
                return

            if not os.path.exists(input_text):
                tkmessagebox.showerror("错误", "输入路径不存在！")
                return

            if not os.path.exists(output_text):
                tkmessagebox.showerror("错误", "输出目录不存在！")
                return

            if is_sub_path(output_text, input_text):
                tkmessagebox.showerror("错误", "输出路径不能是输入路径的子路径！")
                return

            if crypto_option == "加密":
                self.dir_encrypt(input_text, output_text, password, is_handle_name)
            elif crypto_option == "解密":
                self.dir_decrypt(input_text, output_text, password, is_handle_name)


# 预览加密文件名称
class DirShowHandle(threading.Thread):
    def __init__(self, main_window, tree, f_path, name_handle_func):
        threading.Thread.__init__(self)
        self.main_window = main_window
        self.tree = tree
        self.f_path = f_path
        self.name_handle_func = name_handle_func

    def run(self):
        # 发送消息给主窗口，禁用按钮
        self.main_window.event_generate("<<DisableCrypto>>", when="tail")
        [self.tree.delete(item) for item in self.tree.get_children()]
        abspath = os.path.abspath(self.f_path)
        try:
            root_node = self.tree.insert('', 'end', text=self.name_handle_func(os.path.split(abspath)[1]), open=True)
        except Exception as e:
            logging.warning("Convert error: ", e)
            root_node = self.tree.insert('', 'end', text="输入格式或者密码错误！", open=True)
        self.process_directory(root_node, abspath, self.name_handle_func)
        self.main_window.event_generate("<<AllowCrypto>>", when="tail")

    def process_directory(self, parent, path, name_handle_func):
        if os.path.isdir(path):
            # 遍历路径下的子目录
            for p in os.listdir(path):
                # 构建路径
                abspath = os.path.join(path, p)
                # 是否存在子目录
                isdir = os.path.isdir(abspath)
                try:
                    name = name_handle_func(p)
                except Exception as e:
                    logging.warning("Convert error: ", e)
                    name = "输入格式或者密码错误！"
                # 将文件地址加入tree的item的values中
                oid = self.tree.insert(parent, 'end', text=name, values=[abspath], open=False)
                if isdir:
                    self.process_directory(oid, abspath, name_handle_func)
        else:
            name = name_handle_func(os.path.basename(path))
            self.tree.insert(parent, 'end', text=name, open=False)


if __name__ == '__main__':
    app = Window()
    # 设置窗口标题:
    app.master.title("CF加密解密器")
    app.master.minsize(400, 500)
    # 主消息循环:
    app.mainloop()
