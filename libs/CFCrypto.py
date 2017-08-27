import hashlib
import os
import base64
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad


# 字符串加密解密类
class StringCrypto(object):
    def __init__(self, password):
        # 将密码转为md5值作为密钥
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        self.key = md5.digest()
        # AES的ECB模式，数据的长度必须为16节的倍数
        self.multiple_of_byte = 16
        # 使用ECB模式进行加密解密
        self.cipher = AES.new(self.key, AES.MODE_ECB)

    # 加密字符串
    # 将字符串转为字节串进行AES加密，
    # 再将加密后的字节串转为16进制字符串，
    # 再通过base64模块编码
    def encrypt(self, string):
        pad_byte_string = pad(string.encode('utf-8'), self.multiple_of_byte)
        encrypt_byte_string = self.cipher.encrypt(pad_byte_string)
        encrypt_string = base64.urlsafe_b64encode(encrypt_byte_string).decode('ascii')
        return encrypt_string

    # 解密字符串
    # 步骤与加密相反
    def decrypt(self, encrypt_string):
        encrypt_byte_string = base64.urlsafe_b64decode(bytes(map(ord, encrypt_string)))
        pad_byte_string = self.cipher.decrypt(encrypt_byte_string)
        string = unpad(pad_byte_string, self.multiple_of_byte).decode('utf-8')
        return string


# 文件加密解密类
class FileCrypto(object):
    def __init__(self, password):
        # 将密码转为md5值作为密钥
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        self.key = md5.digest()
        # AES的ECB模式，数据的长度必须为16节的倍数
        self.multiple_of_byte = 16
        # 使用ECB模式进行加密解密
        self.cipher = AES.new(self.key, AES.MODE_ECB)
        # 设置加密解密时分块读取10240KB
        self.read_kb = 10240

    # 文件处理静态方法
    # 每次读取block_size字节的file_path
    # 每次读取后，正常是执行data_handle_func方法
    # 如遇到file_path结尾，则执行data_end_handle_func方法
    # 写入处理后的数据到output_file_path
    @staticmethod
    def handle(file_path, output_file_path, block_size, data_handle_func, data_end_handle_func):
        if not os.path.exists(file_path):
            raise ValueError('Input file path not exists: %s ', file_path)
        elif os.path.exists(output_file_path):
            raise ValueError('Output file exists: %s', output_file_path)

        file_len = os.path.getsize(file_path)
        with open(file_path, 'rb') as f:
            read = 0
            while True:
                data = f.read(block_size)
                if not data:
                    break
                read += len(data)
                if read == file_len:
                    data = data_end_handle_func(data)
                else:
                    data = data_handle_func(data)
                with open(output_file_path, 'ab') as out:
                    out.write(data)

    # 加密文件
    def encrypt(self, file_path, output_file_path):
        block_size = self.read_kb * 1024
        data_handle_func = self.cipher.encrypt
        # 读取到文件尾部时，执行尾部补位操作后加密
        data_end_handle_func = lambda d: self.cipher.encrypt(pad(d, self.multiple_of_byte))
        FileCrypto.handle(file_path, output_file_path, block_size, data_handle_func, data_end_handle_func)

    # 解密文件
    def decrypt(self, file_path, output_file_path):
        block_size = self.read_kb * 1024
        data_handle_func = self.cipher.decrypt
        # 读取到文件尾部时，执行解密后尾部去除补位
        data_end_handle_func = lambda d: unpad(self.cipher.decrypt(d), self.multiple_of_byte)
        FileCrypto.handle(file_path, output_file_path, block_size, data_handle_func, data_end_handle_func)


