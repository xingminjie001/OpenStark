from settings import pool
from munch import munchify
from tornado import gen
from tornado.log import app_log as log
import pymysql


class ProjectModule(object):
    """
    项目表相关操作
    """
    # 添加项目
    @gen.coroutine
    def add_project(self, name):
        pj = yield self.get_project(name=name)
        if not pj:
            sql = "INSERT INTO t_projects (`name`) VALUE (%(name)s)"
            with (yield pool.Connection()) as conn:
                with conn.cursor() as cursor:
                    try:
                        yield cursor.execute(sql, dict(name=name))
                    except pymysql.Error as e:
                        yield conn.rollback()
                        log.error('添加项目失败#{}'.format(e))
                        flag, msg = False, '添加项目失败#{}'.format(e)
                    else:
                        yield conn.commit()
                        log.info('添加项目成功')
                        flag, msg = cursor.lastrowid, '添加项目成功'
            return flag, msg
        else:
            log.error('项目 {} 已存在'.format(name))
            return False, '项目 {} 已存在'.format(name)

    # 删除项目
    @gen.coroutine
    def delete_project(self, name=None, pid=None):
        pj = yield self.get_project(name=name, pid=pid)
        if pj:
            sql = "DELETE FROM t_projects"
            where = []
            param = dict()
            if name is not None:
                where.append("name=%(name)s")
                param['name'] = name
            elif pid is not None:
                where.append("id=%(pid)s")
                param['pid'] = pid
            if where:
                sql += ' WHERE {}'.format(' AND '.join(where))
                tx = yield pool.begin()
                try:
                    yield tx.execute(sql, param)
                except Exception as e:
                    yield tx.rollback()
                    log.error('删除项目 {} 失败#{}'.format(pj.name, e))
                    flag, msg = False, '项目 {} 有关联设置, 请先删除该项目下的所有设置后再删除该项目'.format(pj.name)
                else:
                    yield tx.commit()
                    log.info('删除项目 {} 成功'.format(pj.name))
                    flag, msg = True, '删除项目 {} 成功'.format(pj.name)
            else:
                flag, msg = False, '请指定删除项目条件, 不能删除所有项目'
        else:
            log.error('没有指定删除的项目')
            flag, msg = False, '没有指定删除的项目'
        return flag, msg

    # 编辑项目
    @gen.coroutine
    def edit_project(self, name=None, pid=None, user=None, status=None):
        update = []
        where = []
        param = dict()
        if name is not None:
            where.append("p.name=%(name)s")
            param['name'] = name
        elif pid is not None:
            where.append("p.id=%(pid)s")
            param['pid'] = pid
        if user is not None:
            update.append("p.user=%(user)s")
            param['user'] = user
        if status is not None:
            update.append("p.status=%(status)s")
            param['status'] = status
        pj = yield self.get_project(name=name, pid=pid)
        if where and update and pj:
            sql = 'UPDATE t_projects p SET {} WHERE {}'.format(', '.join(update), ' AND '.join(where))
            tx = yield pool.begin()
            try:
                yield tx.execute(sql, param)
            except pymysql.Error as e:
                log.error('项目 {} 编辑失败#{}'.format(pj.name, e))
                yield tx.rollback()
                flag, msg = False, '项目 {} 编辑失败#{}'.format(pj.name, e)
            else:
                yield tx.commit()
                log.info('项目 {} 编辑成功'.format(pj.name))
                flag, msg = True, '项目 {} 编辑成功'.format(pj.name)
            return flag, msg
        else:
            log.error('编辑项目参数不对')
            return False, '编辑项目参数不对'

    # 获取项目
    @gen.coroutine
    def get_project(self, name=None, pid=None, status=None):
        where = []
        param = dict()
        if status is not None:
            where.append("p.status=%(status)s")
            param['status'] = status
        if name is not None:
            where.append("p.name=%(name)s")
            param['name'] = name
        elif pid is not None:
            where.append("p.id=%(pid)s")
            param['pid'] = pid
        sql = 'SELECT * FROM t_projects p'
        if where:
            sql += ' WHERE {}'.format(' AND '.join(where))
            cursor = yield pool.execute(sql, param)
            result = cursor.fetchone()
            cursor.close()
            return munchify(result)
        else:
            log.error('参数不对, 获取项目失败')
            return None

    # 获取项目列表
    @gen.coroutine
    def get_projects_list(self, page=1, limit=10, status=None):
        sql = 'SELECT * FROM t_projects p'
        param = dict()
        if status is not None:
            sql += ' WHERE p.status=%(status)s'
            param['status'] = status
        sql += ' ORDER BY p.id DESC'
        if limit is not None:
            offset = (page - 1) * limit
            sql += ' LIMIT {},{}'.format(offset, limit)
        cursor = yield pool.execute(sql, param)
        print(sql)
        result = cursor.fetchall()
        cursor = yield pool.execute('SELECT COUNT(*) count FROM t_projects')
        total = cursor.fetchone()
        cursor.close()
        return munchify(result), munchify(total).count

    # 获取用户所有项目
    @gen.coroutine
    def get_projects_by_user(self, user, status=None):
        sql = "SELECT * FROM t_projects p WHERE p.user LIKE %(user)s"
        param = dict(user='%{}%'.format(user))
        if status is not None:
            sql += ' AND p.status=%(status)s'
            param['status'] = status
        sql += ' ORDER BY p.id DESC'
        cursor = yield pool.execute(sql, param)
        result = cursor.fetchall()
        cursor.close()
        return munchify(result)
