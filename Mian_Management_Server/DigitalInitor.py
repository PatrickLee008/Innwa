# -*- coding: utf-8 -*-
from management_server import db
from management_server.model.DigitalModel import Digital
from management_server.model.MDictModel import MDict
from management_server.model.OrderModel import Order
from datetime import datetime
import random

import time
import uuid


def init_today_digit():
    runtime = ['5', '6', ]
    localtime = time.strftime("%w", time.localtime())
    if localtime in runtime:
        print('今天是星期%s,不生成比赛' % localtime)
        return
    print(datetime.today())
    today_str = datetime.strftime(datetime.today(), "%Y%m%d")
    today_up_key = "%s_AM" % today_str
    today_down_key = "%s_PM" % today_str
    old_dig = Digital.query.filter_by(STAGE=today_up_key).first()
    if old_dig:
        return
    default_up_open = datetime.strptime("%s 09:00:00" % today_str, "%Y%m%d %H:%M:%S")
    default_up_close = datetime.strptime("%s 12:00:00" % today_str, "%Y%m%d %H:%M:%S")

    default_down_open = datetime.strptime("%s 12:00:00" % today_str, "%Y%m%d %H:%M:%S")
    default_down_close = datetime.strptime("%s 16:00:00" % today_str, "%Y%m%d %H:%M:%S")
    odds = float(MDict.query.filter_by(MDICT_ID="101").one().CONTENT)
    up_digit = Digital(STAGE=today_up_key, ODDS=odds, OPEN_TIME=default_up_open, CLOSE_TIME=default_up_close, CREATOR='system', LIMIT_CODE='10', LIMIT_NUM='100000', EX_LIMIT='50000', SINGLE_MIN='1000', SINGLE_MAX='10000', USER_MAX='20000')
    down_digit = Digital(STAGE=today_down_key, ODDS=odds, OPEN_TIME=default_down_open, CLOSE_TIME=default_down_close, CREATOR='system', LIMIT_CODE='10', LIMIT_NUM='100000', EX_LIMIT='50000', SINGLE_MIN='1000', SINGLE_MAX='10000', USER_MAX='20000')
    db.session.add(up_digit)
    db.session.add(down_digit)
    db.session.commit()


def ini_orders():
    today_str = datetime.strftime(datetime.today(), "%Y%m%d")
    today_down_key = "%s_%s" % (today_str, 2)
    digit_stage = Digital.query.filter_by(STAGE=today_down_key).first()
    print(today_down_key, digit_stage.ID)
    user_id = "0988888888"
    order_id = "%s-%s" % (user_id, round(time.time() * 1000))
    new_order = Order(ID=str(uuid.uuid4()).replace("-", ""), ORDER_ID=order_id, ORDER_TYPE='8', STATUS="1", MATCH_TIME=digit_stage.CLOSE_TIME,
                      MATCH_ID=digit_stage.ID, USER_ID=user_id, USER_NAME="xxXxx", BET_ODDS=digit_stage.ODDS,
                      BET_TYPE=random.randint(0, 99), BET_MONEY=500, IP="0")
    db.session.add(new_order)
    db.session.commit()


if __name__ == '__main__':
    init_today_digit()
    # for i in range(10):
    #     ini_orders()
