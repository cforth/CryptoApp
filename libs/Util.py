import os


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



