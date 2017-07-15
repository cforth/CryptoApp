import tkinter as tk
import tkinter.messagebox as tkmessagebox
import tkinter.ttk as ttk
import logging
from libs.CFCrypto import *


class Window(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master, padding=2)
        self.create_variables()
        self.create_widgets()
        self.create_layout()

    def create_variables(self):
        self.cryptOption = tk.StringVar()

    def create_widgets(self):
        self.cryptOptionCombobox = ttk.Combobox(self, textvariable=self.cryptOption)
        self.passwordLabel = ttk.Label(self, text="密码:")
        self.passwordEntry = ttk.Entry(self, width=100)
        self.textFromLabel = ttk.Label(self, text="输入:")
        self.textFromEntry = ttk.Entry(self, width=100)
        self.textToLabel = ttk.Label(self, text="输出:")
        self.textToEntry = ttk.Entry(self, width=100)
        self.button = ttk.Button(self, text="执行", command=self.converter)
        self.populate_comboboxes()

    def create_layout(self):
        padWE = dict(sticky=(tk.W, tk.E), padx="0.5m", pady="0.5m")
        padNSEW = dict(sticky=(tk.N, tk.S, tk.E, tk.W), padx="0.5m", pady="0.5m")
        self.cryptOptionCombobox.grid(row=0, column=0, **padWE)
        self.button.grid(row=1, column=0, rowspan=2, **padNSEW)
        self.passwordLabel.grid(row=0, column=1, **padWE)
        self.passwordEntry.grid(row=0, column=2, **padWE)
        self.textFromLabel.grid(row=1, column=1, **padWE)
        self.textFromEntry.grid(row=1, column=2, **padWE)
        self.textToLabel.grid(row=2, column=1, **padWE)
        self.textToEntry.grid(row=2, column=2, **padWE)
        self.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=2)
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.master.minsize(150, 40)

    @staticmethod
    def set_combobox_item(combobox, text, fuzzy=False):
        for index, value in enumerate(combobox.cget("values")):
            if (fuzzy and text in value) or (value == text):
                combobox.current(index)
                return
        combobox.current(0 if len(combobox.cget("values")) else -1)

    def populate_comboboxes(self):
        self.cryptOptionCombobox.state(('readonly',))
        self.cryptOptionCombobox.config(values=["加密", "解密"])
        Window.set_combobox_item(self.cryptOptionCombobox, "加密", True)

    def validate(self, title, string):
        if not string:
            tkmessagebox.showerror("错误", title + "为空！")
            return False
        return True

    def text_encrypt(self, plaintext, password):
        strcrypt = StringCrypto(password)
        return strcrypt.encrypt(plaintext)

    def text_decrypt(self, ciphertext, password):
        strcrypt = StringCrypto(password)
        try:
            return strcrypt.decrypt(ciphertext)
        except Exception as e:
            logging.warning("Convert error: ", e)
            tkmessagebox.showerror("错误", "输入格式或者密码错误！")
        return ""

    def converter(self):
        input_text = self.textFromEntry.get()
        password = self.passwordEntry.get()
        option = self.cryptOption.get()
        if self.validate("密码", password) and self.validate("输入", input_text):
            if option == "加密":
                output_text = self.text_encrypt(input_text, password)
            elif option == "解密":
                output_text = self.text_decrypt(input_text, password)
            else:
                return
            self.textToEntry.delete(0, len(self.textToEntry.get()))
            self.textToEntry.insert(0, output_text)
