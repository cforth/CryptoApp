import tkinter.messagebox as tkmessagebox
import tkinter.ttk as ttk
import logging
from libs.CFCrypto import *


class Window(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master, padding=2)
        self.textFromLabel = ttk.Label(self, text="Cipher text:")
        self.textFromEntry = ttk.Entry(self, width=100)
        self.passwordLabel = ttk.Label(self, text="Enter password:")
        self.passwordEntry = ttk.Entry(self, width=100)
        self.textToLabel = ttk.Label(self, text="Plain text:")
        self.textToEntry = ttk.Entry(self, width=100)
        self.doButton = ttk.Button(self, text="converter", command=self.converter)
        self.textFromLabel.pack()
        self.textFromEntry.pack()
        self.passwordLabel.pack()
        self.passwordEntry.pack()
        self.textToLabel.pack()
        self.textToEntry.pack()
        self.doButton.pack()
        self.pack()

    def validate(self, title, string):
        if not string:
            tkmessagebox.showerror("错误", title + "为空！")
            return False
        return True

    def text_encrypt(self, plaintext, password):
        strcrypt = StringCrypto(password)
        try:
            return strcrypt.encrypt(plaintext)
        except Exception as e:
            logging.warning("Convert error: ", e)
            tkmessagebox.showerror("错误", "明文格式或者密码错误！")
        return ""

    def text_decrypt(self, ciphertext, password):
        strcrypt = StringCrypto(password)
        try:
            return strcrypt.decrypt(ciphertext)
        except Exception as e:
            logging.warning("Convert error: ", e)
            tkmessagebox.showerror("错误", "密文格式或者密码错误！")
        return ""

    def converter(self):
        plaintext = self.textToEntry.get()
        ciphertext = self.textFromEntry.get()
        password = self.passwordEntry.get()

        if self.validate("密码", password):
            if ciphertext and not plaintext:
                self.textToEntry.delete(0, len(self.textToEntry.get()))
                plaintext = self.text_decrypt(ciphertext, password)
                self.textToEntry.insert(0, plaintext)
            elif plaintext and not ciphertext:
                self.textFromEntry.delete(0, len(self.textFromEntry.get()))
                ciphertext = self.text_encrypt(plaintext, password)
                self.textFromEntry.insert(0, ciphertext)
            else:
                tkmessagebox.showerror("错误", "我不知道你到底要转换什么！")
