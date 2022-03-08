from functions.custom.crypt_func import *
from functions.custom.sign_func import *

# 加密算法配置
encrypt = [{'name': 'AES(CBC)_TO_base64', 'function': aes_encode_to_b64, 'mode': 'CBC',
            'comment': 'AES加密并进行base64编码, CBC模式'},
           {'name': 'PMS__TO_base64', 'function': pms_encode_to_b64,
            'mode': '', 'comment': 'PMS加密gizp压缩并进行base64编码'}]

# 解密算法配置
decrypt = [{'name': 'AES(CBC)_FROM_base64', 'function': aes_decode_from_b64, 'mode': 'CBC',
            'comment': 'AES加密并进行base64编码对应解密方法, CBC模式'},
           {'name': 'PMS_FROM_base64', 'function': pms_decode_to_b64,
            'mode': '', 'comment': 'PMS加密gizp压缩并进行base64编码对应解密方法'}]

# 自定义方法配置
customs_func = [{'name': 'public_md5_sign_one', 'function': public_md5_sign_one, 'comment': '通用加签方式一, 格式: p1v1p2p2p3v3signKey'},
                {'name': 'public_md5_sign_two', 'function': public_md5_sign_two, 'comment': '通用加签方式二, 格式: signKeyp1v1p2p2p3v3'},
                {'name': 'public_md5_sign_three', 'function': public_md5_sign_three, 'comment': '通用加签方式三, 格式: signKeyp1v1p2p2p3v3signKey'}]
