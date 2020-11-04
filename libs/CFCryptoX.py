import base64
import hashlib
import json
from functools import partial
import os
import re
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from libs.Key import gen_aes_key

# 一个AES加密块的字节长度为16字节(128位)
BLOCK_SIZE: int = 16
# 读写文件时，每次读写的字节数
BUFFER_SIZE: int = 10 * 1024 * 1024
# 文件头加密标识，验证密码是否正确
ENCRYPT_MARK: bytes = b'CF_CRYPTO_X'
# 默认的初始化向量，经过urlsafe_b64encode编码后字符串
DEFAULT_IV_STR = "UEr9si9EynusD5GGVuiqKw=="


# 字符串MD5生成
def get_str_md5(string: str, encoding='utf-8') -> str:
    my_hash = hashlib.md5()
    my_hash.update(string.encode(encoding))
    return my_hash.hexdigest()


# 路径加密解密
def folder_path_convert(folder_path: str, name_convert_func: callable) -> str:
    name_list = re.split(r'[\\/]', folder_path)
    crypto_list = [name_convert_func(s) for s in name_list]
    return '/'.join(crypto_list)


# 通过解密加密文件开头128个字节的块是否与加密标识相符，来判断密码是否正确
def verify_password(password: str, iv: str, data_head: bytes) -> bool:
    try:
        decrypt_head = ByteCrypto(password, iv).decrypt(data_head)
        return True if decrypt_head[:len(ENCRYPT_MARK)] == ENCRYPT_MARK else False
    except Exception as e:
        print('Exception: ', e)
        print("Decrypt Password Error!")
        return False


# 加密解密基类，设置密码和其他参数
class BaseCrypto(object):
    def __init__(self, password, iv_str=None, salt=None, use_md5=False, use_urlsafe=False, buffer_size=BUFFER_SIZE):
        self.password = password
        # 生成密钥时，选择是否加盐，是否使用md5值
        self.key = gen_aes_key(password, salt, use_md5)
        # 使用base64模块将字节转与字符串互相转换时，是否用urlsafe模式
        self.use_urlsafe = use_urlsafe
        # 处理文件时，指定每次读写的数据量
        self.buffer_size = buffer_size
        # 内部的加密解密对象初始化，使用AES-128的CBC模式
        self.cipher = None
        # AES-128的CBC模式时，初始化向量字节(密钥偏移量)
        self._iv_bytes = None
        # 使用base64模块将初始化向量字节(密钥偏移量)由字节转换为字符串时的表现形式
        self._iv_str = iv_str

    # 生成加密解密对象，设置_iv_str和_iv_bytes
    # 加密和解密方法使用前，必须生成新的cipher，不然无法使用
    def gen_cipher(self):
        # 使用AES-128的CBC模式加密解密，_iv_bytes为None时，随机指定一个
        if self._iv_str:
            if self.use_urlsafe:
                self._iv_bytes = base64.urlsafe_b64decode(self._iv_str)
            else:
                self._iv_bytes = base64.b64decode(self._iv_str)
            cipher = AES.new(self.key, AES.MODE_CBC, self._iv_bytes)
        else:
            cipher = AES.new(self.key, AES.MODE_CBC)
            self._iv_bytes = cipher.iv
            if self.use_urlsafe:
                self._iv_str = base64.urlsafe_b64encode(self._iv_bytes).decode('utf-8')
            else:
                self._iv_str = base64.b64encode(self._iv_bytes).decode('utf-8')

        return cipher

    # 获得iv_str
    @property
    def iv_str(self):
        return self._iv_str


