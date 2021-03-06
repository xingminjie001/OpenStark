from functions.ui_modules import NavModule
from tornado.log import app_log as log
from tornado.web import gen
import os
import tormysql
import pymysql


# 数据库配置
db_host = 'localhost'
db_port = 3306
db_name = 'djangotest'
db_user = 'root'
db_password = '123456'
db_charset = 'utf8'
db_pool_size = 150
db_pool_recycle = 3600
db_timeout = 5

# 应用配置
template_path = os.path.join(os.path.dirname(__file__), 'templates')
static_path = os.path.join(os.path.dirname(__file__), 'static')
login_url = '/admin/login'
ui_modules = {'nav': NavModule}
cookie_secret = 'SQYMzDHiShGCl1gx/e4g5HHS7Be1UkPpk7eJxklvKmE='
xsrf_cookie = True
debug = True

# 定时任务配置
cycle_time = 5    # 定时任务监控周期(秒)

# 创建数据库连接池
pool = tormysql.helpers.ConnectionPool(
    max_connections=db_pool_size,
    idle_seconds=db_pool_recycle,
    wait_connection_timeout=db_timeout,
    host=db_host,
    port=db_port,
    user=db_user,
    passwd=db_password,
    db=db_name,
    charset=db_charset,
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)


# 初始化数据库
@gen.coroutine
def init_db():
    sql = """
CREATE TABLE IF NOT EXISTS `t_options` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `value` text NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_t_options_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `t_projects` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `user` text,
  `status` smallint(6) NOT NULL DEFAULT '1' COMMENT '0 禁用, 1 正常',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_t_projects_name` (`name`),
  KEY `ix_t_projects_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `t_settings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project` int(11) NOT NULL,
  `type` varchar(20) NOT NULL COMMENT 'url 接口、crypt 加解密、host 环境、job 任务、case 用例、suite 测试集、param 参数、report 报告、group 部门',
  `name` varchar(1000) NOT NULL,
  `value` longtext NOT NULL,
  `status` smallint(6) NOT NULL DEFAULT '1' COMMENT '0 禁用, 1 正常, job[0 计划中, 1 排队中, 2 测试中, 3 已完成, 4 暂停, 5 异常]',
  `sort` smallint(6) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `project` (`project`),
  KEY `ix_t_settings_type` (`type`),
  KEY `ix_t_settings_status` (`status`),
  CONSTRAINT `t_settings_ibfk_1` FOREIGN KEY (`project`) REFERENCES `t_projects` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `t_users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(60) DEFAULT '',
  `password` varchar(255) NOT NULL DEFAULT '',
  `realname` varchar(50) DEFAULT '',
  `email` varchar(100) NOT NULL DEFAULT '',
  `group` int(10) DEFAULT NULL,
  `role` smallint(6) NOT NULL DEFAULT '2' COMMENT '0 超级管理员, 1 管理员, 2 普通用户',
  `status` smallint(6) NOT NULL DEFAULT '1' COMMENT '0 禁用, 1 正常',
  `registerTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `lastLoginTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_t_users_email` (`email`),
  UNIQUE KEY `ix_t_users_username` (`username`),
  KEY `ix_t_users_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    """
    tx = yield pool.begin()
    try:
        log.info('初始化数据库SQL:\n{}'.format(sql))
        yield tx.execute(sql)
    except pymysql.Error as e:
        yield tx.rollback()
        log.error('初始化数据库失败#{}'.format(e))
    else:
        yield tx.commit()
        log.info('初始化数据库成功')
