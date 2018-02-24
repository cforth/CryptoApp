from libs.json2gui import *
from libs.CFFile import *
import tkinter.filedialog as filedialog


# 窗口类
class Window(ttk.Frame):
    def __init__(self, ui_json, master=None):
        super().__init__(master)
        # 从json自动设置UI控件
        create_ui(self, ui_json)
        # 从json自动绑定事件
        create_all_binds(self, ui_json)
        set_combobox_item(self.__dict__["splitOptionCombobox"], "分割", True)
        self.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.columnconfigure(1, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

    # 文件输入选择
    def file_from_button_callback(self, event=None):
        file_path = filedialog.askopenfilename()
        self.__dict__["file_from"].set(file_path)

    # 文件夹输出选择
    def file_to_button_callback(self, event=None):
        file_path = filedialog.askdirectory()
        self.__dict__["file_to"].set(file_path)

    def split_button_callback(self, event=None):
        file_from_path = self.__dict__["file_from"].get()
        file_to_dir = self.__dict__["file_to"].get()
        file_to_path = os.path.join(file_to_dir, os.path.split(file_from_path)[1])
        split_counter = int(self.__dict__["split_counter"].get())
        split_option = self.__dict__["split_option"].get()
        if split_option == "分割":
            split_size = (os.path.getsize(file_from_path) // split_counter) + 1
            file_split(file_from_path, file_to_path, split_size)
        elif split_option == "合并":
            file_merge(file_from_path, file_to_path, split_counter)


if __name__ == '__main__':
    app = Window("FileSplitUI.json")
    # 设置窗口标题:
    app.master.title("文件分割合并器")
    app.master.minsize(600, 30)
    # 主消息循环:
    app.mainloop()