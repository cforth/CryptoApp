# CryptoApp 简介

###### E-mail:cforth@cfxyz.com

一个简单的加密解密工具箱GUI程序，使用Python3实现。包含以下几个小工具，可通过选项菜单进行切换。

## 安装需要

* Python
    * Python 3.6
    * pycryptodome 3.4.6+
    * chardet 3.0.4
    * Pillow 5.0.0
* Windows(32位/64位)
    * Windows XP及以上
* Linux
    * python3-tk

## 模块介绍

* Cryptor--加密解密器
   * 支持加密字符串、文件、文件夹，可以预览加密或解密后的文件名称。

* ImgLook--图片查看器
   * 支持常见图片格式（包括GIF动图）的显示，并且支持读取使用CFCrypto加密过的图片。

* RandomPassword--随机密码生成器
   * 指定密码长度和复杂度，生成随机密码。

* FileSplit--文件分割合并器
   * 可以将大文件分割，或者将分割后的文件合并。

* MD5Generate--文件MD5值生成器
   * 生成文件的MD5校验值。

## 使用方法

```bash
python3 CryptoApp.pyw
```