# 字符串加密解密类
class StringCrypto(BaseCrypto):
    def __init__(self, password, iv_str=DEFAULT_IV_STR):
        super().__init__(password, iv_str=iv_str, use_md5=True, use_urlsafe=True)

    # 加密字符串
    def encrypt(self, original_string):
        self.cipher = self.gen_cipher()
        # 将原字符串长度补齐到AES.block_size的整数倍长度
        pad_byte_string = pad(original_string.encode('utf-8'), AES.block_size)
        ct_bytes = self.cipher.encrypt(pad_byte_string)
        if self.use_urlsafe:
            encrypt_string = base64.urlsafe_b64encode(ct_bytes).decode('utf-8')
        else:
            encrypt_string = base64.b64encode(ct_bytes).decode('utf-8')
        return encrypt_string

    # 解密字符串
    def decrypt(self, encrypt_string):
        self.cipher = self.gen_cipher()
        if self.use_urlsafe:
            encrypt_byte_string = base64.urlsafe_b64decode(bytes(map(ord, encrypt_string)))
        else:
            encrypt_byte_string = base64.b64decode(bytes(map(ord, encrypt_string)))
        pad_byte_string = self.cipher.decrypt(encrypt_byte_string)
        original_string = unpad(pad_byte_string, AES.block_size).decode('utf-8')
        return original_string


# 将二进制数据加密或解密，返回二进制数据(一次性读入内存加密，用于小文件)
class ByteCrypto(BaseCrypto):
    def __init__(self, password, iv_str=DEFAULT_IV_STR):
        super().__init__(password, iv_str=iv_str, use_md5=True, use_urlsafe=True)

    def encrypt(self, original_data):
        self.cipher = self.gen_cipher()
        return self.cipher.encrypt(pad(original_data, AES.block_size))

    def decrypt(self, data_to_decrypt):
        self.cipher = self.gen_cipher()
        return unpad(self.cipher.decrypt(data_to_decrypt), AES.block_size)


# 将文件加密或解密，指定BUFFER_SIZE作为每次读取写入的字节数，用于大文件
class FileCrypto(BaseCrypto):
    def __init__(self, password, iv_str=DEFAULT_IV_STR):
        super().__init__(password, iv_str=iv_str, use_md5=True, use_urlsafe=True)
        # 加密解密的状态
        self.crypto_status = False
        # 已经读取的数据长度
        self.read_len = 0
        # 记录是否被外部中止
        self.stop_flag = False

    # 获取加密解密状态与已经读取的数据长度，用于显示状态
    def get_status(self):
        return self.crypto_status, self.read_len

    # 停止任务
    def stop_handle(self):
        self.crypto_status = False
        self.stop_flag = True

    # 是否被外部中止任务
    def if_stop(self):
        return self.stop_flag

    # 文件处理方法
    def handle(self, file_path, output_file_path, crypto_option):
        if not os.path.exists(file_path):
            raise ValueError('Input file path not exists: %s ', file_path)
        elif os.path.exists(output_file_path):
            raise ValueError('Output file exists: %s', output_file_path)

        file_len = os.path.getsize(file_path)
        self.crypto_status = True
        self.stop_flag = False
        # 设置加密或者解密
        self.cipher = self.gen_cipher()
        if crypto_option == "encrypt":
            data_handle_func = self.cipher.encrypt
            # 读取到文件尾部时，执行尾部补位操作后加密
            data_end_handle_func = lambda d: self.cipher.encrypt(pad(d, AES.block_size))
            with open(output_file_path, 'wb') as out:
                data_head = ByteCrypto(self.password, iv_str=self.iv_str).encrypt(ENCRYPT_MARK)
                out.write(data_head)
        elif crypto_option == "decrypt":
            data_handle_func = self.cipher.decrypt
            # 读取到文件尾部时，执行解密后尾部去除补位
            data_end_handle_func = lambda d: unpad(self.cipher.decrypt(d), AES.block_size)
        else:
            return

        try:
            with open(file_path, 'rb') as f:
                self.read_len = 0
                # 如果是解密模式，验证密码是否正确
                if crypto_option == "decrypt":
                    self.read_len += BLOCK_SIZE
                    head_data = f.read(BLOCK_SIZE)
                    if not verify_password(self.password, self.iv_str, head_data):
                        return
                # 进行加密或解密操作
                data_iter = iter(partial(f.read, self.buffer_size), b'')
                for data in data_iter:
                    if not self.crypto_status:
                        break
                    self.read_len += len(data)
                    if self.read_len == file_len:
                        data = data_end_handle_func(data)
                    else:
                        data = data_handle_func(data)
                    with open(output_file_path, 'ab') as out:
                        out.write(data)
        except Exception as e:
            raise e
        finally:
            self.crypto_status = False

    def encrypt(self, file_path, output_file_path):
        self.handle(file_path, output_file_path, "encrypt")

    def decrypt(self, file_path, output_file_path):
        self.handle(file_path, output_file_path, "decrypt")


