import re

from functions.custom.pms_crypt import PMSCrypt
from functions.custom.aes_crypt import AESCrypt
from functions.custom.des_crypt import DESCrypt, DES3Crypt
from urllib.parse import quote_plus, unquote_plus, quote, unquote
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_v1_5
import base64


#PMS加密gizp压缩并进行base64编码
def pms_encode_to_b64(string='', key='', iv='', mode=''):
    obj = PMSCrypt()
    pms_str = obj.pms_encode(string)
    return pms_str

#PMS加密gizp压缩并进行base64编码对应解密方法
def pms_decode_to_b64(string='', key='', iv='', mode=''):
    obj = PMSCrypt()
    pms_str = obj.pms_decode(string)
    return pms_str

# content = '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'
# a = pms_decode_to_b64(content)
# #print(a)
# b = pms_encode_to_b64(a)
# print(b)

# AES加密并编码成字符串
def aes_encode_to_string(string='', key='', iv='', mode='ECB'):
    obj = AESCrypt(key=key, iv=iv, mode=mode)
    aes_str = obj.aes_encode(string)
    return obj.byte_to_string(aes_str)


# AES加密并编码成字符串对应解密方法
def aes_decode_from_string(string='', key='', iv='', mode='ECB'):
    obj = AESCrypt(key=key, iv=iv, mode=mode)
    aes_str = obj.string_to_byte(string)
    return obj.aes_decode(aes_str)


# AES加密并进行base64编码
def aes_encode_to_b64(string='', key='', iv='', mode='CBC'):
    obj = AESCrypt(key=key, iv=iv, mode=mode)
    aes_str = obj.aes_encode(string)
    return base64.b64encode(aes_str).decode('utf8', errors='ignore')


# AES加密并进行base64编码对应解密方法
def aes_decode_from_b64(string='', key='', iv='', mode='CBC'):
    obj = AESCrypt(key=key, iv=iv, mode=mode)
    # print('123',type(string),string)
    return obj.aes_decode(string)


# AES加密并进行base64编码后再URLEncode
def aes_encode_to_b64_url_encode(string='', key='', iv='', mode='CBC'):
    obj = AESCrypt(key, iv, mode)
    aes_str = obj.aes_encode(string)
    #return quote_plus(base64.b64encode(aes_str,'-_'))
    return base64.b64encode(aes_str).decode('utf8', errors='ignore')


# AES加密并进行base64编码后再URLEncode对应解密方法
def aes_decode_from_b64_url_encode(string='', key='', iv='', mode='CBC'):
    obj = AESCrypt(key=key, iv=iv, mode=mode)
    aes_str = base64.b64decode(string,'-_')
    return obj.aes_decode(aes_str)


# DES加密并进行base64编码
def des_encode_to_b64(string='', key='', iv='', mode='ECB'):
    obj = DESCrypt(key=key, iv=iv, mode=mode)
    des_str = obj.des_encode(string)
    return base64.b64encode(des_str).decode('utf8', errors='ignore')


# DES加密并进行base64编码对应解密方法
def des_decode_from_b64(string='', key='', iv='', mode='ECB'):
    obj = DESCrypt(key=key, iv=iv, mode=mode)
    des_str = base64.b64decode(string)
    return obj.des_decode(des_str)


# DES加密并进行base64编码后再URLEncode
def des_encode_to_b64_url_encode(string='', key='', iv='', mode='ECB'):
    obj = DESCrypt(key=key, iv=iv, mode=mode)
    des_str = obj.des_encode(string)
    return quote(base64.b64encode(des_str))


# DES加密并进行base64编码后再URLEncode对应解密方法
def des_decode_from_b64_url_encode(string='', key='', iv='', mode='ECB'):
    obj = DESCrypt(key=key, iv=iv, mode=mode)
    des_str = base64.b64decode(unquote(string))
    return obj.des_decode(des_str)


# DES3加密并进行base64编码
def des3_encode_to_b64(string='', key='', iv='', mode='ECB'):
    obj = DES3Crypt(key=key, iv=iv, mode=mode)
    des3_str = obj.des3_encode(string)
    return base64.b64encode(des3_str).decode('utf8', errors='ignore')


