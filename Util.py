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


def validate(title, string):
    if not string:
        tkmessagebox.showerror("错误", title + " 为空！")
        return False
    return True


def path_error_msg(file_path):
    tkmessagebox.showerror("错误", file_path + " 路径错误！")


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
        # 发送消息给主窗口，禁用按钮
        self.main_window.event_generate("<<DisableCrypto>>", when="tail")
        if self.mode == "encrypt":
            dir_encrypt(self.dir_path, self.output_dir_path, self.password)
        elif self.mode == "decrypt":
            dir_decrypt(self.dir_path, self.output_dir_path, self.password)
        self.main_window.event_generate("<<AllowCrypto>>", when="tail")