# 文件夹加密解密类
class DirFileCrypto(object):
    def __init__(self, password, config_file=None, iv_str=DEFAULT_IV_STR):
        self._iv_str = iv_str
        # 用来保存文件名MD5值的字典的配置文件
        self.config_file = config_file
        # 用来保存文件名MD5值的字典
        self.file_name_md5_dict = {}
        # 将用password加密文件名和文件
        self.file_crypto = FileCrypto(password, iv_str)
        self.string_crypto = StringCrypto(password, iv_str)
        # 加密解密的状态
        self.crypto_status = False
        # 已经加密或解密的文件个数
        self.read_count = 0
        # 记录是否被外部中止
        self.stop_flag = False

    # 获得iv_str
    @property
    def iv_str(self):
        return self._iv_str

    # 获取加密解密状态与已经处理的文件个数，用于显示状态
    def get_status(self):
        return self.crypto_status, self.read_count

    # 停止任务
    def stop_handle(self):
        self.crypto_status = False
        self.stop_flag = True

    # 是否被外部中止任务
    def if_stop(self):
        return self.stop_flag

    # 将文件名替换成MD5值,并保存至字典中
    def file_name_encrypt(self, file_name):
        file_name_encrypt_str = self.string_crypto.encrypt(file_name)
        file_name_md5 = get_str_md5(file_name_encrypt_str)
        self.file_name_md5_dict[file_name_md5] = file_name_encrypt_str
        return file_name_md5

    # 读取MD5值对应的文件名
    def file_name_decrypt(self, file_name_md5):
        file_name_encrypt_str = self.file_name_md5_dict[file_name_md5]
        file_name = self.string_crypto.decrypt(file_name_encrypt_str)
        return file_name

    # 文件夹处理方法
    def dir_handle(self, input_dir, output_dir, file_handle_func, name_handle_func):
        real_input_dir = os.path.abspath(input_dir).replace('\\', '/')
        real_output_dir = os.path.abspath(output_dir).replace('\\', '/')
        if not os.path.exists(real_input_dir):
            raise ValueError('Input Dir not exists: %s', real_input_dir)

        if not os.path.exists(real_output_dir):
            os.mkdir(real_output_dir)

        root_parent_dir = os.path.split(real_input_dir)[0]
        root_dir = os.path.split(real_input_dir)[1]
        # 如果在磁盘根目录下，要把根目录后的‘/’计入长度
        root_dir_index = len(root_parent_dir) if root_parent_dir.endswith('/') else len(root_parent_dir) + 1
        real_output_subdir = os.path.join(real_output_dir, name_handle_func(root_dir))

        if not os.path.exists(real_output_subdir):
            os.mkdir(real_output_subdir)

        for path, subdir, files in os.walk(input_dir):

            # 将当前路径path转为加密后的文件夹路径now_output_path
            now_output_path = folder_path_convert(os.path.abspath(path)[root_dir_index:], name_handle_func)
            for d in subdir:
                real_output_subdir = os.path.join(real_output_dir, now_output_path, name_handle_func(d))
                if not os.path.exists(real_output_subdir):
                    os.mkdir(real_output_subdir)

            for f in files:
                if not self.crypto_status:
                    break
                input_file_path = os.path.join(os.path.abspath(path), f)
                output_file_path = os.path.join(real_output_dir, now_output_path, name_handle_func(f))
                file_handle_func(input_file_path, output_file_path)
                self.read_count += 1

    # 加密input_dir文件夹内的所有文件到output_dir
    # encrypt_name控制是否加密文件或文件夹名
    def encrypt(self, input_dir, output_dir, encrypt_name=True):
        self.crypto_status = True
        self.stop_flag = False
        self.read_count = 0
        if encrypt_name:
            self.dir_handle(input_dir, output_dir, self.file_crypto.encrypt, self.file_name_encrypt)
            # 保存文件名MD5值字典
            if not self.config_file:
                input_dir_name = os.path.basename(os.path.abspath(input_dir))
                encrypt_config_name = self.file_name_encrypt(input_dir_name) + ".json"
                self.config_file = os.path.join(os.path.dirname(os.path.abspath(input_dir)), encrypt_config_name)
            with open(self.config_file, "w") as f:
                json.dump(self.file_name_md5_dict, f)
        else:
            self.dir_handle(input_dir, output_dir, self.file_crypto.encrypt, lambda name: name)
        self.crypto_status = False

    # 解密input_dir文件夹内的所有文件到output_dir
    # decrypt_name控制是否加密文件或文件夹名
    def decrypt(self, input_dir, output_dir, decrypt_name=True):
        self.crypto_status = True
        self.stop_flag = False
        self.read_count = 0
        if decrypt_name:
            # 读取文件名MD5值字典
            if not self.config_file:
                input_dir_name = os.path.basename(os.path.abspath(input_dir))
                config_name = input_dir_name + ".json"
                self.config_file = os.path.join(os.path.dirname(os.path.abspath(input_dir)), config_name)
            with open(self.config_file, "r") as f:
                self.file_name_md5_dict = json.load(f)
            self.dir_handle(input_dir, output_dir, self.file_crypto.decrypt, self.file_name_decrypt)
        else:
            self.dir_handle(input_dir, output_dir, self.file_crypto.decrypt, lambda name: name)
        self.crypto_status = False


