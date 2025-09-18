# -*- coding: utf-8 -*-
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, create_engine
import json
from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.mysql import TIMESTAMP
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# from management_server.model.OrderModel import Order
# from management_server.model.ChargeModel import Charge
# from management_server.model.WithDrawModel import WithDraw
# from management_server.model.AppUserModel import AppUser

# 创建对象的基类:
Base = declarative_base()


# 定义Match对象:
class AppUser(Base):
    __tablename__ = 'm_app_user'
    MAJUSER_ID = Column(String(100), nullable=False, primary_key=True)
    OPENID = Column(String(32), comment="微信用户opeid(同样存放userID)")
    NICK_NAME = Column(String(255), comment="昵称")
    USER_ID = Column(String(64), comment="用户ID")
    STATUS = Column(String(6), comment="状态（ 0：正常 1：禁用）")
    SEX = Column(String(2), comment="性别（0:男 1：女）")
    PROVINCE = Column(String(64), comment="省份(暂不用)")
    CITY = Column(String(64), comment="城市(暂不用)")
    PHONE = Column(String(40), comment="手机号码")
    ROOM_CARD = Column(Integer)
    CREAT_TIME = Column(TIMESTAMP, default=datetime.now)
    OPT_TIME = Column(TIMESTAMP, comment="操作时间")

    LOGO_URL = Column(String(255), comment="头像路径")
    USER_ACCOUNT = Column(String(100), comment="pc版登录用户名(已废弃)")
    USER_PWD = Column(String(100), comment="用户密码")
    USER_TYPE = Column(String(2), comment="用户类型，1：app用户，2：pc用户(暂不用)")
    YQ_CODE = Column(String(16), comment="所属代理商的邀请码(已废弃)")
    BANK_CARD = Column(String(64), comment="银行卡")
    BANK_USER_NAME = Column(String(255), comment="用户真实姓名")
    AGENT_ID = Column(String(16), comment="代理商id,绑定代理商")
    TOTAL_MONEY = Column(String(32), default="0", comment="总金额(充值金额和返利金额都入这)")
    CASH_MONEY = Column(String(32), default="0", comment="提现金额")


HOST_WIN = 1
GUEST_WIN = 2
IN_DRAW = 3

BALL_BIG = 1
BALL_SMALL = 2
BALL_DRAW = 3

BALL_SINGLE = 1
BALL_DOUBLE = 2

engine1 = create_engine('mysql+pymysql://root:%s@%s:3306/%s?charset=utf8' % ("zaq12WSX", "192.168.99.162", "elszuqiu"),
                        pool_recycle=10600, pool_size=10600, max_overflow=200)
engine2 = create_engine('mysql+pymysql://root:%s@%s:3306/%s?charset=utf8' % ("zaq12WSX", "192.168.99.162", "elszuqiu_19"),
                        pool_recycle=10600, pool_size=10600, max_overflow=200)
engine = create_engine('mysql+pymysql://root:%s@%s:3306/%s?charset=utf8' % ("zaq12WSX", "localhost", "elszuqiu"),
                       pool_recycle=10600, pool_size=10600, max_overflow=200)


def get_session1():
    session_class = sessionmaker(bind=engine1)
    session = session_class()

    return session


def get_session2():
    session_class = sessionmaker(bind=engine2)
    session = session_class()
    return session


def get_session():
    session_class = sessionmaker(bind=engine)
    session = session_class()

    return session


