# -*- coding: utf-8 -*-
# 此处修改配置参数
import os

base_dir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = '123456'
    DATABASE = "elszuqiu"
    CHARGE_APPLY_PIC_DIR = os.path.join(base_dir, 'static/img/charge_pics')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 10000
    SQLALCHEMY_POOL_TIMEOUT = 10
    SQLALCHEMY_POOL_RECYCLE = 10600

    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 0
    REDIS_EXPIRE = 60


class ProductionConfig(Config):
    DB_ADDRESS = "localhost"
    DB_PASSWORD = "zaq12WSX"
    PORT = 8181
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:%s@%s:3306/%s?charset=utf8' % (DB_PASSWORD, DB_ADDRESS, Config.DATABASE)
    LIVE_API_URL = "http://pay.okbetmm.com/openapi"


class ProductionRWConfig(Config):
    # DB_ADDRESS = "qzaf39cymr5gb2zt8yto-rw4rm.rwlb.singapore.rds.aliyuncs.com"
    DB_ADDRESS = "pc-gs5o3o40mcus3g0cf.rwlb.singapore.rds.aliyuncs.com"
    DB_PASSWORD = "zaq12WSX"
    DATABASE = "innwa"
    DB_USER = "innwa"
    PORT = 8282
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s:3306/%s?charset=utf8' % (DB_USER, DB_PASSWORD, DB_ADDRESS, DATABASE)


class ServerTestConfig(Config):
    DB_ADDRESS = "192.168.99.114"
    DB_PASSWORD = "123456"
    DATABASE = "innwa"
    PORT = 8282
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:%s@%s:3306/%s?charset=utf8' % (DB_PASSWORD, DB_ADDRESS, DATABASE)
    LIVE_API_URL = "http://pay.okbetmm.com/openapi"

class TestingConfig(Config):
    DB_ADDRESS = "localhost"
    DB_PASSWORD = "123456"
    DATABASE = "elszuqiu"
    PORT = 9190
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:%s@%s:3306/%s?charset=utf8' % (DB_PASSWORD, DB_ADDRESS, DATABASE)
    DEBUG = True
    # TESTING = True


class Mian3ProductionConfig(Config):
    DB_ADDRESS = "localhost"
    DB_PASSWORD = "zaq12WSX"
    DATABASE = "elszuqiu"
    APP_IMAGE_DIR = '/www/wwwroot/Soccer_App_Server_test/app_server/static/img/upload'
    PORT = 9190
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://elszuqiu:%s@%s:3306/%s?charset=utf8' % (DB_PASSWORD, DB_ADDRESS, DATABASE)


class Mian4TestConfig(Config):
    DB_ADDRESS = "localhost"
    DB_PASSWORD = "zaq12WSX"
    DATABASE = "elszuqiu"
    PORT = 8282
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://elszuqiu:%s@%s:3306/%s?charset=utf8' % (DB_PASSWORD, DB_ADDRESS, DATABASE)
