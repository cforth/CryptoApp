import hashlib
import os
import base64
import re
from functools import partial
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
import logging
import json


# '\0'填充密码
def null_pad(data_to_pad):
    data_len = len(data_to_pad)
    # 不超过128位的密码填充长度（字节单位）
    if data_len <= 16:
        key_len = 16
    # 128位以上，不超过192位的密码填充长度（字节单位）
    elif data_len > 16 and data_len <= 24:
        key_len = 24
    # 192位以上，不超过256位的密码填充长度（字节单位）
    elif data_len > 24 and data_len <= 32:
        key_len = 32
    # 超过256位的密码直接截断到256位长度
    else:
        return data_to_pad[:32]
    # 进行'\0'填充
    padding_len = key_len - len(data_to_pad)
    padding = b'\0' * padding_len
    return data_to_pad + padding


# 生成密钥
def gen_aes_key(password, salt, use_md5):
    # 将密码加盐，防止泄露原始密码
    if salt:
        password += salt

    if use_md5:
        # 将密码转为md5值作为密钥
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        key = md5.digest()
    else:
        key = null_pad(password.encode('utf-8'))

    return key


# 字符串加密解密类
class StringCrypto(object):
    def __init__(self, password, salt="", use_md5=True, use_urlsafe=True):
        # AES的ECB模式，数据的长度必须为16字节的倍数
        self.multiple_of_byte = 16
        self.use_urlsafe = use_urlsafe
        # 生成密钥时，选择是否加盐，是否使用md5值
        self.key = gen_aes_key(password, salt, use_md5)
        # 使用ECB模式进行加密解密
        self.cipher = AES.new(self.key, AES.MODE_ECB)

    # 加密字符串
    def encrypt(self, string):
        pad_byte_string = pad(string.encode('utf-8'), self.multiple_of_byte)
        encrypt_byte_string = self.cipher.encrypt(pad_byte_string)
        if self.use_urlsafe:
            encrypt_string = base64.urlsafe_b64encode(encrypt_byte_string).decode('ascii')
        else:
            encrypt_string = base64.b64encode(encrypt_byte_string).decode('ascii')
        return encrypt_string

    # 解密字符串
    def decrypt(self, encrypt_string):
        if self.use_urlsafe:
            encrypt_byte_string = base64.urlsafe_b64decode(bytes(map(ord, encrypt_string)))
        else:
            encrypt_byte_string = base64.b64decode(bytes(map(ord, encrypt_string)))
        pad_byte_string = self.cipher.decrypt(encrypt_byte_string)
        string = unpad(pad_byte_string, self.multiple_of_byte).decode('utf-8')
        return string


# 将文件加密或解密，返回二进制数据(用于小文件)
class ByteCrypto:
    def __init__(self, password, salt="", use_md5=True):
        # 生成密钥时，选择是否加盐，是否使用md5值
        self.key = gen_aes_key(password, salt, use_md5)
        # AES的ECB模式，数据的长度必须为16字节的倍数
        self.multiple_of_byte = 16
        # 使用ECB模式进行加密解密
        self.cipher = AES.new(self.key, AES.MODE_ECB)

    def encrypt(self, file_path):
        if not os.path.exists(file_path):
            raise ValueError('Input file path not exists: %s ', file_path)

        with open(file_path, 'rb') as f:
            data_to_encrypt = f.read()
        return self.cipher.encrypt(pad(data_to_encrypt, self.multiple_of_byte))

    def decrypt(self, file_path):
        if not os.path.exists(file_path):
            raise ValueError('Input file path not exists: %s ', file_path)

        with open(file_path, 'rb') as f:
            data_to_decrypt = f.read()
        return unpad(self.cipher.decrypt(data_to_decrypt), self.multiple_of_byte)


