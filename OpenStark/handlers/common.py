import datetime
import tornado
from tornado.web import RequestHandler
from tornado import gen, ioloop
from modules.setting import SettingModule
from modules.user import UserModule
from modules.project import ProjectModule
from modules.option import OptionModule
from functions.common import CommonFunction
from functions.options import OptionsFunction
import json
import functools


# 异步用户认证
def authenticated_async(f):
    @functools.wraps(f)
    #异步生成器
    @gen.engine
    def wrapper(self, *args, **kwargs):
        self._auto_finish = False
        self.current_user = yield gen.Task(self.get_current_user_async)
        if not self.current_user:
            if self.request.method == 'GET':
                self.redirect(self.get_login_url())
            else:
                self.send_error(403)
        else:
            f(self, *args, **kwargs)
    return wrapper


class BaseHandler(RequestHandler):
    """
    后台管理父类，后台相关handlers继承本类
    """
    current_user = None

    # 初始化方法
    @gen.coroutine
    def prepare(self):
        self.common_func = CommonFunction()
        self.user = UserModule()
        self.project = ProjectModule()
        self.setting = SettingModule()
        self.option = OptionModule()
        self.option_func = OptionsFunction()
        self.company = yield self.option_func.get_option_by_name(name='company')
        self.limit = yield self.option_func.get_option_by_name(name='page_limit')
        self.company = self.company or '开源接口测试平台'
        self.argv = dict(company=self.company)

    # 获取当前用户信息
    @gen.engine
    def get_current_user_async(self, callback):
        user = self.get_secure_cookie('BSTSESSION', None)
        if user is not None:
            if isinstance(user, bytes):
                user = user.decode('utf8', errors='ignore')
            user = yield self.user.get_user_info(email_or_username=user)
            if not user:
                self.clear_cookie('BSTSESSION')
        callback(user)

    # 接口返回json格式字符串
    @gen.coroutine
    def return_json(self, msg):
        print(type(msg),msg)
        if isinstance(msg, dict):
            msg = json.dumps(msg, ensure_ascii=False)
        self.set_header('Content-Type', 'application/json')
        self.write(msg)
        self.finish()

if __name__ == '__main__':
    authenticated_async(functools)

