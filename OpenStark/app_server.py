#!/usr/bin/env python3

from tornado import httpserver, ioloop
from tornado.options import options, define
from tornado.web import Application
from functions.scheduler import job_monitor
from settings import *
import urls


class AppServer(Application):
    """应用启动入口"""
    def __init__(self):
        handlers = urls.handlers
        settings = {'template_path': template_path,
                    'static_path': static_path,
                    'cookie_secret': cookie_secret,
                    'xsrf_cookie': xsrf_cookie,
                    'login_url': login_url,
                    'ui_modules': ui_modules,
                    'debug': debug}
        #传递给Application类__init__方法的最重要的参数是handlers。
        # 它告诉Tornado应该用哪个类来响应请求
        #__init__方法中，我们创建了处理类列表以及一个设置的字典，然后在初始化子类的调用中传递这些值
        Application.__init__(self, handlers, **settings)

#一旦Application对象被创建，我们可以将其传递给Tornado的HTTPServer对象，
# 然后使用我们在命令行指定的端口进行监听（通过options对象取出。）
# 最后，在程序准备好接收HTTP请求后，我们创建一个Tornado的IOLoop的实例。
def main():
    define('port', default=9090, help='run on the given port', type=int)
    define('monitor', default='on', help='open jobs monitor', type=str)

    options.parse_command_line()
    http_server = httpserver.HTTPServer(AppServer(), xheaders=True)
    http_server.listen(options.port)

    #PeriodicCallback的源码足够的简单，就是传递回调函数及间隔时间后，调用start()来触发该任务
    if options.monitor.lower() == 'on':
        ioloop.PeriodicCallback(job_monitor, cycle_time * 1000).start()
    #ioloop.IOLoop.instance().run_sync(init_db)
    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