# 文件或文件夹列表加密解密类
class ListCrypto(DirFileCrypto):
    def __init__(self, password, config_file, iv_str=DEFAULT_IV_STR):
        super().__init__(password, config_file, iv_str)

    # 文件或文件夹列表处理
    def list_handle(self, input_list, output_dir, file_handle_func, name_handle_func):
        real_output_dir = os.path.abspath(output_dir).replace('\\', '/')
        if not os.path.exists(real_output_dir):
            os.mkdir(real_output_dir)

        for input_path in input_list:
            real_input = os.path.abspath(input_path).replace('\\', '/')

            if not os.path.exists(real_input):
                raise ValueError('Input Dir not exists: %s', real_input)

            if os.path.isfile(real_input):
                output_file_path = os.path.join(real_output_dir, name_handle_func(os.path.basename(real_input)))
                file_handle_func(real_input, output_file_path)
                self.read_count += 1
            elif os.path.isdir(real_input):
                self.dir_handle(real_input, real_output_dir, file_handle_func, name_handle_func)

    # 加密input_list内的所有文件或文件夹到output_dir
    # encrypt_name控制是否加密文件或文件夹名
    def encrypt(self, input_list, output_dir, encrypt_name=True):
        self.crypto_status = True
        self.stop_flag = False
        self.read_count = 0
        if encrypt_name:
            self.list_handle(input_list, output_dir, self.file_crypto.encrypt, self.file_name_encrypt)
            # 保存文件名MD5值字典
            with open(self.config_file, "w") as f:
                json.dump(self.file_name_md5_dict, f)
        else:
            self.list_handle(input_list, output_dir, self.file_crypto.encrypt, lambda name: name)
        self.crypto_status = False

    # 解密input_list内的所有文件或文件夹到output_dir
    # decrypt_name控制是否加密文件或文件夹名
    def decrypt(self, input_list, output_dir, decrypt_name=True):
        self.crypto_status = True
        self.stop_flag = False
        self.read_count = 0
        if decrypt_name:
            # 读取文件名MD5值字典
            with open(self.config_file, "r") as f:
                self.file_name_md5_dict = json.load(f)
            self.list_handle(input_list, output_dir, self.file_crypto.decrypt, self.file_name_decrypt)
        else:
            self.list_handle(input_list, output_dir, self.file_crypto.decrypt, lambda name: name)
        self.crypto_status = False
