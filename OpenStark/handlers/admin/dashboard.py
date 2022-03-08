from handlers.common import BaseHandler, authenticated_async
from tornado import gen


class DashboardHandler(BaseHandler):
    @authenticated_async
    @gen.coroutine
    def get(self, op='test1'):
        if op == 'test1':
            pass
        elif op == 'test2':
            pass
        argv = dict(title='控制台', op=op)
        argv = dict(self.argv, **argv)
        self.render('admin/dashboard.html', **argv)