# 将二进制数据加密或解密，返回二进制数据(用于小文件)
class BinaryDataCrypto:
    def __init__(self, password, salt="", use_md5=True):
        # 生成密钥时，选择是否加盐，是否使用md5值
        self.key = gen_aes_key(password, salt, use_md5)
        # AES的ECB模式，数据的长度必须为16字节的倍数
        self.multiple_of_byte = 16
        # 使用ECB模式进行加密解密
        self.cipher = AES.new(self.key, AES.MODE_ECB)

    def encrypt(self, data_to_encrypt):
        return self.cipher.encrypt(pad(data_to_encrypt, self.multiple_of_byte))

    def decrypt(self, data_to_decrypt):
        return unpad(self.cipher.decrypt(data_to_decrypt), self.multiple_of_byte)


# 文件加密解密类
class FileCrypto(object):
    def __init__(self, password, salt="", use_md5=True, block_size=10 * 1024 * 1024):
        # 生成密钥时，选择是否加盐，是否使用md5值
        self.key = gen_aes_key(password, salt, use_md5)
        # AES的ECB模式，数据的长度必须为16节的倍数
        self.multiple_of_byte = 16
        # 使用ECB模式进行加密解密
        self.cipher = AES.new(self.key, AES.MODE_ECB)
        # 设置加密解密时分块读取10MB
        self.block_size = block_size
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
    def handle(self, file_path, output_file_path, data_handle_func, data_end_handle_func):
        if not os.path.exists(file_path):
            raise ValueError('Input file path not exists: %s ', file_path)
        elif os.path.exists(output_file_path):
            raise ValueError('Output file exists: %s', output_file_path)

        file_len = os.path.getsize(file_path)
        self.crypto_status = True
        self.stop_flag = False
        try:
            with open(file_path, 'rb') as f:
                self.read_len = 0
                data_iter = iter(partial(f.read, self.block_size), b'')
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

    # 加密文件
    def encrypt(self, file_path, output_file_path):
        data_handle_func = self.cipher.encrypt
        # 读取到文件尾部时，执行尾部补位操作后加密
        data_end_handle_func = lambda d: self.cipher.encrypt(pad(d, self.multiple_of_byte))
        self.handle(file_path, output_file_path, data_handle_func, data_end_handle_func)

    # 解密文件
    def decrypt(self, file_path, output_file_path):
        data_handle_func = self.cipher.decrypt
        # 读取到文件尾部时，执行解密后尾部去除补位
        data_end_handle_func = lambda d: unpad(self.cipher.decrypt(d), self.multiple_of_byte)
        self.handle(file_path, output_file_path, data_handle_func, data_end_handle_func)


