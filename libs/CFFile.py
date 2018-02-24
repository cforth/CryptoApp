import os


class CFFile(object):
    def __init__(self, path, size):
        self.path = path
        self.tell_pos = 0
        self.size = size
        self.gen_file()

    def gen_file(self):
        with open(self.path, 'w') as f:
            f.seek(self.size - 1)
            f.write('\x00')

    def write(self, data, mode='r+'):
        if len(data) + self.tell_pos > self.size:
            print('error')
            return
        with open(self.path, mode) as f:
            f.seek(self.tell_pos)
            f.write(data)
            self.tell_pos = f.tell()


class FileSearch(object):
    MOVIE = ['mp4', 'avi', 'wmv', 'rmvb', 'mov', 'mkv']
    PIC = ['bmp', 'gif', 'jpeg', 'jpg', 'png']
    DATA = ['zip', 'rar', '7z']
    DOC = ['doc', 'xls', 'ppt', 'pdf', 'txt']

    # 初始化时设置好过滤器
    def __init__(self, the_filter):
        capital_filter = [x.upper() for x in the_filter]
        self.the_filter = the_filter + capital_filter
        print(self.the_filter)

    # 搜索过滤列表内的后缀名文件，返回一个生成器
    def search(self, dir_path):
        for path, subdir, files in os.walk(dir_path):
            for f in files:
                if '.' in f and f[f.rindex('.')+1:] in self.the_filter:
                    file_path = os.path.abspath(path)
                    yield os.path.join(file_path, f)


def file_split(file_path, output_file_path, size):
    if not os.path.exists(file_path):
        raise ValueError('Input file path not exists: %s ', file_path)

    all_len = os.path.getsize(file_path)
    num = all_len // size if all_len % size == 0 else (all_len // size) + 1
    index = 0
    with open(file_path, 'rb') as f:
        for i in range(0, num):
            index += 1
            data = f.read(size)
            if not data:
                break
            with open(output_file_path + '.' + str(index), 'ab') as out:
                out.write(data)


def file_merge(file_path, output_file_path, num):
    if os.path.exists(output_file_path):
        raise ValueError('Output file path exists: %s ', output_file_path)

    with open(output_file_path, 'ab') as out:
        for i in range(1, num + 1):
            with open(file_path + '.' + str(i), 'rb') as f:
                data = f.read()
                if not data:
                    break
                out.write(data)
