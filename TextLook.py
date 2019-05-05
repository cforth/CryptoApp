import os
import logging
import tkinter.filedialog as filedialog
import tkinter.messagebox as tkmessagebox
from libs.json2gui import *
from libs.CFCrypto import StringCrypto
from libs.Util import TextSection

logging.basicConfig(level=logging.ERROR)
TEXT_DEFAULT_SIZE = 12


# 窗口类
class Window(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master, padding=2)
        # 初始化UI
        self.cryptoOptionCombobox = ttk.Combobox(self, state=['readonly'], values=['输入密码', '没有密码'], width=10)
        self.cryptoOption = tk.StringVar()
        self.cryptoOptionCombobox['textvariable'] = self.cryptoOption
        self.cryptoOptionCombobox.grid(sticky=('w', 'e'), row=0, column=0)
        self.passwordEntry = tk.Entry(self, show='*', width=20)
        self.password = tk.StringVar()
        self.passwordEntry['textvariable'] = self.password
        self.passwordEntry.grid(sticky=('w', 'e'), row=0, column=1)
        self.fileFromButton = ttk.Button(self, text='读取', width=10)
        self.fileFromButton.grid(sticky=('w', 'e'), row=0, column=2)
        self.fileFromButton['command'] = self.file_from_button_callback
        self.fileSaveButton = ttk.Button(self, text='保存', width=10)
        self.fileSaveButton.grid(sticky=('w', 'e'), row=0, column=3)
        self.fileSaveButton['command'] = self.file_save_button_callback
        self.fileSaveNewButton = ttk.Button(self, text='另存为', width=10)
        self.fileSaveNewButton.grid(sticky=('w', 'e'), row=0, column=4)
        self.fileSaveNewButton['command'] = self.file_save_new_button_callback
        self.filePathLabel = tk.Label(self, width=40)
        self.filePath = tk.StringVar()
        self.filePathLabel['textvariable'] = self.filePath
        self.filePathLabel.grid(sticky=('w', 'e'), row=1, column=0, columnspan=6)
        self.fileShowText = tk.Text(self, width=60, height=20)
        self.fileShowText.grid(sticky=('w', 'e', 'n', 's'), row=2, column=0, columnspan=5)
        self.TextScrollbarY = ttk.Scrollbar(self, orient='vertical')
        self.TextScrollbarY.grid(sticky=('n', 's'), row=2, column=5)
        self.TextScrollbarX = ttk.Scrollbar(self, orient='horizontal')
        self.TextScrollbarX.grid(sticky=('w', 'e'), row=3, column=0, columnspan=6)
        self.textWrapOptionCombobox = ttk.Combobox(self, state=['readonly'], values=['换行', '不换行'], width=10)
        self.textWrapOption = tk.StringVar()
        self.textWrapOptionCombobox['textvariable'] = self.textWrapOption
        self.textWrapOptionCombobox.grid(sticky=('w', 'e'), row=4, column=0)
        self.fileCryptoStatusLabel = tk.Label(self, width=10)
        self.fileCryptoStatus = tk.StringVar()
        self.fileCryptoStatusLabel['textvariable'] = self.fileCryptoStatus
        self.fileCryptoStatusLabel.grid(sticky=('w', 'e'), row=4, column=2)
        self.fileSaveStatusLabel = tk.Label(self, width=10)
        self.fileSaveStatus = tk.StringVar()
        self.fileSaveStatusLabel['textvariable'] = self.fileSaveStatus
        self.fileSaveStatusLabel.grid(sticky=('w', 'e'), row=4, column=3)
        self.textSizeOptionCombobox = ttk.Combobox(self, state=['readonly'],
                                                   values=['75%', '100%', '150%', '200%'], width=10)
        self.textSizeOption = tk.StringVar()
        self.textSizeOptionCombobox['textvariable'] = self.textSizeOption
        self.textSizeOptionCombobox.grid(sticky=('w', 'e'), row= 4, column=4)
        self.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        # 设置滚动条
        set_scrollbar(self.fileShowText, self.TextScrollbarX, self.TextScrollbarY)
        # 设置下拉列表默认值
        set_combobox_item(self.cryptoOptionCombobox, "没有密码", True)
        set_combobox_item(self.textSizeOptionCombobox, "100%", True)
        self.textSizeOptionCombobox.bind("<<ComboboxSelected>>", self.set_text_size)
        set_combobox_item(self.textWrapOptionCombobox, "换行", True)
        self.textWrapOptionCombobox.bind("<<ComboboxSelected>>", self.set_text_wrap)
        self.text_size = TEXT_DEFAULT_SIZE
        self.current_file_path = None
        self.file_text = None
        # 设置文本区右键菜单
        self.menu = tk.Menu(self, tearoff=0)
        self.set_text_section()
        self.set_text_size()
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

    # 弹出菜单
    def popupmenu(self, event):
        self.menu.post(event.x_root, event.y_root)

    # 设置文本选中时的右键菜单
    def set_text_section(self):
        self.section = TextSection(self, self.fileShowText)
        self.menu.add_command(label="复制", command=self.section.on_copy)
        self.menu.add_separator()
        self.menu.add_command(label="粘贴", command=self.section.on_paste)
        self.menu.add_separator()
        self.menu.add_command(label="剪切", command=self.section.on_cut)
        self.fileShowText.bind("<Button-3>", self.popupmenu)

    # 设置文本字体大小
    def set_text_size(self, event=None):
        text_font_info_dict = {"75%": TEXT_DEFAULT_SIZE * 0.75, "100%": TEXT_DEFAULT_SIZE,
                               "150%": TEXT_DEFAULT_SIZE * 1.5, "200%": TEXT_DEFAULT_SIZE * 2}
        self.text_size = text_font_info_dict[self.textSizeOption.get()]
        text_font = "sans-serif %u" % self.text_size
        self.fileShowText.configure(font=text_font)

    # 设置文本自动换行或不换行
    def set_text_wrap(self, event=None):
        text_wrap_option = self.textWrapOption.get()
        if text_wrap_option == "不换行":
            self.fileShowText.configure(wrap="none")
        else:
            self.fileShowText.configure(wrap=tk.CHAR)

    def file_from_button_callback(self, event=None):
        current_file_path = filedialog.askopenfilename()
        if current_file_path:
            self.current_file_path = current_file_path
            self.file_show()

    def file_save_button_callback(self, event=None):
        self.file_save(self.current_file_path)

    def file_save_new_button_callback(self, event=None):
        new_file_path = os.path.abspath(filedialog.asksaveasfilename())
        self.file_save(new_file_path)

    def file_show(self):
        if not os.path.isfile(self.current_file_path) or not self.current_file_path.endswith('.txt'):
            logging.error("Text Format Error！！！")
            tkmessagebox.showerror("错误", "文本格式错误！")
            return

        self.filePath.set(self.current_file_path)
        crypto_option = self.cryptoOption.get()
        self.fileShowText.delete(0.0, 'end')
        with open(self.current_file_path, "r") as f:
            self.file_text = f.read()
            self.fileSaveStatus.set("")
            if crypto_option == "输入密码":
                password = self.password.get()
                try:
                    self.file_text = StringCrypto(password).decrypt(self.file_text)
                    self.fileCryptoStatus.set("[已加密]")
                except Exception as e:
                    self.file_text = ""
                    self.filePath.set("")
                    self.fileCryptoStatus.set("")
                    self.fileSaveStatus.set("")
                    logging.error("Text Decrypt Error！！！")
                    tkmessagebox.showerror("错误", "文本格式或密码错误！")
            else:
                self.fileCryptoStatus.set("")

            self.set_text_size()
            self.set_text_wrap()
            self.fileShowText.insert('end', self.file_text)

    def file_save(self, file_path):
        if not file_path or os.path.isdir(file_path):
            tkmessagebox.showerror("错误", "文件保存路径不存在！")
            return
        crypto_option = self.cryptoOption.get()
        save_text = self.fileShowText.get(0.0, 'end')

        if crypto_option == "输入密码":
            password = self.password.get()
            save_text = StringCrypto(password).encrypt(save_text)
            self.fileCryptoStatus.set("[已加密]")
        else:
            self.fileCryptoStatus.set("")

        with open(file_path, "w") as f:
            f.write(save_text)

        self.fileSaveStatus.set("[已保存]")
        self.current_file_path = file_path
        self.filePath.set(self.current_file_path)
        self.after(2000, self.clear_save_status)

    def clear_save_status(self):
        self.fileSaveStatus.set("")


if __name__ == '__main__':
    app = Window()
    # 设置窗口标题:
    app.master.title("文本查看器")
    app.master.minsize(600, 30)
    # 主消息循环:
    app.mainloop()