# 文件夹加密解密类
class DirFileCrypto(object):
    def __init__(self, password):
        # 将用password加密文件名和文件
        self.file_crypto = FileCrypto(password)
        self.string_crypto = StringCrypto(password)
        # 加密解密的状态
        self.crypto_status = False
        # 已经加密或解密的文件个数
        self.read_count = 0
        # 记录是否被外部中止
        self.stop_flag = False

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

    # 路径加密解密静态方法
    @staticmethod
    def dir_path_handle(path_string, name_handle_func):
        name_list = re.split(r'[\\/]', path_string)
        crypto_list = [name_handle_func(s) for s in name_list]
        return '/'.join(crypto_list)

    # 文件夹处理方法
    def handle(self, input_dir, output_dir, file_handle_func, name_handle_func):
        real_input_dir = os.path.abspath(input_dir).replace('\\', '/')
        real_output_dir = os.path.abspath(output_dir).replace('\\', '/')
        if not os.path.exists(real_input_dir):
            raise ValueError('Input Dir not exists: %s', real_input_dir)

        if not os.path.exists(real_output_dir):
            os.mkdir(real_output_dir)

        self.crypto_status = True
        self.stop_flag = False
        self.read_count = 0
        root_parent_dir = os.path.split(real_input_dir)[0]
        root_dir = os.path.split(real_input_dir)[1]
        # 如果在磁盘根目录下，要把根目录后的‘/’计入长度
        root_dir_index = len(root_parent_dir) if root_parent_dir.endswith('/') else len(root_parent_dir) + 1
        real_output_subdir = os.path.join(real_output_dir, name_handle_func(root_dir)).replace('\\', '/')

        if not os.path.exists(real_output_subdir):
            os.mkdir(real_output_subdir)

        for path, subdir, files in os.walk(real_input_dir):

            # 将当前路径path转为加密后的文件夹路径now_output_path
            now_output_path = DirFileCrypto.dir_path_handle(os.path.abspath(path)[root_dir_index:], name_handle_func)
            for d in subdir:
                real_output_subdir = os.path.join(real_output_dir, now_output_path, name_handle_func(d)).replace('\\', '/')
                if not os.path.exists(real_output_subdir):
                    os.mkdir(real_output_subdir)

            for f in files:
                if not self.crypto_status:
                    break
                input_file_path = os.path.join(os.path.abspath(path), f).replace('\\', '/')
                output_file_path = os.path.join(real_output_dir, now_output_path, name_handle_func(f)).replace('\\', '/')
                try:
                    file_handle_func(input_file_path, output_file_path)
                except Exception as e:
                    logging.exception(e)
                self.read_count += 1

        self.crypto_status = False

    # 加密input_dir文件夹内的所有文件到output_dir
    # encrypt_name控制是否加密文件或文件夹名
    def encrypt(self, input_dir, output_dir, encrypt_name=True):
        if encrypt_name:
            self.handle(input_dir, output_dir, self.file_crypto.encrypt, self.string_crypto.encrypt)
        else:
            self.handle(input_dir, output_dir, self.file_crypto.encrypt, lambda name: name)

    # 解密input_dir文件夹内的所有文件到output_dir
    # decrypt_name控制是否加密文件或文件夹名
    def decrypt(self, input_dir, output_dir, decrypt_name=True):
        if decrypt_name:
            self.handle(input_dir, output_dir, self.file_crypto.decrypt, self.string_crypto.decrypt)
        else:
            self.handle(input_dir, output_dir, self.file_crypto.decrypt, lambda name: name)


# RSA加密解密类
class RSACrypto(object):
    def __init__(self):
        self.code = None
        self.private_key_path = None
        self.public_key_path = None

    # 设置私钥密码
    def set_password(self, password):
        self.code = password

    # 设置私钥文件的路径
    def set_private_key_path(self, private_key_path):
        self.private_key_path = private_key_path

    # 设置公钥文件的路径
    def set_public_key_path(self, public_key_path):
        self.public_key_path = public_key_path

    # 根据私钥密码生成私钥和公钥
    def generate_key(self):
        if not self.code:
            print('Please set password first!')
        elif not self.private_key_path:
            print('Please set private_key_path!')
        elif not self.public_key_path:
            print('Please set public_key_path!')
        else:
            key = RSA.generate(2048)
            encrypted_key = key.exportKey(passphrase=self.code, pkcs=8,
                                          protection="scryptAndAES128-CBC")
            with open(self.private_key_path, 'wb') as f:
                f.write(encrypted_key)
            with open(self.public_key_path, 'wb') as f:
                f.write(key.publickey().exportKey())

    # 加密文件，需要设置公钥文件
    def encrypt(self, file_path, output_file_path):
        if not self.public_key_path:
            print('Please set public_key_path!')
        else:
            with open(output_file_path, 'wb') as out_file:
                public_file = open(self.public_key_path)
                recipient_key = RSA.import_key(
                    public_file.read())
                session_key = get_random_bytes(16)
                cipher_rsa = PKCS1_OAEP.new(recipient_key)
                out_file.write(cipher_rsa.encrypt(session_key))
                cipher_aes = AES.new(session_key, AES.MODE_EAX)
                public_file.close()
                with open(file_path, 'rb') as f:
                    data = f.read()
                cipher_text, tag = cipher_aes.encrypt_and_digest(data)
                out_file.write(cipher_aes.nonce)
                out_file.write(tag)
                out_file.write(cipher_text)

    # 解密文件，需要设置私钥密码和私钥文件
    def decrypt(self, file_path, output_file_path):
        if not self.code:
            print('Please set password first!')
        elif not self.private_key_path:
            print('Please set private_key_path!')
        else:
            with open(file_path, 'rb') as file:
                private_file = open(self.private_key_path)
                private_key = RSA.import_key(
                    private_file.read(),
                    passphrase=self.code)
                enc_session_key, nonce, tag, cipher_text = [file.read(x)
                                                            for x in (private_key.size_in_bytes(), 16, 16, -1)]
                cipher_rsa = PKCS1_OAEP.new(private_key)
                session_key = cipher_rsa.decrypt(enc_session_key)
                cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
                data = cipher_aes.decrypt_and_verify(cipher_text, tag)
                private_file.close()
            with open(output_file_path, 'wb') as f:
                f.write(data)


