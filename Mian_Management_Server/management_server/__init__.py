# -*- coding: utf-8 -*-
# m_withdrawal.CARD_NUM m_withdrawal.BANK_TYPE
# 2020/9/2 新增字段: m_play_recharge.BEFORE_MONEY m_play_recharge.AFTER_MONEY m_play_recharge.OPERATOR
# 2020/9/2 新增字段: m_withdrawal.BEFORE_MONEY m_withdrawal.AFTER_MONEY
# 2020/12/8 增加字段 ALTER TABLE m_app_user ADD COLUMN IS_VIP bool DEFAULT false not null COMMENT 'VIP';
# 2020/12/17 增加字段 ALTER TABLE m_app_user ADD COLUMN HIGHER_LIMIT bool DEFAULT false not null COMMENT 'HIGHER_LIMIT';
# 2020/12/17 增加配置 INSERT INTO m_dict ( MDICT_ID, REMARK, TITLE, CONTENT) VALUES ( '32', '混合盘口总下注限制', 'higher mix total limit', '80000');
# 2020/12/17 增加配置 INSERT INTO m_dict ( MDICT_ID, REMARK, TITLE, CONTENT) VALUES ( '33', '单场比赛混合限制',  'higher mix match limit', '80000');
# 2020/12/17 增加配置 INSERT INTO m_dict ( MDICT_ID, NAME, TITLE, CONTENT) VALUES ( '27', '比赛结算队列开关',  'settle on/off', '0');
# 2021/01/10 增加配置 INSERT INTO m_dict ( MDICT_ID, NAME, TITLE, CONTENT) VALUES ( '28', '当前提现组ID',  'current withdraw work group', '0');
# 2021/01/10 增加配置 INSERT INTO m_dict ( MDICT_ID, NAME, TITLE, CONTENT) VALUES ( '29', '单用户提现组切换时间',  'withdraw group expire time(minute)', '1');

# 2021/01/10 增加字段 ALTER TABLE m_sys_user ADD COLUMN Withdraw_Group INTEGER unsigned DEFAULT '0' not null COMMENT '结算组ID';
# 2021/01/10 增加字段 ALTER TABLE m_withdrawal ADD COLUMN Work_Group INTEGER unsigned DEFAULT '0' not null COMMENT '结算组ID';

# 2021/05/11 增加配置 INSERT INTO m_dict ( MDICT_ID, NAME, TITLE, CONTENT) VALUES ( '101', '2D/3D赔率',  'odds of 2D/3D', '20');
# 2021/05/11 增加配置 INSERT INTO m_dict ( MDICT_ID, NAME, TITLE, CONTENT) VALUES ( '102', '2D/3D平台佣金比例',  '2D/3D Comm', '5');
# 2021/05/11 增加字段 ALTER TABLE m_match_settle ADD COLUMN GAME_TYPE TINYINT unsigned DEFAULT '0' not null COMMENT '游戏类型: 0比赛 1数字';
# 2021/05/11 增加配置 INSERT INTO `m_route` (`ID`, `path`, `component`, `name`, `redirect`, `parent_id`, `alwaysShow`, `title`, `icon`, `roles`) VALUES (36, 'digital-list', '/match/digital-list', 'digital-list', NULL, '16', NULL, 'Digital List', 'table', NULL);

# 2021/05/11 增加字段
# ALTER TABLE m_digital ADD COLUMN LIMIT_CODE TINYINT unsigned DEFAULT '0' not null COMMENT '限额参数';
# ALTER TABLE m_digital ADD COLUMN LIMIT_NUM INTEGER unsigned DEFAULT '0' not null COMMENT '单数字限额';
# ALTER TABLE m_digital ADD COLUMN SINGLE_MIN INTEGER unsigned DEFAULT '0' not null COMMENT '单笔最小';
# ALTER TABLE m_digital ADD COLUMN SINGLE_MAX INTEGER unsigned DEFAULT '0' not null COMMENT '单笔最大';
# ALTER TABLE m_digital ADD COLUMN USER_MAX INTEGER unsigned DEFAULT '0' not null COMMENT '单用户最大';
# ALTER TABLE m_digital ADD COLUMN EX_LIMIT INTEGER unsigned DEFAULT '0' not null COMMENT '扩展限额';

# 2021/06/12 报表按游戏类型分类
# ALTER TABLE report_history ADD COLUMN game_type TINYINT unsigned DEFAULT '1' not null COMMENT '游戏类型: 1比赛 2数字';
# 2021/06/12 操作类型 是否数字盘操作
# ALTER TABLE m_app_operation ADD COLUMN IS_DIGIT bool DEFAULT false not null COMMENT '是否数字盘操作';
# 22/09/02 添加异常状态字段
# ALTER TABLE m_app_match ADD COLUMN exception TINYINT(3) DEFAULT '0' not null COMMENT '比赛异常状态：0正常，1可能异常，2确认异常';
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPTokenAuth
from flask_docs import ApiDoc
from blinker import Namespace
import redis

my_signals = Namespace()
user_opt = my_signals.signal('user_opt')
app_opt = my_signals.signal('app_opt')

app = Flask(__name__, static_folder='static', static_url_path='/static')
auth = HTTPTokenAuth(scheme="JWT")
CORS(app, resources=r'/*')

# api文档地址: http://192.168.99.9:9090/docs/api/
app.config['API_DOC_MEMBER'] = ['match', 'order', 'charge', 'withdraw', 'user', 'menu', 'app_user', 'role',
                                'admin', 'notice', 'config', 'agent', 'settlement', 'report', 'operation',
                                'app_operation', 'login_record', 'bank_type', 'contact_fun', 'up_image',
                                'match_settle', 'withdraw_group']
ApiDoc(app)

# 此处切换环境配置
app.config.from_object('management_server.setting.TestingConfig')
# 新服配置
# app.config.from_object('management_server.setting.ProductionRWConfig')


Redis = redis.StrictRedis(app.config['REDIS_HOST'], app.config['REDIS_PORT'], app.config['REDIS_DB'], decode_responses=True)
db = SQLAlchemy(app)
db.engine_options = {"pool_pre_ping": True}

db.create_all()
