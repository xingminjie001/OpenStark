import json
from Cryptodome.Hash import MD5
from urllib.parse import quote_plus


"""
签名方法函数格式:
def 方法名(接口请求内容接收变量"body", 项目自定义参数接收变量"params", 项目相关加密方法接收变量"encrypt"):
    方法过程
"""

# 通用加签方式一, 格式: p1v1p2p2p3v3signKey
def public_md5_sign_one(body, params, encrypt):
    if not isinstance(body, dict):
        return ''
    signKey = ''
    for param in params:
        if param['name'] == 'signKey':
            signKey = param['value']
    body.pop('sign')
    s = ''
    for k in sorted(body):
        s += '%s%s' % (k, body[k])
    s += signKey
    t = MD5.new()
    t.update(b'%s' % s.encode('utf8', errors='ignore'))
    return t.hexdigest()


# 通用加签方式二, 格式: signKeyp1v1p2p2p3v3
def public_md5_sign_two(body, params, encrypt):
    if not isinstance(body, dict):
        return ''
    signKey = ''
    for param in params:
        if param['name'] == 'signKey':
            signKey = param['value']
    body.pop('sign')
    s = signKey
    for k in sorted(body):
        s += '%s%s' % (k, body[k])
    t = MD5.new()
    t.update(b'%s' % s.encode('utf8', errors='ignore'))
    return t.hexdigest()


# 通用加签方式三, 格式: signKeyp1v1p2p2p3v3signKey
def public_md5_sign_three(body, params, encrypt):
    if not isinstance(body, dict):
        return ''
    signKey = ''
    for param in params:
        if param['name'] == 'signKey':
            signKey = param['value']
    body.pop('sign')
    s = signKey
    for k in sorted(body):
        s += '%s%s' % (k, body[k])
    s += signKey
    t = MD5.new()
    t.update(b'%s' % s.encode('utf8', errors='ignore'))
    return t.hexdigest()