# 文件夹名称加密解密类
class DirNameCrypto(object):
    def __init__(self, password, config_file=None):
        self.string_crypto = StringCrypto(password)
        # 用来保存文件名MD5值的字典的配置文件
        self.config_file = config_file
        # 用来保存文件名MD5值的字典
        self.file_name_md5_dict = {}

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
    @staticmethod
    def dir_handle(input_dir, name_handle_func):
        real_input_dir = os.path.abspath(input_dir).replace('\\', '/')
        if not os.path.exists(real_input_dir):
            raise ValueError('Input Dir not exists: %s', real_input_dir)
        for path, subdir, files in os.walk(input_dir, topdown=False):
            for d in subdir:
                original_dir = os.path.join(os.path.abspath(path), d)
                try:
                    rename_dir = os.path.join(os.path.abspath(path), name_handle_func(d))
                    os.rename(original_dir, rename_dir)
                except Exception as e:
                    logging.exception(e)
            for f in files:
                original_file = os.path.join(os.path.abspath(path), f)
                try:
                    rename_file = os.path.join(os.path.abspath(path), name_handle_func(f))
                    os.rename(original_file, rename_file)
                except Exception as e:
                    logging.exception(e)

    def encrypt(self, input_dir):
        DirNameCrypto.dir_handle(input_dir, self.file_name_encrypt)
        # 保存文件名MD5值字典
        if not self.config_file:
            input_dir_name = os.path.basename(os.path.abspath(input_dir))
            encrypt_config_name = self.file_name_encrypt(input_dir_name) + ".json"
            self.config_file = os.path.join(os.path.dirname(os.path.abspath(input_dir)), encrypt_config_name)
        with open(self.config_file, "w") as f:
            json.dump(self.file_name_md5_dict, f)

    def decrypt(self, input_dir):
        # 读取文件名MD5值字典
        if not self.config_file:
            input_dir_name = os.path.basename(os.path.abspath(input_dir))
            encrypt_config_name = self.file_name_encrypt(input_dir_name) + ".json"
            self.config_file = os.path.join(os.path.dirname(os.path.abspath(input_dir)), encrypt_config_name)
        with open(self.config_file, "r") as f:
            self.file_name_md5_dict = json.load(f)
        DirNameCrypto.dir_handle(input_dir, self.file_name_decrypt)


# 文件MD5值生成
def get_file_md5(filename):
    if not os.path.isfile(filename):
        return

    my_hash = hashlib.md5()
    with open(filename, 'rb') as f:
        while True:
            b = f.read(8096)
            if not b:
                break
            my_hash.update(b)

    return my_hash.hexdigest()


# 字符串MD5生成
def get_str_md5(string):
    my_hash = hashlib.md5()
    my_hash.update(string.encode('utf-8'))
    return my_hash.hexdigest()

