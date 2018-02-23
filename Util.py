import logging
import tkinter.messagebox as tkmessagebox
import threading
import time
from threading import Thread
from libs.CFCrypto import *

logging.basicConfig(level=logging.INFO)
# 全局变量，用于进度条显示当前数值
global_now_length = 0


# 计算文件夹内的文件个数
def count_files(dir_path):
    count = 0
    for path, subdir, files in os.walk(dir_path):
        for f in files:
            count += 1
    logging.info(count)
    return count


# 通过obj.get_status方法，获取加密解密对象内部的处理状态和进度，更新全局变量
def update_global_now_length(obj, length):
    global global_now_length
    global_now_length = 0
    while True:
        time.sleep(0.5)
        crypto_status, global_now_length = obj.get_status()
        if not crypto_status or global_now_length >= length:
            logging.info("now_length:%d, length:%d" % (global_now_length, length))
            break
    logging.info("Done!")


# 根据全局变量，更新进度条显示
def update_process_bar(process_var, process_label_var, max_length, max_position=100):
    process_var.set(0.0)
    process_label_var.set("")
    old_length = 0
    global global_now_length
    while True:
        if global_now_length > old_length:
            process_scale = global_now_length / max_length
            process_var.set(process_scale * max_position)
            process_label_var.set(str(int(process_scale * 100)) + " %   任务进行中...")
            logging.info("Old ProcessBar position: %d  New ProcessBar position: %d"
                         % (old_length * max_position / max_length, global_now_length * max_position / max_length))
            old_length = global_now_length
        elif global_now_length == max_length:
            process_var.set(max_position)
            process_label_var.set("100%   任务已完成.")
            return
        time.sleep(0.5)


def set_combobox_item(combobox, text, fuzzy=False):
    for index, value in enumerate(combobox.cget("values")):
        if (fuzzy and text in value) or (value == text):
            combobox.current(index)
            return
    combobox.current(0 if len(combobox.cget("values")) else -1)


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


def file_encrypt(main_window, file_path, output_dir_path, password, is_encrypt_name):
    f_crypto = FileCrypto(password)
    input_file_name = os.path.split(file_path)[1]
    max_length = os.path.getsize(file_path)
    t = Thread(target=update_global_now_length, args=(f_crypto, max_length,))
    b = Thread(target=update_process_bar, args=(main_window.process_var, main_window.process_label_var, max_length))
    # is_encrypt_name为False时，不加密文件名
    if is_encrypt_name:
        output_path = os.path.join(output_dir_path, StringCrypto(password).encrypt(input_file_name))
    else:
        output_path = os.path.join(output_dir_path, input_file_name)
    if os.path.exists(output_path):
        tkmessagebox.showerror("错误", "加密后输出路径下存在同名文件！")
        return
    c = Thread(target=f_crypto.encrypt, args=(file_path, output_path))
    c.start()
    t.start()
    b.start()


def file_decrypt(main_window, file_path, output_dir_path, password, is_decrypt_name):
    f_crypto = FileCrypto(password)
    input_file_name = os.path.split(file_path)[1]
    max_length = os.path.getsize(file_path)
    t = Thread(target=update_global_now_length, args=(f_crypto, max_length,))
    b = Thread(target=update_process_bar, args=(main_window.process_var, main_window.process_label_var, max_length))
    try:
        # is_decrypt_name为False时，不解密文件名
        if is_decrypt_name:
            output_path = os.path.join(output_dir_path, StringCrypto(password).decrypt(input_file_name))
        else:
            output_path = os.path.join(output_dir_path, input_file_name)
        if os.path.exists(output_path):
            tkmessagebox.showerror("错误", "解密后输出路径下存在同名文件！")
            return
        c = Thread(target=f_crypto.decrypt, args=(file_path, output_path))
        c.start()
        t.start()
        b.start()
    except Exception as e:
        logging.warning("Convert error: ", e)
        tkmessagebox.showerror("错误", "输入文件格式或者密码错误！")
    return ""


