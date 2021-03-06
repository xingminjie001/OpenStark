from Cryptodome.Hash import MD5
from tornado.log import app_log as log
from urllib.parse import urlsplit, unquote_plus
from munch import munchify
import re
import json
import ast
import time
import random


class CommonFunction(object):
    # 对用户密码进行加密
    def encode_password(self, password):
        obj = MD5.new()
        obj.update(password.encode('utf8', errors='ignore') * 3)
        data = obj.hexdigest()
        data = self.__encode_md5(data.encode('utf8', errors='ignore'))
        obj.update(data)
        return obj.hexdigest()

    def __encode_md5(self, md5_string):
        md5_string = bytearray(md5_string)
        buf = bytearray()
        for i in range(len(md5_string)):
            buf.append(((md5_string[i] >> 4) & 0xF) + ord('a'))
            buf.append((md5_string[i] & 0xF) + ord('a'))
        return bytes(buf)

    # 字符串类型及合法性检查
    def check_string(self, string, str_type='email'):
        if str_type == 'email':
            if re.match(r'^[a-zA-Z\d][\w-]+@[\w-]+(\.[a-zA-Z]+)*$', string) is not None:
                return True
            else:
                log.warning('email {} 格式校验不通过'.format(string))
                return False
        elif str_type == 'username':
            if re.match(b'\w*[\x80-\xff]+\w*', string.encode('utf8', errors='ignore')) is not None:
                return False
            elif re.match(r'^[a-zA-Z]\w{1,19}$', string) is not None:
                return True
            else:
                log.warning('username {} 格式校验不通过'.format(string))
                return False
        elif str_type == 'realname':
            if re.match(b'^[\x80-\xff]{6,60}$', string.encode('utf8', errors='ignore')) is not None:
                return True
            else:
                log.warning('realname {} 格式校验不通过'.format(string))
                return False
        elif str_type == 'password':
            if re.match(r'^\S.{5,20}$', string) is not None:
                return True
            else:
                log.warning('password格式校验不通过')
                return False
        elif str_type == 'url':
            if re.match(r'^https?://[\w-]+\.[\w.:/-]+([?\w=&#-]+)[^-_.]$', string) is not None:
                return True
            else:
                log.warning('url {} 格式校验不通过'.format(string))
                return False
        elif str_type == 'ip':
            if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', string) is not None:
                return True
            else:
                log.warning('ip {} 格式校验不通过'.format(string))
                return False
        elif str_type == 'host':
            if re.match(r'^([^http://]|[^https://])[\w-]*\.[\w.-]+[^-_.]$', string) is not None:
                return True
            else:
                log.warning('host {} 格式校验不通过'.format(string))
                return False
        elif str_type == 'json':
            if re.match(r'^\{.*\}$', string) is not None:
                try:
                    json.loads(string)
                    return True
                except Exception as e:
                    log.error(e)
                    log.warning('json {} 格式校验不通过'.format(string))
                return False
            else:
                return False
        elif str_type == 'datetime':
            if re.match(r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}$', string) is not None:
                return True
            else:
                log.warning('datetime {} 格式校验不通过'.format(string))
                return False
        elif str_type == 'check_key':
            if re.match(r'^\w+=\d\|(int|float|num|str|/.*/|date|time|datetime|list|dict)$',
                        string.strip()) is None and re.match(
                        r'^(\w+|\[\d+\])(\.\w+|\.\[\d+\])*\.\[\w+=\d\|('
                        r'int|float|num|str|/.*/|date|time|datetime|list|dict)('
                        r',\w+=\d\|(int|float|num|str|/.*/|date|time|datetime|list|dict))*\]$', string.strip()
            ) is None:
                log.warning('check_key {} 格式校验不通过'.format(string))
                return False
            else:
                return True
        else:
            return False

    # 切割URL
    def url_split(self, url):
        urls = urlsplit(url)
        url = urls.netloc.split(sep=':', maxsplit=1)
        if len(url) == 2:
            port = url[1]
        else:
            if urls.scheme == 'https':
                port = 443
            else:
                port = 80
        host = url[0]
        urls = {'scheme': urls.scheme, 'netloc': urls.netloc, 'host': host, 'port': port, 'path': urls.path,
                'query': urls.query, 'fragment': urls.fragment}
        return munchify(urls)

    # 解析URL
    def url_query_decode(self, query=''):
        query_dict = dict()
        for line in unquote_plus(query).split('&'):
            line = line.split(sep='=', maxsplit=1)
            if len(line) == 2:
                query_dict[line[0]] = line[1]
        if len(query_dict) == len(query.split('&')):
            return query_dict
        else:
            return query

    # 判断是否是list或dict并尝试转换
    def convert_to_list_or_dict(self, string, s_type='list'):
        flag = True
        if s_type == 'list' and not isinstance(string, list):
            try:
                if isinstance(string, bytes):
                    string = ast.literal_eval(string.decode('utf8', errors='ignore'))
                else:
                    string = ast.literal_eval(string)
            except Exception as e:
                log.warning(e)
            if not isinstance(string, list):
                flag = False
        elif s_type == 'dict' and not isinstance(string, dict):
            if isinstance(string, bytes):
                string = string.decode('utf8', errors='ignore')
            try:
                string = ast.literal_eval(string)
            except Exception as e:
                log.warning(e)
                try:
                    string = json.loads(string)
                except Exception as e:
                    log.warning(e)
            if not isinstance(string, dict):
                flag = False
        return flag, string

    # 预定义参数
    def default_param(self):
        default_param = dict()
        default_param['{random_mobile}'] = '{}{}'.format(random.choice(['13', '14', '15', '17', '18']),
                                                         random.randint(100000000, 999999999))
        default_param['{random_email}'] = '{}@automation.test'.format(''.join(random.sample(
            'abcdefghijklmnopqrstuvwxyz', 6)))
        default_param['{timestamp}'] = int(time.time())
        default_param['{datetime}'] = time.strftime('%Y-%m-%d %H:%M:%S')
        default_param['{datetime_int}'] = time.strftime('%Y%m%d%H%M%S')
        default_param['{date}'] = time.strftime('%Y-%m-%d')
        default_param['{date_int}'] = time.strftime('%Y%m%d')
        return default_param
