import logging
import tkinter.messagebox as tkmessagebox
import threading
from libs.CFCrypto import *


def set_combobox_item(combobox, text, fuzzy=False):
    for index, value in enumerate(combobox.cget("values")):
        if (fuzzy and text in value) or (value == text):
            combobox.current(index)
            return
    combobox.current(0 if len(combobox.cget("values")) else -1)


def validate_null(title, string):
    if not string:
        tkmessagebox.showerror("错误", title + " 为空！")
        return False
    return True


def is_sub_path(output_path, input_path):
    input_dir = os.path.abspath(input_path).replace('\\', '/')
    output_dir = os.path.abspath(output_path).replace('\\', '/')
    if input_dir in output_dir:
        return True
    else:
        return False


def text_encrypt(plain_text, password):
    string_crypt = StringCrypto(password)
    return string_crypt.encrypt(plain_text)


def text_decrypt(cipher_text, password):
    string_crypt = StringCrypto(password)
    try:
        return string_crypt.decrypt(cipher_text)
    except Exception as e:
        logging.warning("Convert error: ", e)
    return "输入格式或者密码错误！"


def file_encrypt(file_path, output_dir_path, password):
    f_crypto = FileCrypto(password)
    input_file_name = os.path.split(file_path)[1]
    f_crypto.encrypt(file_path, os.path.join(output_dir_path, StringCrypto(password).encrypt(input_file_name)))


def file_decrypt(file_path, output_dir_path, password):
    f_crypto = FileCrypto(password)
    input_file_name = os.path.split(file_path)[1]
    try:
        f_crypto.decrypt(file_path, os.path.join(output_dir_path, StringCrypto(password).decrypt(input_file_name)))
    except Exception as e:
        logging.warning("Convert error: ", e)
        tkmessagebox.showerror("错误", "输入文件格式或者密码错误！")
    return ""


def dir_encrypt(dir_path, output_dir_path, password):
    dir_crypto = DirFileCrypto(password)
    name_crypto = DirNameCrypto(password)
    input_dir_name = os.path.split(dir_path)[1] if not dir_path.endswith('/') else os.path.split(dir_path[:-1])[1]
    dir_crypto.encrypt(dir_path, output_dir_path)
    name_crypto.encrypt(os.path.join(output_dir_path, input_dir_name))


def dir_decrypt(dir_path, output_dir_path, password):
    dir_crypto = DirFileCrypto(password)
    name_crypto = DirNameCrypto(password)
    input_dir_name = os.path.split(dir_path)[1] if not dir_path.endswith('/') else os.path.split(dir_path[:-1])[1]
    try:
        dir_crypto.decrypt(dir_path, output_dir_path)
        name_crypto.decrypt(os.path.join(output_dir_path, input_dir_name))
    except Exception as e:
        logging.warning("Convert error: ", e)
        tkmessagebox.showerror("错误", "输入文件格式或者密码错误！")
    return ""


class FileHandle(threading.Thread):
    def __init__(self, main_window, mode, file_path, output_dir_path, password):
        threading.Thread.__init__(self)
        self.main_window = main_window
        self.mode = mode
        self.file_path = file_path
        self.output_dir_path = output_dir_path
        self.password = password

    def run(self):
        if not os.path.exists(self.file_path):
            tkmessagebox.showerror("错误", "输入路径不存在！")
            return

        if os.path.exists(os.path.join(self.output_dir_path, os.path.split(self.file_path)[1])):
            tkmessagebox.showerror("错误", "输出路径下存在同名文件！")
            return

        # 发送消息给主窗口，禁用按钮
        self.main_window.event_generate("<<DisableCrypto>>", when="tail")
        if self.mode == "encrypt":
            file_encrypt(self.file_path, self.output_dir_path, self.password)
        elif self.mode == "decrypt":
            file_decrypt(self.file_path, self.output_dir_path, self.password)
        self.main_window.event_generate("<<AllowCrypto>>", when="tail")


class DirHandle(threading.Thread):
    def __init__(self, main_window, mode, dir_path, output_dir_path, password):
        threading.Thread.__init__(self)
        self.main_window = main_window
        self.mode = mode
        self.dir_path = dir_path
        self.output_dir_path = output_dir_path
        self.password = password

    def run(self):
        if not os.path.exists(self.dir_path):
            tkmessagebox.showerror("错误", "输入路径不存在！")
            return

        if os.path.exists(os.path.join(self.output_dir_path, os.path.split(self.dir_path)[1])):
            tkmessagebox.showerror("错误", "输出路径下存在同名文件夹！")
            return

        if is_sub_path(self.output_dir_path, self.dir_path):
            tkmessagebox.showerror("错误", "输出路径不能是输入路径的子路径！")
            return

        # 发送消息给主窗口，禁用按钮
        self.main_window.event_generate("<<DisableCrypto>>", when="tail")
        if self.mode == "encrypt":
            dir_encrypt(self.dir_path, self.output_dir_path, self.password)
        elif self.mode == "decrypt":
            dir_decrypt(self.dir_path, self.output_dir_path, self.password)
        self.main_window.event_generate("<<AllowCrypto>>", when="tail")


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
        root_node = self.tree.insert('', 'end', text=abspath, open=True)
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
                name = name_handle_func(p)
                oid = self.tree.insert(parent, 'end', text=name, open=False)
                if isdir:
                    self.process_directory(oid, abspath, name_handle_func)
        else:
            name = name_handle_func(os.path.basename(path))
            self.tree.insert(parent, 'end', text=name, open=False)