# DES3加密并进行base64编码对应解密方法
def des3_decode_from_b64(string='', key='', iv='', mode='ECB'):
    obj = DES3Crypt(key=key, iv=iv, mode=mode)
    des3_str = base64.b64decode(string)
    return obj.des3_decode(des3_str)


# DES3加密并进行base64编码后再URLEncode
def des3_encode_to_b64_url_encode(string='', key='', iv='', mode='ECB'):
    obj = DES3Crypt(key=key, iv=iv, mode=mode)
    des3_str = obj.des3_encode(string)
    return quote(base64.b64encode(des3_str))


# DES3加密并进行base64编码后再URLEncode对应解密方法
def des3_decode_from_b64_url_encode(string='', key='', iv='', mode='ECB'):
    obj = DES3Crypt(key=key, iv=iv, mode=mode)
    des3_str = base64.b64decode(unquote(string))
    return obj.des3_decode(des3_str)


# RSA加密并进行base64编码
def rsa_encode_to_b64(string='', key='../static/jushi_pub.key', iv='', mode='200'):
    with open(key, 'r') as pub_file:
        pub_key = PKCS1_v1_5.new(RSA.importKey(pub_file.read()))
    res = []
    for i in range(0, len(string), int(mode)):
        res.append(pub_key.encrypt(string[i:i+int(mode)].encode('utf8', errors='ignore')))
    return base64.b64encode(b"".join(res)).decode('utf8', errors='ignore')


# RSA加密并进行base64编码对应解密方法
def rsa_decode_from_b64(string='', key='../static/pri_6615126990652570.key', iv='', mode='256'):
    with open(key, 'r') as pvt_file:
        pvt_key = PKCS1_v1_5.new(RSA.importKey(pvt_file.read()))
    res = []
    string = base64.b64decode(string)
    for i in range(0, len(string), int(mode)):
        res.append(pvt_key.decrypt(string[i:i+int(mode)], 'xyz'))
    text = b"".join(res)
    return text if isinstance(text, str) else text.decode('utf8', errors='ignore')


str = '{"RQModel_CheckInfo":[{"Identity":"18611625312","ArrDate":"2020-02-26","DptDate":"2020-03-04","Status":"1","SearchFlg":"3","SearchMainAcct":"False","SearchLockFlag":"False"}],"grpcd":"lc","htlcd":"lc01","staffcd":"9897","token":"52138214DD7DC7A80073B3C2CF3D2AD5F0841C16","staffpassword":"sunwood","isformal":"True","mac":"6C-0B-84-08-06-78"}'
key = 'cloudwisdomadjsn'
iv = '5721678222017913'
mode = 'CBC'
# e = aes_encode_to_b64_url_encode(str,key,iv,mode=mode)
# b1 = "lUbG2pkZMLJUjp4bNDtZzkZf3TWB4KmZjISMjsSN53vWH2bjpt5N1TJQx0bGFGU/FvgCW9i+aoEq7yqgoJa4D/7pWXV+s4orpeunmsKA5PPyAWmt6PjveeNwQUh7mIrSd6Dejuyjx3T/N6XqRUS3PQssbpKT/shGPEdFtMfJQzprU/zD0cyeOePocQ4g6eKj"
# b = '<?xml version="1.0" encoding="utf-8"?> <string xmlns="http://tempuri.org/">lUbG2pkZMLJUjp4bNDtZzkZf3TWB4KmZjISMjsSN53vWH2bjpt5N1TJQx0bGFGU/FvgCW9i+aoEq7yqgoJa4D/7pWXV+s4orpeunmsKA5PPyAWmt6PjveeNwQUh7mIrSd6Dejuyjx3T/N6XqRUS3PQssbpKT/shGPEdFtMfJQzprU/zD0cyeOePocQ4g6eKj</string>'
# d = aes_decode_from_b64_url_encode(b1,key,iv,mode=mode)
#
# print(type(b1))
# print("加密:", type(e),e)
# print("解密:", d)
