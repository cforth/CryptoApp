import logging
import tkinter.messagebox as tkmessagebox
import threading
from libs.CFCrypto import StringCrypto
from libs.CFCrypto import FileCrypto


def set_combobox_item(combobox, text, fuzzy=False):
    for index, value in enumerate(combobox.cget("values")):
        if (fuzzy and text in value) or (value == text):
            combobox.current(index)
            return
    combobox.current(0 if len(combobox.cget("values")) else -1)


def validate(title, string):
    if not string:
        tkmessagebox.showerror("错误", title + "为空！")
        return False
    return True


def text_encrypt(plain_text, password):
    string_crypt = StringCrypto(password)
    return string_crypt.encrypt(plain_text)


def text_decrypt(cipher_text, password):
    string_crypt = StringCrypto(password)
    try:
        return string_crypt.decrypt(cipher_text)
    except Exception as e:
        logging.warning("Convert error: ", e)
        tkmessagebox.showerror("错误", "输入格式或者密码错误！")
    return ""


def file_encrypt(file_path, output_file_path, password):
    my_crypto = FileCrypto(password)
    my_crypto.encrypt(file_path, output_file_path)


def file_decrypt(file_path, output_file_path, password):
    my_crypto = FileCrypto(password)
    try:
        my_crypto.decrypt(file_path, output_file_path)
    except Exception as e:
        logging.warning("Convert error: ", e)
        tkmessagebox.showerror("错误", "输入文件格式或者密码错误！")
    return ""


class FileHandle(threading.Thread):
    def __init__(self, mode, file_path, output_file_path, password):
        threading.Thread.__init__(self)
        self.mode = mode
        self.file_path = file_path
        self.output_file_path = output_file_path
        self.password = password

    def run(self):
        if self.mode == "encrypt":
            file_encrypt(self.file_path, self.output_file_path, self.password)
        elif self.mode == "decrypt":
            file_decrypt(self.file_path, self.output_file_path, self.password)