def dir_encrypt(main_window, dir_path, output_dir_path, password, is_encrypt_name):
    dir_crypto = DirFileCrypto(password)
    max_length = count_files(dir_path)
    t = Thread(target=update_global_now_length, args=(dir_crypto, max_length,))
    b = Thread(target=update_process_bar, args=(main_window.process_var, main_window.process_label_var, max_length))
    if is_encrypt_name:
        output_path = os.path.join(output_dir_path, StringCrypto(password).encrypt(os.path.split(dir_path)[1]))
    else:
        output_path = os.path.join(output_dir_path, os.path.split(dir_path)[1])
    if os.path.exists(output_path):
        tkmessagebox.showerror("错误", "加密后输出路径下存在同名文件夹！")
        return
    # is_encrypt_name为False时，不加密文件和文件夹名
    if is_encrypt_name:
        c = Thread(target=dir_crypto.encrypt, args=(dir_path, output_dir_path))
    else:
        c = Thread(target=dir_crypto.encrypt, args=(dir_path, output_dir_path, False))
    c.start()
    t.start()
    b.start()


def dir_decrypt(main_window, dir_path, output_dir_path, password, is_decrypt_name):
    dir_crypto = DirFileCrypto(password)
    max_length = count_files(dir_path)
    t = Thread(target=update_global_now_length, args=(dir_crypto, max_length,))
    b = Thread(target=update_process_bar, args=(main_window.process_var, main_window.process_label_var, max_length))
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
            c = Thread(target=dir_crypto.decrypt, args=(dir_path, output_dir_path))
        else:
            c = Thread(target=dir_crypto.decrypt, args=(dir_path, output_dir_path, False))
        c.start()
        t.start()
        b.start()
    except Exception as e:
        logging.warning("Convert error: ", e)
        tkmessagebox.showerror("错误", "输入文件格式或者密码错误！")
    return ""


class FileHandle(threading.Thread):
    def __init__(self, main_window, mode, file_path, output_dir_path, password, is_handle_name):
        threading.Thread.__init__(self)
        self.main_window = main_window
        self.mode = mode
        self.file_path = file_path
        self.output_dir_path = output_dir_path
        self.password = password
        self.is_handle_name = is_handle_name

    def run(self):
        if not os.path.exists(self.file_path):
            tkmessagebox.showerror("错误", "输入路径不存在！")
            return

        if not os.path.exists(self.output_dir_path):
            tkmessagebox.showerror("错误", "输出目录不存在！")
            return

        # 发送消息给主窗口，禁用按钮
        self.main_window.event_generate("<<DisableCrypto>>", when="tail")
        if self.mode == "encrypt":
            file_encrypt(self.main_window, self.file_path, self.output_dir_path, self.password, self.is_handle_name)
        elif self.mode == "decrypt":
            file_decrypt(self.main_window, self.file_path, self.output_dir_path, self.password, self.is_handle_name)
        self.main_window.event_generate("<<AllowCrypto>>", when="tail")


class DirHandle(threading.Thread):
    def __init__(self, main_window, mode, dir_path, output_dir_path, password, is_handle_name):
        threading.Thread.__init__(self)
        self.main_window = main_window
        self.mode = mode
        self.dir_path = dir_path
        self.output_dir_path = output_dir_path
        self.password = password
        self.is_handle_name = is_handle_name

    def run(self):
        if not os.path.exists(self.dir_path):
            tkmessagebox.showerror("错误", "输入路径不存在！")
            return

        if is_sub_path(self.output_dir_path, self.dir_path):
            tkmessagebox.showerror("错误", "输出路径不能是输入路径的子路径！")
            return

        # 发送消息给主窗口，禁用按钮
        self.main_window.event_generate("<<DisableCrypto>>", when="tail")
        if self.mode == "encrypt":
            dir_encrypt(self.main_window, self.dir_path, self.output_dir_path, self.password, self.is_handle_name)
        elif self.mode == "decrypt":
            dir_decrypt(self.main_window, self.dir_path, self.output_dir_path, self.password, self.is_handle_name)
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
        root_node = self.tree.insert('', 'end', text=self.name_handle_func(os.path.split(abspath)[1]), open=True)
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
