import hashlib
import random

LOW_LEVEL = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

MEDIUM_LEVEL = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

HIGH_LEVEL = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
              'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
              'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
              'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
              '!', '@', '#', '$', '%', '^', '&', '*', '-', '_', '=',
              '+', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']


# 根据密码长度与复杂度，生成随机密码
def generate_password(length, level):
    return ''.join([random.choice(level) for i in range(0, length)])


# b'\0'填充密码
def null_pad(data_to_pad):
    data_len = len(data_to_pad)
    # 不超过128位的密码填充长度（字节单位）
    if data_len <= 16:
        key_len = 16
    # 128位以上，不超过192位的密码填充长度（字节单位）
    elif 16 < data_len <= 24:
        key_len = 24
    # 192位以上，不超过256位的密码填充长度（字节单位）
    elif 24 < data_len <= 32:
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
    password = password + salt if salt else password
    # use_md5为True值时，将密码转为md5值作为密钥，否则使用b'\0'填充密码
    if use_md5:
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        key = md5.digest()
    else:
        key = null_pad(password.encode('utf-8'))

    return key
