from tornado.websocket import WebSocketHandler
from tornado.log import app_log as log
from tornado.options import options
from tornado.web import escape
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
import os
import json
import time


class WeblogsHandler(WebSocketHandler):
    executor = ThreadPoolExecutor(50)
    #log_file_prefix = os.path.join(os.path.dirname(__file__), 'static/logs')

    def prepare(self):
        self.file = options.log_file_prefix
        self.flag = False
        self.fp = None
        self.offset = 0

    # 实时获取log日志并输出
    def open(self):
        log.info('建立WebSocket连接, 开始处理日志文件')
        if self.file is not None and os.path.isfile(self.file):
            self.fp = open(self.file, 'r')
            self.flag = True

    def on_message(self, message):
        log.info('收到消息: {}'.format(message))
        try:
            message = json.loads(message)
            if message['data'] == 'get_logs' and self.flag:
                self.__send_logs(message)
            elif self.file is None:
                message['data'] = ['无法读取日志文件或日志文件不存在, 请联系管理员处理, 可能在启动命令中没有加--log_file_prefix参数指定日志路径']
                self.write_message(json.dumps(message))
                self.close()
        except Exception as e:
            self.flag = False
            if self.fp is not None:
                self.fp.close()
            self.close()
            log.error(e)

    def on_close(self):
        log.info('WebSocket连接已关闭, 关闭日志文件')
        self.flag = False
        if self.fp is not None:
            self.fp.close()

    @run_on_executor
    def __send_logs(self, message):
        while self.flag:
            self.fp.seek(self.offset, 0)
            lines = self.fp.readlines()
            if lines:
                if self.offset == 0:
                    lines = lines if len(lines) < 20 else lines[-20:]
                for i in range(len(lines)):
                    lines[i] = escape.xhtml_escape(lines[i])
                message['data'] = lines
                self.offset = self.fp.tell()
                self.write_message(json.dumps(message))
            time.sleep(1)