# 文件夹加密解密类
class DirFileCrypto(object):
    def __init__(self, password):
        # 将用password加密文件名和文件
        self.file_crypto = FileCrypto(password)
        self.string_crypto = StringCrypto(password)

    # 文件夹处理静态方法
    # 复制input_dir的目录结构（包含子目录结构）到output_dir中
    # 对input_dir中的所有文件（包含子目录中的文件）应用file_handle_func方法
    # 将处理后的文件存放到output_dir中
    @staticmethod
    def handle(input_dir, output_dir, file_handle_func):
        real_input_dir = os.path.abspath(input_dir).replace('\\', '/')
        real_output_dir = os.path.abspath(output_dir).replace('\\', '/')
        if not os.path.exists(real_input_dir):
            raise ValueError('Input Dir not exists: %s', real_input_dir)

        if not os.path.exists(real_output_dir):
            os.mkdir(real_output_dir)

        root_dir = os.path.split(real_input_dir)[0]
        # 如果在磁盘根目录下，要把根目录后的‘/’计入长度
        root_dir_index = len(root_dir) if root_dir.endswith('/') else len(root_dir) + 1
        real_output_subdir = os.path.join(real_output_dir, real_input_dir[root_dir_index:])

        if not os.path.exists(real_output_subdir):
            os.mkdir(real_output_subdir)

        for path, subdir, files in os.walk(input_dir):

            for d in subdir:
                real_output_subdir = os.path.join(real_output_dir, os.path.abspath(path)[root_dir_index:], d)
                if not os.path.exists(real_output_subdir):
                    os.mkdir(real_output_subdir)

            for f in files:
                input_file_path = os.path.join(os.path.abspath(path), f)
                output_file_path = os.path.join(real_output_dir, os.path.abspath(path)[root_dir_index:], f)
                file_handle_func(input_file_path, output_file_path)

    # 加密input_dir文件夹内的所有文件到output_dir
    def encrypt(self, input_dir, output_dir):
        DirFileCrypto.handle(input_dir, output_dir, self.file_crypto.encrypt)

    # 解密input_dir文件夹内的所有文件到output_dir
    def decrypt(self, input_dir, output_dir):
        DirFileCrypto.handle(input_dir, output_dir, self.file_crypto.decrypt)


# 文件夹名称加密解密类
class DirNameCrypto(object):
    def __init__(self, password):
        # 将用password加密文件夹名
        self.string_crypto = StringCrypto(password)

    # 修改文件夹名称的静态方法
    @staticmethod
    def handle(f_path, handle_func):
        os.chdir(f_path)
        for item in os.listdir(f_path):
            if os.path.isdir(item):
                DirNameCrypto.handle(os.path.join(os.getcwd(), item), handle_func)
                os.chdir('..')
                dir_name = handle_func(item)
                if dir_name is not None:
                    os.rename(item, dir_name)
            elif os.path.isfile(item):
                file_name = handle_func(item)
                if file_name is not None:
                    os.rename(item, file_name)

    # 加密文件夹名称
    def encrypt(self, dir_path):
        if not os.path.exists(dir_path):
            raise ValueError('Dir not exists: %s', dir_path)
        root_path = os.path.abspath('.')
        dir_path = os.path.abspath(dir_path)
        DirNameCrypto.handle(dir_path, self.string_crypto.encrypt)
        dir_name = self.string_crypto.encrypt(os.path.split(dir_path)[1])
        os.chdir(os.path.split(dir_path)[0])
        os.rename(os.path.split(dir_path)[1], dir_name)
        os.chdir(root_path)

    # 解密文件夹名称
    def decrypt(self, dir_path):
        if not os.path.exists(dir_path):
            raise ValueError('Dir not exists: %s', dir_path)
        root_path = os.path.abspath('.')
        dir_path = os.path.abspath(dir_path)
        DirNameCrypto.handle(dir_path, self.string_crypto.decrypt)
        dir_name = self.string_crypto.decrypt(os.path.split(dir_path)[1])
        os.chdir(os.path.split(dir_path)[0])
        os.rename(os.path.split(dir_path)[1], dir_name)
        os.chdir(root_path)


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
