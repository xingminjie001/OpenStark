from tornado.web import escape
from tornado import gen
from functions.test_runner import TestRunner
from tornado.log import app_log as log
from handlers.common import BaseHandler, authenticated_async
from munch import munchify
from functions.custom import config
from handlers.admin.api import AddLogs
import json
import re
import math
import time


# 控制台操作类
class InterfaceHandler(BaseHandler):
    """
    控制台
    """
    @authenticated_async
    @gen.coroutine
    def get(self, op='overview', pid=0, page=1, limit=10):
        try:
            pid = int(pid)
            do = ''
        except Exception as e:
            log.warning(e)
            do = pid
            pid = 0
        if not isinstance(limit, int):
            limit = int(limit)
        else:
            limit = limit if self.limit == '' else int(self.limit)
        page = 1 if int(page) <= 0 else int(page)
        pid = 0 if pid < 0 else pid
        project_list = yield self.project.get_projects_by_user(user=self.current_user.email, status=1)
        lists = []
        total_page = 1
        if op == 'overview':
            jobs, total = yield self.setting.get_settings_list(
                s_type='job', user=self.current_user.email, pj_status=1, limit=limit, page=page)
            if pid != 0:
                jobs, total = yield self.setting.get_settings_list(
                    pid=pid, s_type='job', user=self.current_user.email, pj_status=1, limit=limit, page=page)
            if self.current_user.role != 2:
                project_list, total = yield self.project.get_projects_list(limit=None, status=1)
                jobs, total = yield self.setting.get_settings_list(s_type='job', pj_status=1, limit=limit, page=page)
                if pid != 0:
                    jobs, total = yield self.setting.get_settings_list(
                        pid=pid, s_type='job', pj_status=1, limit=limit, page=page)
            for job in jobs:
                sid = job.id
                project = job.project_name
                project_id = job.project_id
                status = job.status
                top = job.sort
                job = json.loads(job.value)
                cycle_time = job['overview']['cycle_time']
                if cycle_time == 0:
                    cycle_time = '一次'
                elif cycle_time == 3600:
                    cycle_time = '每时'
                elif cycle_time == 3600 * 24:
                    cycle_time = '每天'
                elif cycle_time == 3600 * 24 * 7:
                    cycle_time = '每周'
                elif cycle_time == 3600 * 24 * 30:
                    cycle_time = '每月'
                else:
                    cycle_time = '每年'
                lists.append(munchify(
                    dict(name=job['name'], top=top, sid=sid, project_id=project_id, project=project,
                         plan_time=job['overview']['plan_time'], cycle_time=cycle_time,
                         start_time=job['overview']['start_time'], end_time=job['overview']['end_time'],
                         elapsed_time=job['overview']['elapsed_time'], status=status, rid=job['lastreport'])))
            total_page = int(math.ceil(total / limit))
        elif op == 'reports':
            if do == 'job':
                self.argv['project'] = ''
                self.argv['name'] = ''
                self.argv['report_time'] = ''
                setting = yield self.setting.get_setting_by_id(page)
                if setting and setting.type == 'report':
                    report = json.loads(setting.value)
                    self.argv['project'] = setting.project_name
                    self.argv['name'] = report['overview']['name']
                    self.argv['report_time'] = report['overview']['report_time']
                    lists = report['report']
                for row in lists:
                    if row['report']:
                        row['success_rate'] = '{:.2f} %'.format(row['success_test'] / row['total_test'] * 100)
                    else:
                        row['success_rate'] = '0.00 %'
                lists = munchify(lists)
            elif do == 'list':
                self.argv['project'] = ''
                self.argv['name'] = ''
                self.argv['report_time'] = ''
                setting = yield self.setting.get_setting_by_id(page)
                if setting and setting.type == 'report':
                    report = json.loads(setting.value)
                    self.argv['project'] = setting.project_name
                    self.argv['report_time'] = report['overview']['report_time']
                    for row in report['report']:
                        if row['suite_id'] == limit and row['report']:
                            self.argv['name'] = row['suite_name']
                            lists = row['report']
                lists = munchify(lists)
            else:
                report, total = yield self.setting.get_settings_list(
                    s_type='report', user=self.current_user.email, status=1,
                    pj_status=1, limit=limit, page=page)
                if pid != 0:
                    report, total = yield self.setting.get_settings_list(
                        pid=pid, s_type='report', user=self.current_user.email, status=1,
                        pj_status=1, limit=limit, page=page)
                if self.current_user.role != 2:
                    project_list, total = yield self.project.get_projects_list(limit=None, status=1)
                    report, total = yield self.setting.get_settings_list(
                        s_type='report', status=1, pj_status=1, limit=limit, page=page)
                    if pid != 0:
                        report, total = yield self.setting.get_settings_list(
                            pid=pid, s_type='report', status=1, pj_status=1, limit=limit, page=page)
                for row in report:
                    sid = row.id
                    project = row.project_name
                    row = json.loads(row.value)
                    lists.append(munchify(
                        dict(name=row['overview']['name'], sid=sid, project=project, start_time=row['overview']['start_time'],
                             end_time=row['overview']['end_time'], elapsed_time=row['overview']['elapsed_time'],
                             total=row['overview']['total'], total_test=row['overview']['total_test'],
                             success_test=row['overview']['success_test'], fail_test=row['overview']['fail_test'],
                             success_rate=row['overview']['success_rate'], report_time=row['overview']['report_time'])))
                total_page = int(math.ceil(total / limit))
        elif op == 'single':
            if self.current_user.role != 2:
                print('111')
                project_list, total = yield self.project.get_projects_list(limit=None, status=1)
        elif op == 'case':
            if self.current_user.role != 2:
                project_list, total = yield self.project.get_projects_list(limit=None, status=1)
            if do == 'list':
                suite = yield self.setting.get_setting_by_id(sid=page)
                case = json.loads(suite.value)['cases'] if suite and suite.type == 'suite' else []
                lists = yield self.setting.get_settings_by_ids(sids=case)
                interface = []
                for row in lists:
                    params = json.loads(row.value)
                    inter = dict(sort_id=row.sort, sid=row.id, pid=row.project_id, project=row.project_name, url=params['url'],
                                 label=params['label'], method=params['method'], headers=params['headers'], body=params['body'],
                                 comment=params['comment'], checkpoint=params['checkpoint'], correlation=params['correlation'],
                                 crypt=params['crypt'], encrypt_content=params['encrypt_content'])
                    interface.append(munchify(inter))
                lists = interface
                self.argv['suite_name'] = suite.name if suite and suite.type == 'suite' else ''
                self.argv['project_name'] = suite.project_name if suite and suite.type == 'suite' else ''
                self.argv['project_id'] = suite.project_id if suite and suite.type == 'suite' else 0
            elif do == 'edit':
                jobs = yield self.setting.get_setting_by_id(sid=page)
                pid = jobs.project_id if jobs and jobs.type == 'job' else 0
                self.argv['sid'] = 0
                self.argv['project_name'] = ''
                self.argv['job_name'] = ''
                self.argv['plan_time'] = ''
                self.argv['cycle_time'] = ''
                if jobs and jobs.type == 'job':
                    enable_suite = json.loads(jobs.value)['testsuite']
                    self.argv['project_name'] = jobs.project_name
                    self.argv['job_name'] = json.loads(jobs.value)['name']
                    self.argv['sid'] = jobs.id
                    self.argv['plan_time'] = time.strftime('%Y-%m-%dT%H:%M', time.gmtime(int(float(jobs.name)) + 3600 * 8))
                    self.argv['cycle_time'] = json.loads(jobs.value)['overview']['cycle_time']
                    if self.argv['cycle_time'] == 0:
                        self.argv['cycle_time'] = 'once'
                    elif self.argv['cycle_time'] == 3600:
                        self.argv['cycle_time'] = 'hour'
                    elif self.argv['cycle_time'] == 3600 * 24:
                        self.argv['cycle_time'] = 'day'
                    elif self.argv['cycle_time'] == 3600 * 24 * 7:
                        self.argv['cycle_time'] = 'week'
                    elif self.argv['cycle_time'] == 3600 * 24 * 30:
                        self.argv['cycle_time'] = 'mouth'
                    else:
                        self.argv['cycle_time'] = 'year'
                    lists, total = yield self.setting.get_settings_list(pid=pid, s_type='suite',
                                                                        user=self.current_user.email, pj_status=1,
                                                                        limit=None)
                    if self.current_user.role != 2:
                        lists, total = yield self.setting.get_settings_list(pid=pid, s_type='suite', pj_status=1,
                                                                            limit=None)
                    for row in lists:
                        if "{}".format(row.id) in enable_suite:
                            row.status = 0
                        row.value = munchify(json.loads(row.value))
                else:
                    self.redirect('/admin/interface-test/case')
                    return
            else:
                lists, total = yield self.setting.get_settings_list(s_type='suite', user=self.current_user.email,
                                                                    pj_status=1, limit=limit, page=page)
                if pid != 0:
                    lists, total = yield self.setting.get_settings_list(pid=pid, s_type='suite',
                                                                        user=self.current_user.email, pj_status=1,
                                                                        limit=limit, page=page)
                if self.current_user.role != 2:
                    lists, total = yield self.setting.get_settings_list(s_type='suite', pj_status=1,
                                                                        limit=limit, page=page)
                    if pid != 0:
                        lists, total = yield self.setting.get_settings_list(pid=pid, s_type='suite', pj_status=1,
                                                                            limit=limit, page=page)
                for row in lists:
                    row.value = munchify(json.loads(row.value))
                total_page = int(math.ceil(total / limit))
        elif op in ['encrypt', 'decrypt']:
            if self.current_user.role != 2:
                project_list, total = yield self.project.get_projects_list(limit=None, status=1)
        else:
            self.redirect('/admin/interface-test')
            return
        argv = dict(title='接口测试', op=op, project_list=project_list, lists=lists, total_page=total_page,
                    limit=limit, page=page, pid=pid, do=do)
        argv = dict(self.argv, **argv)
        total_page = 1 if total_page <= 0 else total_page
        if total_page < page and do not in ['job', 'list', 'edit']:
            self.redirect('/admin/interface-test/{}/{}/{}/{}'.format(op, pid, total_page, limit))
            return
        self.render('admin/interface.html', **argv)

    @authenticated_async
    @gen.coroutine
    def post(self, op='overview', do=''):
        add_logs = AddLogs(operate_ip=self.request.remote_ip)
        if op == 'overview':
            if do == 'runjob':
                sid = int(self.get_argument('sid', default=0))
                setting = yield self.setting.get_setting_by_id(sid)
                if setting is None:
                    msg = dict(result=False, msg='所选任务不存在')
                    yield self.return_json(msg)
                    return
                try:
                    yield self.setting.edit_setting(sid=sid, status=1)
                    msg = dict(result=True, msg='/admin/interface-test/overview')
                except RuntimeError as e:
                    log.warning(e)
                    msg = dict(result=False, msg='批量接口测试执行失败, 请检查接口配置是否正确')
                add_logs.add_logs()
                yield self.return_json(msg)
                return
            elif do == 'canceljob':
                sid = int(self.get_argument('sid', default=0))
                setting = yield self.setting.get_setting_by_id(sid)
                if setting is None:
                    msg = dict(result=False, msg='所选任务不存在')
                    yield self.return_json(msg)
                    return
                result, msg = yield self.setting.edit_setting(sid=sid, status=4)
                if result:
                    msg = dict(result=True, msg='/admin/interface-test/overview')
                else:
                    msg = dict(result=False, msg=msg)
                yield self.return_json(msg)
                return
            elif do == 'up':
                sid = int(self.get_argument('sid', default=0))
                top = int(self.get_argument('top', default=0))
                if top == 0:
                    top = 1
                else:
                    top = 0
                yield self.setting.edit_setting(sid=sid, sort=top)
                msg = dict(result=True, msg='/admin/interface-test/overview')
                yield self.return_json(msg)
                return
            elif do == 'delete':
                sid = int(self.get_argument('id', default=0))
                flag, msg = yield self.setting.delete_setting(sid=sid)
                if flag:
                    msg = dict(result=True, msg=msg)
                else:
                    msg = dict(result=False, msg=msg)
                yield self.return_json(msg=msg)
                return
        elif op == 'single':
            pid = int(self.get_argument('pid', default=0))
            if do in ['gethost', 'geturl']:
                if pid == 0:
                    msg = dict(result=False, msg=[], encrypt=[])
                    yield self.return_json(msg)
                    return
                msg = yield self.__get_url_by_project(pid=pid, do=do, user=self.current_user.email)
                if self.current_user.role != 2:
                    msg = yield self.__get_url_by_project(pid=pid, do=do)
                yield self.return_json(msg)
                return
            else:
                host = self.get_argument('host', default='')
                host_url = self.get_argument('host_url', default='')
                env = self.get_argument('env', default='none')
                method = self.get_argument('method', default='')
                url = self.get_argument('url', default='')
                label = self.get_argument('url_label', default='')
                headers = self.get_argument('headers', default='')
                body = self.get_argument('body', default='')
                body_crypt = self.get_argument('body_crypt', default='')
                encrypt_content = self.get_argument('encrypt_content', default='')
                decrypt_content = self.get_argument('decrypt_content', default='')
                redirects = self.get_argument('redirects', default='off')
                redirects = True if redirects == 'on' else False
                no_test = self.get_argument('notest', default='off')
                no_test = True if no_test == 'on' else False
                if host == 'none' and url == '':
                    msg = dict(result=False, msg='请选择要测试的接口或在【Url】中填写要测试的接口')
                    yield self.return_json(msg)
                    return
                elif host != 'none':
                    url = '{}{}'.format(host, host_url)
                elif not self.common_func.check_string(url, 'url'):
                        msg = dict(result=False, msg='请在【Url】中填写正确的接口地址, 必须以http(s)开头')
                        yield self.return_json(msg)
                        return
                add_logs.add_logs()
                test = TestRunner(pid=pid)
                body_rows = body.splitlines()
                if len(body_rows) > 1 and test.get_headers(headers)['Content-Type'].find('x-www-form-urlencoded') != -1:
                    body = ''
                    for row in body_rows:
                        if re.match(r'^.*=.*$', row) is None:
                            msg = dict(result=False, msg='【Body】格式不正确, 请检查')
                            yield self.return_json(msg)
                            return
                        body += '{}&'.format(row.strip())
                    body = body[0:-1]
                try:
                    if no_test:
                        request_body = yield test.run_test(
                            url=url, label=label, method=method, headers=headers, body=body, crypt=body_crypt,
                            encrypt_content=encrypt_content, decrypt_content=decrypt_content,
                            follow_redirects=redirects, no_test=no_test)
                        msg = dict(result=True, msg='{}?{}'.format(url, escape.xhtml_escape(request_body)), type='')
                    else:
                        resp = yield test.run_test(url=url, label=label, method=method, headers=headers, body=body,
                                                   env=env, crypt=body_crypt, encrypt_content=encrypt_content,
                                                   decrypt_content=decrypt_content, follow_redirects=redirects)
                        msg = dict(result=True,
                                   msg={'code': resp['code'], 'reason': resp['reason'], 'error': resp['error'],
                                        'request_headers': resp['request_headers'].splitlines(),
                                        'request_body': escape.xhtml_escape(resp['request_body']) if resp['request_body'] is not None else resp['request_body'],
                                        'headers': resp['headers'].splitlines(),
                                        'body': escape.xhtml_escape(resp['body']) if resp['body'] is not None else resp['body'],
                                        'body_decrypt': escape.xhtml_escape(resp['body_decrypt']) if resp['body_decrypt'] is not None else resp['body_decrypt'],
                                        'checkpoint': resp['checkpoint'],
                                        'check_key': resp['check_key'],
                                        'correlation': resp['correlation']}, type='test')
                except Exception as e:
                    msg = dict(result=False, msg=str(e))
                yield self.return_json(msg)
                return
        elif op == 'case':
            if do == 'add':
                pid = int(self.get_argument('pid', default=0))
                name = self.get_argument('name', default='').strip()
                sort_id = int(self.get_argument('id', default=0))
                if pid == 0:
                    msg = dict(result=False, msg='请先选择项目')
                elif name == '':
                    msg = dict(result=False, msg='测试集名称不能为空')
                else:
                    result, msg = yield self.setting.add_setting(
                        pid=pid, s_type='suite', name=name, sort=sort_id+1, value=json.dumps(
                            dict(cases=[], detail='操作步骤: \r\n预期结果:'), ensure_ascii=False))
                    if result:
                        msg = dict(result=True, msg='添加测试集成功')
                    else:
                        msg = dict(result=False, msg=msg)
                add_logs.add_logs()
                yield self.return_json(msg)
                return
            elif do == 'edit':
                sid = int(self.get_argument('sid', default=0))
                value = self.get_argument('value', default='')
                edit_type = self.get_argument('type', default='')
                suite = yield self.setting.get_setting_by_id(sid=sid)
                if suite:
                    name = value if edit_type == 'name' else None
                    if edit_type == 'detail':
                        cases = json.loads(suite.value)
                        cases['detail'] = value
                        value = json.dumps(cases, ensure_ascii=False)
                    else:
                        value = None
                    res, msg = yield self.setting.edit_setting(sid=sid, name=name, value=value)
                    if res:
                        msg = dict(result=True, msg='/admin/interface-test/case')
                    else:
                        msg = dict(result=False, msg=msg)
                else:
                    msg = dict(result=False, msg='所编辑配置不存在')
                yield self.return_json(msg)
            elif do == 'delete':
                sid = int(self.get_argument('id', default=0))
                suite = yield self.setting.get_setting_by_id(sid=sid)
                case = []
                if suite:
                    case = json.loads(suite.value)['cases']
                for i in case:
                    yield self.setting.delete_setting(sid=i)
                result, msg = yield self.setting.delete_setting(sid)
                if result:
                    msg = dict(result=True, msg='/admin/interface-test/case')
                else:
                    msg = dict(result=False, msg=msg)
                yield self.return_json(msg)
                return
            elif do == 'up':
                sid = int(self.get_argument('sid', default=0))
                sort_id = int(self.get_argument('id', default=0))
                pre_sid = int(self.get_argument('pre_sid', default=0))
                pre_id = int(self.get_argument('pre_id', default=0))
                yield self.setting.edit_setting(sid=sid, sort=sort_id - 1)
                yield self.setting.edit_setting(sid=pre_sid, sort=pre_id + 1)
                msg = dict(result=True, msg='/admin/interface-test/case')
                yield self.return_json(msg)
                return
            elif do == 'runtest':
                pid = int(self.get_argument('pid', default=0))
                jid = int(self.get_argument('jid', default=0))
                sid_list = self.get_arguments('sid')
                job_name = self.get_argument('job_name', default='')
                job_type = self.get_argument('type', default='')
                cycle_time = self.get_argument('cycle_time', default='')
                if cycle_time == 'once':
                    cycle_time = 0
                elif cycle_time == 'hour':
                    cycle_time = 3600
                elif cycle_time == 'day':
                    cycle_time = 3600 * 24
                elif cycle_time == 'week':
                    cycle_time = 3600 * 24 * 7
                elif cycle_time == 'mouth':
                    cycle_time = 3600 * 24 * 30
                else:
                    cycle_time = 3600 * 24 * 365
                if sid_list and pid != 0:
                    add_logs.add_logs()
                    job = yield self.setting.get_setting_by_id(sid=jid)
                    if job_type == 'now':
                        try:
                            plan_time = time.time()
                            if job and job.type == 'job':
                                jobs = json.loads(job.value)
                                jobs['name'] = job_name if job_name != '' else jobs['name']
                                jobs['overview']['cycle_time'] = cycle_time
                                jobs['overview']['plan_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(plan_time + 3600 * 8))
                                jobs['testsuite'] = sid_list
                                yield self.setting.edit_setting(sid=jid, name=plan_time, value=json.dumps(jobs, ensure_ascii=False), status=1)
                            else:
                                jobs = dict(name=job_name if job_name != '' else '临时任务_{}'.format(time.strftime('%Y%m%d%H%M%S')),
                                            overview=dict(plan_time=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(plan_time + 3600 * 8)),
                                                          cycle_time=cycle_time, start_time='', end_time='', elapsed_time=''),
                                            testsuite=sid_list, lastreport='')
                                yield self.setting.add_setting(pid=pid, s_type='job', name=plan_time,
                                                               value=json.dumps(jobs, ensure_ascii=False), status=1)
                            msg = dict(result=True, msg='/admin/interface-test/overview')
                        except Exception as e:
                            log.warning(e)
                            msg = dict(result=False, msg='批量接口测试执行失败, 请检查接口配置是否正确')
                    else:
                        plan_time = self.get_argument('plan_time', default='')
                        if plan_time == '' or re.match(r'^\d+-\d+-\d+T\d+:\d+$', plan_time) is None:
                            msg = dict(result=False, msg='请选择定时执行的日期及时间')
                        else:
                            plan_time = time.mktime(time.strptime(plan_time, '%Y-%m-%dT%H:%M'))
                            if job and job.type == 'job':
                                jobs = json.loads(job.value)
                                jobs['name'] = job_name if job_name != '' else jobs['name']
                                jobs['overview']['cycle_time'] = cycle_time
                                jobs['overview']['plan_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(plan_time + 3600 * 8))
                                jobs['testsuite'] = sid_list
                                yield self.setting.edit_setting(sid=jid, name=plan_time, value=json.dumps(jobs, ensure_ascii=False), status=0)
                            else:
                                jobs = dict(name=job_name if job_name != '' else '定时任务_{}'.format(time.strftime('%Y%m%d%H%M%S')),
                                            overview=dict(plan_time=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(plan_time + 3600 * 8)),
                                                          cycle_time=cycle_time, start_time='', end_time='', elapsed_time=''),
                                            testsuite=sid_list, lastreport='')
                                yield self.setting.add_setting(pid=pid, s_type='job', name=plan_time,
                                                               value=json.dumps(jobs, ensure_ascii=False), status=0)
                            msg = dict(result=True, msg='/admin/interface-test/overview')
                    yield self.return_json(msg)
                    return
                else:
                    msg = dict(result=False, msg='请选择项目和要执行测试的用例')
                    yield self.return_json(msg)
                    return
        elif op == 'list':
            if do in ['test', 'add']:
                pid = int(self.get_argument('pid', default=0))
                host = self.get_argument('host', default='')
                host_url = self.get_argument('host_url', default='')
                env = self.get_argument('env', default='none')
                label = self.get_argument('url_label', default='')
                method = self.get_argument('method', default='')
                headers = self.get_argument('headers', default='')
                body = self.get_argument('body', default='')
                body_crypt = self.get_argument('body_crypt', default='')
                encrypt_content = self.get_argument('encrypt_content', default='')
                decrypt_content = self.get_argument('decrypt_content', default='')
                checkpoint = self.get_argument('checkpoint', default='')
                check_key = self.get_argument('keys', default='')
                correlation = self.get_argument('correlation', default='')
                redirects = self.get_argument('redirects', default='off')
                redirects = True if redirects == 'on' else False
                if host == 'none':
                    msg = dict(result=False, msg='请选择要测试的接口')
                    yield self.return_json(msg)
                    return
                for key in check_key.splitlines():
                    if not self.common_func.check_string(string=key, str_type='check_key'):
                        msg = dict(result=False, msg='【完整性检查】配置行 {} 格式不正确, 请检查'.format(key if len(key) <= 70 else key[:70]))
                        yield self.return_json(msg)
                        return
                if checkpoint != '' and re.match(
                        r'^[^\|]+(\s*\|\s*[^\|]+)*$', checkpoint) is None and re.match(r'^/.*/$', checkpoint) is None:
                    msg = dict(result=False, msg='【检查点】格式不正确, 请检查')
                    yield self.return_json(msg)
                    return
                url = '{}{}'.format(host, host_url)
                if correlation != '':
                    for corr in correlation.split('|'):
                        if re.match(r'^\{[\w-]+\}=[\w-]+$', corr.strip()) is None and re.match(
                                r'^\{[\w-]+\}=(int|float)\([\w-]+\)$', corr.strip()) is None and re.match(
                            r'^\{[\w-]+\}=([\w-]+|\[\d+\])(\.[\w-]+|\.\[\d+\])*\.[\w-]+$', corr.strip()) is None and re.match(
                            r'^\{[\w-]+\}=(int|float)\(([\w-]+|\[\d+\])(\.[\w-]+|\.\[\d+\])*\.[\w-]+\)$', corr.strip()
                        ) is None and re.match(r'^\{[\w-]+\}=/.*/$', corr.strip()) is None and re.match(
                            r'^\{[\w-]+\}=(int|float)\(/.*/\)$', corr.strip()
                        ) is None and re.match(r'^\{[\w-]+\}=response_headers.([\w-]+|/.*/)$', corr.strip()) is None and re.match(
                            r'^\{[\w-]+\}=(int|float)\(response_headers.([\w-]+|/.*/)\)$', corr.strip()
                        ) is None:
                            msg = dict(result=False, msg='【关联配置】格式不正确, 请检查')
                            yield self.return_json(msg)
                            return
                test = TestRunner(pid=pid)
                body_rows = body.splitlines()
                if len(body_rows) > 1 and test.get_headers(headers)['Content-Type'].find('x-www-form-urlencoded') != -1:
                    body = ''
                    for row in body_rows:
                        if re.match(r'^.*=.*$', row) is None:
                            msg = dict(result=False, msg='【Body】格式不正确, 请检查')
                            yield self.return_json(msg)
                            return
                        body += '{}&'.format(row.strip())
                    body = body[0:-1]
                if do == 'test':
                    try:
                        resp = yield test.run_test(url=url, label=label, method=method, headers=headers, body=body, crypt=body_crypt,
                                                   check_key=check_key, encrypt_content=encrypt_content, decrypt_content=decrypt_content,
                                                   env=env, follow_redirects=redirects, checkpoint=checkpoint, correlation=correlation)
                        msg = dict(result=True, msg={'code': resp['code'], 'reason': resp['reason'],
                                                     'headers': resp['headers'].splitlines(), 'error': resp['error'],
                                                     'body': escape.xhtml_escape(resp['body']) if resp['body'] is not None else resp['body'],
                                                     'request_headers': resp['request_headers'].splitlines(),
                                                     'request_body': escape.xhtml_escape(resp['request_body']) if resp['request_body'] is not None else resp['request_body'],
                                                     'body_decrypt': escape.xhtml_escape(resp['body_decrypt']) if resp['body_decrypt'] is not None else resp['body_decrypt'],
                                                     'checkpoint': resp['checkpoint'],
                                                     'check_key': resp['check_key'],
                                                     'correlation': resp['correlation']}, type='test')
                    except Exception as e:
                        msg = dict(result=False, msg=str(e))
                    yield self.return_json(msg)
                    return
                else:
                    sort_id = int(self.get_argument('id', default=0))
                    comment = self.get_argument('comment', default='')
                    request_param = dict(url=url, label=label, comment=comment, method=method, headers=headers,
                                         body=body, crypt=body_crypt, check_key=check_key,
                                         encrypt_content=encrypt_content, decrypt_content=decrypt_content,
                                         checkpoint=checkpoint, correlation=correlation, follow_redirects=redirects)
                    sid = int(self.get_argument('sid', default=0))
                    suite_id = int(self.get_argument('suite_id', default=0))
                    if sid != 0:
                        setting = yield self.setting.get_setting_by_id(sid)
                        if setting is not None:
                            result, msg = yield self.setting.edit_setting(
                                sid=sid, value=json.dumps(request_param, ensure_ascii=False), sort=sort_id)
                            if result:
                                msg = dict(result=True, msg='/admin/interface-test/list/{}'.format(pid))
                            else:
                                msg = dict(result=False, msg=msg)
                            yield self.return_json(msg)
                            return
                    result, msg = yield self.setting.add_setting(
                        pid=pid, s_type='list', name=url, value=json.dumps(
                            request_param, ensure_ascii=False), sort=sort_id)
                    if result and suite_id != 0:
                        suite = yield self.setting.get_setting_by_id(sid=suite_id)
                        msg = dict(result=True, msg='/admin/interface-test/case/list/{}'.format(suite_id))
                        if suite:
                            case = json.loads(suite.value)
                            case['cases'].append(result)
                            res, massage = yield self.setting.edit_setting(sid=suite_id,
                                                                           value=json.dumps(case, ensure_ascii=False))
                            if not res:
                                msg = dict(result=False, msg=massage)
                    else:
                        msg = dict(result=False, msg=msg)
                    add_logs.add_logs()
                    yield self.return_json(msg)
                    return
            elif do == 'delete':
                sid = self.get_argument('id', default=0)
                suite_id = int(sid.split('|')[1])
                sid = int(sid.split('|')[0])
                result, msg = yield self.setting.delete_setting(sid)
                if result and suite_id != 0:
                    suite = yield self.setting.get_setting_by_id(sid=suite_id)
                    msg = dict(result=True, msg='/admin/interface-test/case/list/{}'.format(suite_id))
                    if suite:
                        case = json.loads(suite.value)
                        try:
                            case['cases'].remove(sid)
                            res, massage = yield self.setting.edit_setting(sid=suite_id,
                                                                           value=json.dumps(case, ensure_ascii=False))
                            if not res:
                                msg = dict(result=False, msg=massage)
                        except Exception as e:
                            log.warning(e)
                else:
                    msg = dict(result=False, msg=msg)
                yield self.return_json(msg)
                return
            elif do == 'edit':
                sid = int(self.get_argument('sid', default=0))
                pid = int(self.get_argument('pid', default=0))
                interface = yield self.setting.get_setting_by_id(sid)
                if interface is None:
                    msg = dict(result=False, msg='所请求配置项不存在')
                    yield self.return_json(msg)
                    return
                interface = json.loads(interface.value)
                encrypt, total = yield self.setting.get_settings_list(pid=pid, s_type='crypt', limit=None)
                encrypt = '' if not encrypt else json.loads(encrypt[0].value)['encrypt']['name']
                inter = self.common_func.url_split(interface['url'])
                ips = []
                ips_list, total = yield self.setting.get_settings_list(pid=pid, s_type='host',
                                                                       name=inter.host, limit=None)
                for ip in ips_list:
                    ips.append(dict(ip=ip.value, status=ip.status))
                interface['host'] = '{}://{}'.format(inter.scheme, inter.netloc)
                interface['url'] = inter.path
                interface['encrypt'] = encrypt
                msg = dict(result=True, msg=interface, ips=ips)
                yield self.return_json(msg)
                return
            elif do == 'up':
                sid = int(self.get_argument('sid', default=0))
                sort_id = int(self.get_argument('id', default=0))
                pre_sid = int(self.get_argument('pre_sid', default=0))
                pre_id = int(self.get_argument('pre_id', default=0))
                yield self.setting.edit_setting(sid=sid, sort=sort_id - 1)
                yield self.setting.edit_setting(sid=pre_sid, sort=pre_id + 1)
                msg = dict(result=True, msg='/admin/interface-test/list')
                yield self.return_json(msg)
                return
            elif do == 'detail':
                sid = int(self.get_argument('sid', default=0))
                detail = yield self.setting.get_setting_by_id(sid=sid)
                if detail:
                    detail = json.loads(detail.value)
                    detail['body'] = escape.xhtml_escape(detail['body'])
                    msg = dict(result=True, msg=detail)
                else:
                    msg = dict(result=False, msg='没有获取到接口配置详情参数')
                yield self.return_json(msg)
        elif op == 'encrypt':
            #print('111111')
            pid = int(self.get_argument('project', default=0))
            if do == 'getcrypt':
                #print('222111')
                encrypt = yield self.option_func.get_crypt_info(do=op, pid=pid)
                if encrypt is None:
                    msg = dict(result=False, msg='所选项目没有配置加密算法')
                else:
                    msg = dict(result=True, msg=[encrypt['name']])
                yield self.return_json(msg)
                return
            else:
                encrypt = self.get_argument('encrypt', default='')
                source = self.get_argument('source', default='')
                if pid == 0:
                    msg = dict(result=False, msg='请先选择加密算法所属项目!')
                    yield self.return_json(msg)
                    return
                elif encrypt == '0':
                    msg = dict(result=False, msg='请先选择加密算法!')
                    yield self.return_json(msg)
                    return
                yield self.__do_crypt(op=op, pid=pid, crypt=encrypt, source=source)
        elif op == 'decrypt':
            pid = int(self.get_argument('project', default=0))
            if do == 'getcrypt':
                decrypt = yield self.option_func.get_crypt_info(do=op, pid=pid)
                if decrypt is None:
                    msg = dict(result=False, msg='所选项目没有配置解密算法')
                else:
                    msg = dict(result=True, msg=[decrypt['name']])
                yield self.return_json(msg)
                return
            else:
                decrypt = self.get_argument('decrypt', default='')
                source = self.get_argument('source', default='')
                if pid == 0:
                    msg = dict(result=False, msg='请先选择解密算法所属项目!')
                    yield self.return_json(msg)
                    return
                elif decrypt == '0':
                    msg = dict(result=False, msg='请先选择解密算法!')
                    yield self.return_json(msg)
                    return
                elif source == '':
                    msg = dict(result=False, msg='请先填写需要解密的密文!')
                    yield self.return_json(msg)
                    return
                yield self.__do_crypt(op=op, pid=pid, crypt=decrypt, source=source)
        else:
            self.redirect('/admin/interface-test')

    # 根据项目获取接口地址
    @gen.coroutine
    def __get_url_by_project(self, pid, do='gethost', user=None):
        if do == 'gethost':
            hosts = []
            host_list, total = yield self.setting.get_settings_list(pid=pid, s_type='url', user=user, limit=None)
            for host in host_list:
                if host.name not in hosts:
                    hosts.append(host.name)
            encrypt = []
            crypt = yield self.option_func.get_crypt_info(do='encrypt', pid=pid)
            if crypt is not None:
                encrypt.append(crypt['name'])
            if len(hosts) > 0:
                msg = dict(result=True, msg=hosts, encrypt=encrypt)
            else:
                msg = dict(result=False, msg=['该项目还没有配置接口'], encrypt=encrypt)
        elif do == 'geturl':
            host = self.get_argument('host', default='')
            if host == 'none':
                return dict(result=False, msg=[])
            urls = []
            url_list, total = yield self.setting.get_settings_list(pid=pid, s_type='url', name=host,
                                                                   user=user, limit=None)
            for url in url_list:
                path = self.common_func.url_split(json.loads(url.value)['url']).path
                label = json.loads(url.value)['label']
                request_headers = json.loads(url.value)['request_headers']
                request_body = json.loads(url.value)['request_body']
                check_key = json.loads(url.value)['key']
                urls.append(dict(path=path, label=label, request_headers=request_headers,
                                 request_body=request_body, check_key=check_key))
            ips = []
            ips_list, total = yield self.setting.get_settings_list(pid=pid, s_type='host', user=user,
                                                                   name=self.common_func.url_split(host).host, limit=None)
            for ip in ips_list:
                ips.append(dict(ip=ip.value, status=ip.status))
            if len(urls) > 0:
                msg = dict(result=True, msg=urls, ips=ips)
            else:
                msg = dict(result=False, msg=['该项目还没有配置接口'], ips=ips)
        else:
            msg = dict(result=False, msg=['请求参数不对'])
        return msg

    # 加解密操作
    @gen.coroutine
    def __do_crypt(self, op='encrypt', pid=0, crypt='', source=''):
        setting, total = yield self.setting.get_settings_list(pid=pid, s_type='crypt', limit=None)
        if not setting:
            msg = dict(result=False, msg='该项目没有配置加解密算法!')
            yield self.return_json(msg)
            return
        if op == 'encrypt':
            encrypt_info = json.loads(setting[0].value)['encrypt']
            if encrypt_info['name'] != crypt:
                msg = dict(result=False, msg='该项目没有配置所选择的加密算法!')
                yield self.return_json(msg)
                return
            msg = dict(result=False, msg='加密算法配置不正确!')
            for encrypt in config.encrypt:
                if crypt == encrypt['name']:
                    func = encrypt['function']
                    try:
                        source = func(source, encrypt_info['key'], encrypt_info['iv'], encrypt['mode'])
                        msg = dict(result=True, msg=source)
                    except Exception as e:
                        msg = dict(result=False, msg='加密出错#{}'.format(str(e)))
                    break
        elif op == 'decrypt':
            decrypt_info = json.loads(setting[0].value)['decrypt']
            if decrypt_info['name'] != crypt:
                msg = dict(result=False, msg='该项目没有配置所选择的解密算法!')
                yield self.return_json(msg)
                return
            msg = dict(result=False, msg='解密算法配置不正确!')
            for decrypt in config.decrypt:
                if crypt == decrypt['name']:
                    func = decrypt['function']
                    try:
                        source = func(source, decrypt_info['key'], decrypt_info['iv'], decrypt['mode'])
                        msg = dict(result=True, msg=escape.xhtml_escape(source))
                    except Exception as e:
                        msg = dict(result=False, msg='解密出错#{}'.format(str(e)))
                    break
        else:
            msg = dict(result=False, msg='请求参数不对')
        add_logs = AddLogs(operate_ip=self.request.remote_ip)
        add_logs.add_logs()
        yield self.return_json(msg)
