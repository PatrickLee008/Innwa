# -*- coding: utf-8 -*-
# 此处修改配置参数


class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = '123456'
    DB_USER = "root"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 1000
    SQLALCHEMY_POOL_TIMEOUT = 10
    SQLALCHEMY_POOL_RECYCLE = 10600

    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 0
    REDIS_EXPIRE = 60




class ProductionRWConfig(Config):
    # DB_ADDRESS = "qzaf39cymr5gb2zt8yto-rw4rm.rwlb.singapore.rds.aliyuncs.com"
    DB_ADDRESS = "pc-gs5o3o40mcus3g0cf.rwlb.singapore.rds.aliyuncs.com"
    DB_PASSWORD = "zaq12WSX"
    DATABASE = "innwa"
    DB_USER = "innwa"
    APP_IMAGE_DIR = '/www/wwwroot/img_upload'
    SPHINX_COMMAND = r'/www/sphinx-3.1.1/bin/indexer -c /www/sphinx-3.1.1/etc/order_history.conf order_history_add --rotate'
    PORT = 9090
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s:3306/%s?charset=utf8' % (DB_USER, DB_PASSWORD, DB_ADDRESS, DATABASE)



class TestingConfig(Config):
    DB_ADDRESS = "192.168.99.114"
    DB_PASSWORD = "123456"
    DATABASE = "innwa"
    APP_IMAGE_DIR = 'E:/CodeBase/Soccer_App_Server/app_server/static/img_upload/'
    SPHINX_COMMAND = r"E:\SoftWares\sphinx-3.1.1\bin\indexer.exe -c E:\SoftWares\sphinx-3.1.1\bin\sphinx.conf order_history_add --rotate"
    PORT = 9090
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s:3306/%s?charset=utf8' % (Config.DB_USER, DB_PASSWORD, DB_ADDRESS, DATABASE)
    DEBUG = True
    # TESTING = True