# def count():
#     s1 = get_session1()
#     s2 = get_session2()
#     right = {}
#
#     withdraws = s1.query(WithDraw).filter(WithDraw.CREATE_TIME > "2020-08-19 00:00:00").all()
#     for withdraw in withdraws:
#         if withdraw.USER_ID not in right:
#             right[withdraw.USER_ID] = {"withdraw": 0, "current_money": 0, "left_19": 0, "bonus": 0, "bets": 0, "result": 0, "charges": 0}
#         right[withdraw.USER_ID]["withdraw"] += float(withdraw.MONEY)
#
#     current_moneys = s1.query(AppUser).filter(AppUser.USER_ID.in_(right)).all()
#     for cm in current_moneys:
#         right[cm.USER_ID]["current_money"] += float(cm.TOTAL_MONEY)
#
#     left_19 = s2.query(AppUser).filter(AppUser.USER_ID.in_(right)).all()
#     for cm in left_19:
#         right[cm.USER_ID]["left_19"] += float(cm.TOTAL_MONEY)
#
#     valid_orders = s1.query(Order).filter(Order.CREATE_TIME > "2020-08-19 00:00:00", Order.USER_ID.in_(right)).group_by(Order.ORDER_ID).all()
#     for order in valid_orders:
#         right[order.USER_ID]["bonus"] += float(order.BONUS or 0)
#         right[order.USER_ID]["bets"] += float(order.BET_MONEY)
#     charges = s1.query(Charge).filter(Charge.CREATOR_TIME > "2020-08-19 00:00:00", Charge.USER_ID.in_(right)).all()
#     for order in charges:
#         right[order.USER_ID.strip()]["charges"] += float(order.MONEY)
#
#     # print(right)
#     the_right = {}
#
#     # import xlwt
#     # style0 = xlwt.easyxf(num_format_str='0')
#     # wb = xlwt.Workbook()
#     # # 添加一个表
#     # ws = wb.add_sheet('test')
#     #
#     # # 3个参数分别为行号，列号，和内容
#     # # 需要注意的是行号和列号都是从0开始的
#     # ws.col(0).width = 4000
#     #
#     # ws.write(0, 0, '用户ID')
#     # ws.write(0, 1, '总提现')
#     # ws.write(0, 2, '当前余额')
#     # ws.write(0, 3, '19号余额')
#     # ws.write(0, 4, '总盈利')
#     # ws.write(0, 5, '总投注')
#     # ws.write(0, 6, '总充值')
#     # ws.write(0, 7, '结果')
#     cnt = 1
#     eq = 0
#     for k, v in right.items():
#         result = v["withdraw"] + v["current_money"] - v["left_19"] - v["bonus"] + v["bets"] - v["charges"]
#         if result < 100:
#             eq += 1
#             continue
#         the_right[k] = result
#         # ws.write(cnt, 0, k)
#         # ws.write(cnt, 1, v["withdraw"], style0)
#         # ws.write(cnt, 2, v["current_money"], style0)
#         # ws.write(cnt, 3, v["left_19"], style0)
#         # ws.write(cnt, 4, v["bonus"], style0)
#         # ws.write(cnt, 5, v["bets"], style0)
#         # ws.write(cnt, 6, v["charges"], style0)
#         # ws.write(cnt, 7, v["withdraw"] + v["current_money"] - v["left_19"] - v["bonus"] + v["bets"] - v["charges"], style0)
#         cnt += 1
#
#     # 保存excel文件
#     # wb.save('./test.xls')
#     # print("the right json:", the_right)
#     # with open("right_result.json", "w") as f:
#     #     f.write(json.dumps(the_right))
#     print("相等数量:", eq)


def save_the_project(reverse=False):
    session = get_session()
    with open("right_result.json", "r") as f:
        right_json = json.loads(f.read())
    users = session.query(AppUser).filter(AppUser.OPENID.in_(right_json)).all()
    users = {u.OPENID: u for u in users}
    for k, v in right_json.items():
        user = users[k]
        if reverse:
            user.TOTAL_MONEY = float(user.TOTAL_MONEY) + v
        else:
            user.TOTAL_MONEY = float(user.TOTAL_MONEY) - v
    session.commit()


def now_status():
    session1 = get_session1()
    with open("right_result.json", "r") as f:
        right_json = json.loads(f.read())
    users = session1.query(AppUser).filter(AppUser.OPENID.in_(right_json)).all()

    import xlwt
    style0 = xlwt.easyxf(num_format_str='0')
    wb = xlwt.Workbook()
    # 添加一个表
    ws = wb.add_sheet('test')
    # 3个参数分别为行号，列号，和内容
    # 需要注意的是行号和列号都是从0开始的
    ws.col(0).width = 4000
    ws.write(0, 0, '用户ID')
    ws.write(0, 1, '当前余额')
    cnt = 1
    for u in users:
        ws.write(cnt, 0, u.OPENID)
        ws.write(cnt, 1, u.TOTAL_MONEY, style0)
        cnt += 1

    # 保存excel文件
    wb.save('./now_last.xls')
    print("finish.")


if __name__ == '__main__':
    # save_the_project()
    save_the_project(True)
    # now_status()
    # count()
