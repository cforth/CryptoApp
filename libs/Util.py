import os
import tkinter as tk


# 计算文件夹内的文件个数
def count_files(dir_path):
    count = 0
    for path, subdir, files in os.walk(dir_path):
        for f in files:
            count += 1
    return count


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


# 文本选中时的处理
class TextSection(object):
    def __init__(self, master_widget, text_area):
        self.master_widget = master_widget
        self.text_area = text_area

    def on_paste(self):
        try:
            self.text = self.master_widget.clipboard_get()
        except tk.TclError:
            pass
        try:
            self.text_area.delete('sel.first', 'sel.last')
        except tk.TclError:
            pass
        self.text_area.insert(tk.INSERT, self.text)

    def on_copy(self):
        self.text = self.text_area.get('sel.first', 'sel.last')
        self.master_widget.clipboard_clear()
        self.master_widget.clipboard_append(self.text)

    def on_cut(self):
        self.on_copy()
        try:
            self.text_area.delete('sel.first', 'sel.last')
        except tk.TclError:
            pass
