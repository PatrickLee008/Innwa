# -*- coding: utf-8 -*-
from management_server import app_opt, app
from management_server.utils.OrmUttil import AppOpType
from management_server.model.MatchModel import Match, MatchAttr
from management_server.model.OrderModel import Order
from management_server.model.AppUserModel import AppUser
from management_server.model.MDictModel import MDict
from management_server.model.SettleMentModel import Settlement
from management_server.model.OrderHistoryModel import OrderHistory
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, create_engine
import datetime
from management_server.model.AppOperationModel import AppOperation
from management_server.utils.OrmUttil import AppOpType2Name
from multiprocessing.dummy import Pool
from subprocess import Popen
from management_server.utils.sphinxapi import *
import time
import uuid
import traceback
from sqlalchemy import event
from sqlalchemy import exc
import os

HOST_WIN = 1
GUEST_WIN = 2
IN_DRAW = 3

BALL_BIG = 1
BALL_SMALL = 2
BALL_DRAW = 3

BALL_SINGLE = 1
BALL_DOUBLE = 2

engine = create_engine('mysql+pymysql://%s:%s@%s:3306/%s?charset=utf8' % (app.config["DB_USER"], app.config["DB_PASSWORD"], app.config["DB_ADDRESS"], app.config["DATABASE"]),
                       pool_recycle=10600, pool_size=10600, max_overflow=200)


def set_field_by_orm(obj_db, data):
    for key in obj_db.__table__.columns.keys():
        if key in data:
            setattr(obj_db, key, data[key])


# 多进程相关配置,Pool使用事件来检测自身，以便在子进程中自动使连接无效
@event.listens_for(engine, "connect")
def connect(dbapi_connection, connection_record):
    connection_record.info['pid'] = os.getpid()


@event.listens_for(engine, "checkout")
def checkout(dbapi_connection, connection_record, connection_proxy):
    pid = os.getpid()
    if connection_record.info['pid'] != pid:
        connection_record.connection = connection_proxy.connection = None
        raise exc.DisconnectionError(
            "Connection record belongs to pid %s, "
            "attempting to check out in pid %s" %
            (connection_record.info['pid'], pid)
        )


def get_session():
    session_class = sessionmaker(bind=engine)
    session = session_class()

    return session


# 胜负盘
def settle_type_win_lose(order, com_ration, session):
    order = session.query(Order).filter_by(ID=order).one()

    bet_money = int(order.BET_MONEY)  # 下注金额
    bet_type = order.BET_TYPE  # 下注类型, 1    主胜, 2    客胜
    odds = float(order.BET_ODDS)  # 订单下注时赔率
    draw_bunko = order.DRAW_BUNKO  # 平局胜负0: +, 1: -
    draw_odds = int(order.DRAW_ODDS) * 0.01  # 平局赔率 %
    lose_team = order.LOSE_TEAM  # 让球方1: 主队, 2: 客队
    lose_num = int(order.LOSE_BALL_NUM)  # 让球数
    host = int(order.BET_HOST_TEAM_RESULT)  # 主队比分
    guest = int(order.BET_GUEST_TEAM_RESULT)  # 客队比分
    result = host - guest  # 主队 - 客队 = result
    # print("---用户ID:[" + order.USER_ID, "] 开始结算订单ID:[" + order.ORDER_ID, "]")

    # 一.首先判断出胜利方,以主队为标准
    # 1:主胜
    # 2:客胜
    # 3:平局

    bunko_result = 1
    if lose_team == "1":
        if result - lose_num > 0:
            bunko_result = HOST_WIN
        elif result - lose_num == 0:
            bunko_result = IN_DRAW
        else:
            bunko_result = GUEST_WIN
    else:
        if result + lose_num > 0:
            bunko_result = HOST_WIN
        elif result + lose_num == 0:
            bunko_result = IN_DRAW
        else:
            bunko_result = GUEST_WIN

    #  二.根据比赛胜负和用户购买的订单计算出用户的奖金(奖金算上下注金额)
    bonus = 0  # 订单奖金
    is_win = 1  # 输赢状态

    # 计算结算赔率
    sodds = draw_odds
    if bunko_result == 1 or bunko_result == 2:
        sodds = odds

    # 用户买主胜
    if bet_type == "1":
        if bunko_result == HOST_WIN:
            bonus = bet_money + bet_money * odds
        elif bunko_result == IN_DRAW:
            benefit = bet_money * draw_odds

            # 主队让球
            if lose_team == "1":
                # + 主让客,买主队 平局则赢
                if draw_bunko == "0":
                    bonus = bet_money + benefit
                # - 主队让客队,用户买主队 平局则输
                else:
                    bonus = bet_money - benefit
                    is_win = 3
            # 客队让球
            else:
                # + 客让主  买主输
                if draw_bunko == "0":
                    bonus = bet_money - benefit
                    is_win = 3
                # - 客让主  买主赢
                else:
                    bonus = bet_money + benefit
        else:
            is_win = 0

    # 用户买客胜
    else:
        # 客队胜
        if bunko_result == GUEST_WIN:
            bonus = bet_money + bet_money * odds
        # 平局
        elif bunko_result == IN_DRAW:
            benefit = bet_money * draw_odds
            # 主队让球
            if lose_team == "1":
                # + 主队让客队,用户买客队 平局则输
                if draw_bunko == "0":
                    bonus = bet_money - benefit
                    is_win = 3
                # - 主队让客队,用户买客队 平局则赢
                else:
                    bonus = bet_money + benefit
            # 客队让球
            else:
                # + 客让主 买客赢
                if draw_bunko == "0":
                    bonus = bet_money + benefit
                # - 客让主  买主赢
                else:
                    bonus = bet_money - benefit
                    is_win = 3
        else:
            is_win = 0

    #  计算平台佣金
    com_money = 0
    if is_win == 0:
        com_money = 0
    elif is_win == 1:
        com_money = (bonus - bet_money) * com_ration

    if is_win == 0:
        bonus = 0
    else:
        bonus -= com_money

    if is_win == 3:
        is_win = 0

    # 三.修改用户金额并保存结算记录

    # 2.修改订单数据(奖金,状态,输赢)
    order.BONUS = bonus
    order.STATUS = 0
    order.IS_WIN = is_win
    order.HOST_TEAM_RESULT = host
    order.GUEST_TEAM_RESULT = guest

    # 转换到历史记录
    order_history = OrderHistory()
    order_history.set_by_order(order)
    session.add(order_history)
    session.delete(order)

    # 3.插入结算记录
    settlement = Settlement(ID=str(uuid.uuid4()).replace("-", ""), TRAN_ID=order.ORDER_ID, USER_NICK_NAME=order.USER_NAME, USER_ID=order.USER_ID, MATCH_ID=order.MATCH_ID,
                            TRAN_MONEY=bet_money, TRAN_CONTENT=order.REMARK, AGENT_PROFIT_BL=sodds, AGENT_PROFIT_MONEY=com_money, STATUS="1")
    session.add(settlement)
    settlement.ORDER_TYPE = order.ORDER_TYPE
    settlement.PROFIT_TYPE = "2"

    # 用户信息加锁写入
    user = session.query(AppUser).filter_by(OPENID=order.USER_ID).with_for_update().first()
    nick_name = user.NICK_NAME
    before_amount = float(user.TOTAL_MONEY)
    after_amount = before_amount + bonus
    user.TOTAL_MONEY = after_amount

    session.commit()
    new_do_app_record(order.USER_ID, nick_name, order.ORDER_ID, before_amount, after_amount)

    # print("---用户ID:[" + user.USER_ID, "] 结算胜负订单ID:[" + order.ORDER_ID, "]完成, 奖金:", bonus, "结算后用户余额:", user.TOTAL_MONEY)


# 大小盘
def settle_type_big_small(order, commission_ratio, session):
    order = session.query(Order).filter_by(ID=order).one()

    bet_money = int(order.BET_MONEY)  # 下注金额
    ballType = order.BALL_TYPE  # 大小球类型,1:大球,2:小球
    odds = float(order.BET_ODDS)  # 下注时赔率
    draw_bunko = order.DRAW_BUNKO  # 平球胜负0:+,1:-
    draw_odds = int(order.DRAW_ODDS) * 0.01  # 平球赔率 %

    lose_num = int(order.LOSE_BALL_NUM)  # 让球数
    host = int(order.BET_HOST_TEAM_RESULT)  # 主队比分
    guest = int(order.BET_GUEST_TEAM_RESULT)  # 客队比分
    result = host + guest  # 主队 - 客队 = result

    # user = session.query(AppUser).filter_by(OPENID=order.USER_ID).one_or_none()
    # print("---用户ID:[" + order.USER_ID, "] 开始结算大小球订单ID:[" + order.ORDER_ID, "]")

    # 一.首先判断出大小球
    # 1: 大球
    # 2: 小球
    # 3: 平球
    bunko_result = 1
    if result > lose_num:
        bunko_result = BALL_BIG
    elif result == lose_num:
        bunko_result = BALL_DRAW
    else:
        bunko_result = BALL_SMALL

    # 二.根据比赛总球数和用户购买的订单计算出用户的奖金(奖金算上下注金额)
    bonus = 0  # 订单奖金
    is_win = 1  # 输赢状态

    # 计算结算赔率
    sodds = draw_odds
    if bunko_result == 1 or bunko_result == 2:
        sodds = odds

    # 用户买大球
    if ballType == "1":
        # 开大球
        if bunko_result == BALL_BIG:
            bonus = bet_money + bet_money * odds
        elif bunko_result == BALL_DRAW:
            benefit = bet_money * draw_odds
            # 平局算赢
            if draw_bunko == "0":
                bonus = bet_money + benefit
            else:
                bonus = bet_money - benefit
                is_win = 3
        else:
            is_win = 0
    # 用户买小球
    else:
        # 开小球
        if bunko_result == BALL_SMALL:
            bonus = bet_money + bet_money * odds
        # 平球
        elif bunko_result == BALL_DRAW:
            benefit = bet_money * draw_odds
            # 平局算输
            if draw_bunko == "0":
                bonus = bet_money - benefit
                is_win = 3
            else:
                bonus = bet_money + benefit
        else:
            is_win = 0

    #  计算平台佣金
    com_money = 0
    if is_win == 0:
        com_money = 0
    elif is_win == 1:
        com_money = (bonus - bet_money) * commission_ratio

    if is_win == 0:
        bonus = 0
    else:
        bonus -= com_money

    if is_win == 3:
        is_win = 0

    # 三.修改用户金额并保存结算记录
    # 2.修改订单数据(奖金,状态,输赢)
    order.BONUS = bonus
    order.STATUS = 0
    order.IS_WIN = is_win
    order.HOST_TEAM_RESULT = host
    order.GUEST_TEAM_RESULT = guest
    # 转换到历史记录
    order_history = OrderHistory()
    order_history.set_by_order(order)
    session.add(order_history)
    session.delete(order)

    # 3.插入结算记录
    settlement = Settlement(ID=str(uuid.uuid4()).replace("-", ""), TRAN_ID=order.ORDER_ID, USER_NICK_NAME=order.USER_NAME, USER_ID=order.USER_ID, MATCH_ID=order.MATCH_ID,
                            TRAN_MONEY=bet_money, TRAN_CONTENT=order.REMARK, AGENT_PROFIT_BL=sodds, AGENT_PROFIT_MONEY=com_money, STATUS="1")
    session.add(settlement)
    settlement.ORDER_TYPE = order.ORDER_TYPE
    settlement.PROFIT_TYPE = "2"

    session.commit()

    # 用户信息加锁写入
    user = session.query(AppUser).filter_by(OPENID=order.USER_ID).with_for_update().first()
    nick_name = user.NICK_NAME
    before_amount = float(user.TOTAL_MONEY)
    after_amount = before_amount + bonus
    user.TOTAL_MONEY = after_amount

    session.commit()

    new_do_app_record(order.USER_ID, nick_name, order.ORDER_ID, before_amount, after_amount)

    # print("---用户ID:[" + user.USER_ID, "] 结算大小球订单ID:[" + order.ORDER_ID, "]完成 奖金:", bonus, " 结算后用户余额:", user.TOTAL_MONEY)


# 波胆盘
def settle_type_bodan(order, com_ratio):
    return []


# 单双盘
def settle_type_single_double(order, commission_ratio, session):
    order = session.query(Order).filter_by(ID=order).one()

    bet_money = int(order.BET_MONEY)  # 下注金额
    bet_type = order.BET_TYPE  # 大小球类型,1:单,2:双
    odds = float(order.BET_ODDS)  # 下注时赔率

    host = int(order.BET_HOST_TEAM_RESULT)  # 主队比分
    guest = int(order.BET_GUEST_TEAM_RESULT)  # 客队比分
    result = host + guest  # 主队 - 客队 = result

    # user = session.query(AppUser).filter_by(OPENID=order.USER_ID).one_or_none()
    # 单双盘 单独读取佣金比例
    commission_ratio = int(session.query(MDict).filter_by(MDICT_ID="554").one().CONTENT) * 0.01
    # print("---用户ID:[" + order.USER_ID, "] 开始结算大小球订单ID:[" + order.ORDER_ID, "] ")

    # 一.首先判断出大小球
    # 1: 单
    # 2: 双
    sd_result = BALL_DOUBLE if result % 2 == 0 else BALL_SINGLE

    # 二.根据比赛总球数和用户购买的订单计算出用户的奖金(奖金算上下注金额)
    bonus = 0  # 订单奖金
    is_win = 1  # 输赢状态

    # 计算结算赔率

    # 判断是否买对
    if int(bet_type) == sd_result:
        bonus = bet_money + bet_money * odds
    else:
        is_win = 0

    #  计算平台佣金
    com_money = 0
    if is_win == 0:
        com_money = 0
    elif is_win == 1:
        com_money = (bonus - bet_money) * commission_ratio

    if is_win == 0:
        bonus = 0
    else:
        bonus -= com_money

    if is_win == 3:
        is_win = 0

    # 三.修改用户金额并保存结算记录
    # 2.修改订单数据(奖金,状态,输赢)
    order.BONUS = bonus
    order.STATUS = 0
    order.IS_WIN = is_win
    order.HOST_TEAM_RESULT = host
    order.GUEST_TEAM_RESULT = guest

    # 转换到历史记录
    order_history = OrderHistory()
    order_history.set_by_order(order)
    session.add(order_history)
    session.delete(order)

    # 3.插入结算记录
    settlement = Settlement(ID=str(uuid.uuid4()).replace("-", ""), TRAN_ID=order.ORDER_ID, USER_NICK_NAME=order.USER_NAME, USER_ID=order.USER_ID, MATCH_ID=order.MATCH_ID,
                            TRAN_MONEY=bet_money, TRAN_CONTENT=order.REMARK, AGENT_PROFIT_BL=odds, AGENT_PROFIT_MONEY=com_money, STATUS="1")

    session.add(settlement)
    settlement.ORDER_TYPE = order.ORDER_TYPE
    settlement.PROFIT_TYPE = "2"

    session.commit()

    # 用户信息加锁写入
    user = session.query(AppUser).filter_by(OPENID=order.USER_ID).with_for_update().first()
    nick_name = user.NICK_NAME
    before_amount = float(user.TOTAL_MONEY)
    after_amount = before_amount + bonus
    user.TOTAL_MONEY = after_amount

    session.commit()

    new_do_app_record(order.USER_ID, nick_name, order.ORDER_ID, before_amount, after_amount)


def deal_single_order(args):
    order, com_ratio, order_type = args[0], args[1], args[2]
    session = get_session()
    if order_type == "1":
        settle_type_win_lose(order, com_ratio, session)
    elif order_type == "2":
        settle_type_big_small(order, com_ratio, session)
    elif order_type == "3":
        settle_type_bodan(order, com_ratio)
    elif order_type == "6":
        settle_type_single_double(order, com_ratio, session)
    session.close()


def deal_blend_order(args):
    order_id, com_ratio = args[0], args[1]

    session = get_session()
    order = session.query(Order).filter_by(ID=order_id).one()
    user_id = order.USER_ID
    user_name = order.USER_NAME
    order_id = order.ORDER_ID
    order_type = order.ORDER_TYPE
    the_match_id =  order.MATCH_ID
    bet_money = int(order.BET_MONEY)
    com_money = 0
    # 保存所有需要结算的订单
    need_settle_orders = []
    # if order_id != "1575800477932":
    #     return
    # 所有关联的订单
    link_orders = session.query(Order).filter_by(ORDER_ID=order_id).all()
    # link_matches = []
    match_to_order = {l_order.MATCH_ID: l_order for l_order in link_orders}
    # match_to_order = {}
    # 关联订单与比赛
    link_matches = session.query(Match).filter(Match.MATCH_ID.in_(match_to_order.keys())).all()
    # 2.根据订单的比赛号查询该混合下注的所有比赛
    running_matches = [match for match in link_matches if match.IS_GAME_OVER == "0" and match.MATCH_ID != order.MATCH_ID]
    # print("订单:", order_id, '关联比赛共:', len(link_matches), "场, 其中正在进行比赛有:", len(running_matches), "场")
    # 已经完成的比赛
    fin_matches = [match for match in link_matches if match.IS_GAME_OVER == "1" or match.MATCH_ID == order.MATCH_ID]
    total_odds = 1  # 总赔率
    is_win = "0"
    for match in fin_matches:
        match_id = match.MATCH_ID
        # print("开始计算订单:", order_id, "关联比赛:", match_id, "的输赢结果")
        # 与该比赛关联的订单
        link_order = match_to_order[match_id]
        need_settle_orders.append(link_order)
        is_win, sodds = count_match_bunko(link_order, match.HOST_TEAM_RESULT, match.GUEST_TEAM_RESULT)
        odds = sodds
        if is_win == "0":
            total_odds = 0
            break
        else:
            # 0输1赢  3输半4赢半
            if is_win == "3":
                odds = 1 - sodds
            elif is_win == "4":
                odds = 1 + sodds
            total_odds = total_odds * odds
        # print("订单:", order_id, "关联比赛:", match_id, "的输赢结果为:", is_win, total_odds)

    # 关联比赛未全部结束 且没有输的注单 不做结算
    if len(running_matches) and is_win != "0":
        return []

    odds_money = bet_money * total_odds
    if total_odds > 1:
        real_ratio = com_ratio
        com_money = odds_money * real_ratio
        odds_money = odds_money - com_money
        is_win = "1"
    elif total_odds == 1:
        is_win = "1"
    else:
        is_win = "0"
    # 三.修改用户金额并保存结算记录
    # 2.修改订单数据(奖金,状态,输赢)
    for link_order in link_orders:
        link_order.BONUS = odds_money
        link_order.STATUS = 0
        link_order.IS_WIN = is_win
        # 转换到历史记录
        # order_history = OrderHistory()
        # order_history.set_by_order(link_order)
        # session.add(order_history)
        # session.delete(order)
    session.execute(
        OrderHistory.__table__.insert(),
        [o.to_history() for o in link_orders]
        # Creator需要修改
    )

    # 3.插入结算记录
    settlement = Settlement(ID=str(uuid.uuid4()).replace("-", ""), TRAN_ID=order_id, IS_WIN=is_win, BONUS=odds_money, USER_ID=user_id, MATCH_ID=the_match_id,
                            USER_NICK_NAME=user_name, TRAN_MONEY=bet_money, TRAN_CONTENT="混合单结算", AGENT_PROFIT_BL=total_odds, AGENT_PROFIT_MONEY=com_money, STATUS="1")
    session.add(settlement)
    settlement.ORDER_TYPE = order_type
    settlement.PROFIT_TYPE = "2"
    # print("订单:", order_id, '最终结算结果输赢:', is_win, "奖金:", odds_money)
    # if odds_money > 0:
        # print("---------此时一名乘客心态发生了变化:", user_id, odds_money)

    # 用户信息加锁写入
    user = session.query(AppUser).filter_by(OPENID=user_id).with_for_update().first()
    nick_name = user.NICK_NAME
    before_amount = float(user.TOTAL_MONEY)
    after_amount = before_amount + odds_money
    user.TOTAL_MONEY = after_amount

    opt = AppOperation(USER_ACCOUNT=user_id, TYPE=AppOpType.SETTLEMENT, AMOUNT=before_amount,
                       BALANCE=after_amount, SOURCE_ID=order_id)
    opt.DESC = "%s do %s at %s make % amount change" % (nick_name, AppOpType2Name[AppOpType.SETTLEMENT], str(datetime.datetime.now().replace(microsecond=0)), before_amount)
    session.add(opt)

    t1 = time.time()
    # 放到最后删 这回不死锁了吧
    [session.delete(o) for o in link_orders]
    # print("delete order to:", time.time() - t1)

    session.commit()
    session.close()

    # new_do_app_record(user_id, nick_name, order_id, before_amount, after_amount)


def count_match_bunko(order, h_r, g_r):
    orderType = order.ORDER_TYPE  # 订单类型:1胜负2大小3波胆,4混合胜负,5混合大小6单笔单双7混合单双
    bet_type = order.BET_TYPE  # 下注类型,1主胜,2客胜
    ball_type = order.BALL_TYPE  # 大小球类型,1:大球,2:小球
    odds = float(order.BET_ODDS)  # 订单下注时赔率
    draw_bunko = order.DRAW_BUNKO  # 平局胜负0: +, 1: -
    draw_odds = int(order.DRAW_ODDS or "0")  # 平局赔率 %
    lose_team = order.LOSE_TEAM  # 让球方1: 主队, 2: 客队
    lose_num = int(order.LOSE_BALL_NUM or '0')  # 让球数
    # print("正在统计订单%s 的混合胜负.." % order.ORDER_ID)
    if not order.BET_HOST_TEAM_RESULT:
        order.BET_HOST_TEAM_RESULT = h_r
    if not order.BET_GUEST_TEAM_RESULT:
        order.BET_GUEST_TEAM_RESULT = g_r

    host = int(order.BET_HOST_TEAM_RESULT)  # 主队比分
    guest = int(order.BET_GUEST_TEAM_RESULT)  # 客队比分

    sodds = draw_odds * 0.01  # 结算赔率(插入结算表中数据,不做计算)
    is_win = "1"  # 输赢状态0输1赢   3输半4赢半
    result = 0
    bunko_result = 1
    if host == 100 and guest == 100:
        sodds = 1
        return is_win, sodds
    # 胜负盘
    if orderType == "1" or orderType == "4":
        result = host - guest
        # 计算比分结果
        if lose_team == "1":
            if result - lose_num > 0:
                bunko_result = HOST_WIN
            elif result - lose_num == 0:
                bunko_result = IN_DRAW
            else:
                bunko_result = GUEST_WIN
        else:
            if result + lose_num > 0:
                bunko_result = HOST_WIN
            elif result + lose_num == 0:
                bunko_result = IN_DRAW
            else:
                bunko_result = GUEST_WIN
        if bunko_result == HOST_WIN or bunko_result == GUEST_WIN:
            sodds = odds
        # 计算买主胜负
        # 用户买主胜
        if bet_type == "1":
            # 结果为 主胜
            if bunko_result == HOST_WIN:
                is_win = "1"
            # 结果为 平局
            elif bunko_result == IN_DRAW:
                # 主队让球
                if lose_team == "1":
                    # + 主队让球赢
                    if draw_bunko == "0":
                        is_win = "4"
                    # - 主队让球输
                    else:
                        is_win = "3"
                # 客队让球
                else:
                    # + 客让主  买主输
                    if draw_bunko == "0":
                        is_win = "3"
                    # - 客让主  买主赢
                    else:
                        is_win = "4"
            else:
                is_win = "0"
        # 用户买客胜
        else:
            # 结果为 客胜
            if bunko_result == GUEST_WIN:
                is_win = "1"
            # 结果为 平局
            elif bunko_result == IN_DRAW:
                # 主队让球
                if lose_team == "1":
                    # + 主队让客队,用户买客队 平局则输
                    if draw_bunko == "0":
                        is_win = "3"
                    # - 主队让客队,用户买客队 平局则赢
                    else:
                        is_win = "4"
                # 客队让球
                else:
                    # + 客让主 买客赢
                    if draw_bunko == "0":
                        is_win = "4"
                    # - 客让主 买客输
                    else:
                        is_win = "3"
            else:
                is_win = "0"
    # 大小盘
    elif orderType == "2" or orderType == "5":
        result = host + guest  # 总球数: 主队 + 客队
        # 一.首先判断出大小球
        if result > lose_num:
            bunko_result = BALL_BIG
        elif result == lose_num:
            bunko_result = BALL_DRAW
        else:
            bunko_result = BALL_SMALL
        if bunko_result == BALL_BIG or bunko_result == BALL_SMALL:
            sodds = odds
        if ball_type == "1":
            # 开大球
            if bunko_result == BALL_BIG:
                is_win = "1"
            elif bunko_result == BALL_DRAW:
                # 平局算赢
                if draw_bunko == "0":
                    is_win = "4"
                else:
                    is_win = "3"
            else:
                is_win = "0"
        # 用户买小球
        else:
            # 开小球
            if bunko_result == BALL_SMALL:
                is_win = "1"
            # 平球
            elif bunko_result == BALL_DRAW:
                # 平局算输
                if draw_bunko == "0":
                    is_win = "3"
                else:
                    is_win = "4"
            else:
                is_win = "0"
    elif orderType == "3":  # 波胆
        pass
    # 单双盘
    elif orderType == "6" or orderType == "7":  # 单双
        # 一.首先判断出大小球
        # 1: 单
        # 2: 双
        sd_result = BALL_DOUBLE if (host + guest) % 2 == 0 else BALL_SINGLE

        is_win = "1" if int(bet_type) == sd_result else "0"
        sodds = odds

    return is_win, float(sodds)


def cancel_single(order):
    session = get_session()
    order = session.query(Order).filter_by(ID=order).one()
    order_id = order.ORDER_ID
    user_id = order.USER_ID

    bet_money = float(order.BET_MONEY)  # 下注金额

    host = int(order.BET_HOST_TEAM_RESULT)  # 主队比分
    guest = int(order.BET_GUEST_TEAM_RESULT)  # 客队比分

    bonus = bet_money
    is_win = 1

    # 三.修改用户金额并保存结算记录

    # 2.修改订单数据(奖金,状态,输赢)
    order.BONUS = bonus
    order.STATUS = 0
    order.IS_WIN = is_win
    order.HOST_TEAM_RESULT = host
    order.GUEST_TEAM_RESULT = guest

    # 转换到历史记录
    order_history = OrderHistory()
    order_history.set_by_order(order)
    session.add(order_history)
    session.delete(order)

    # 3.插入结算记录
    settlement = Settlement(ID=str(uuid.uuid4()).replace("-", ""), TRAN_ID=order.ORDER_ID, USER_NICK_NAME=order.USER_NAME, USER_ID=order.USER_ID, MATCH_ID=order.MATCH_ID,
                            TRAN_MONEY=bet_money, TRAN_CONTENT=order.REMARK, AGENT_PROFIT_BL="1", AGENT_PROFIT_MONEY="0", STATUS="1")
    session.add(settlement)
    settlement.ORDER_TYPE = order.ORDER_TYPE
    settlement.PROFIT_TYPE = "2"

    # 用户信息加锁写入
    user = session.query(AppUser).filter_by(OPENID=order.USER_ID).with_for_update().first()
    nick_name = user.NICK_NAME
    before_amount = float(user.TOTAL_MONEY)
    after_amount = before_amount + bonus
    user.TOTAL_MONEY = after_amount
    # print("---用户ID:[" + order.USER_ID, "] 开始取消订单ID:[" + order.ORDER_ID, "] 取消前用户余额:", before_amount)
    session.commit()
    session.close()

    new_do_app_record(user_id, nick_name, order_id, before_amount, after_amount, AppOpType.CANCEL)

    # print("---用户ID:[" + user_id, "] 完成取消订单ID:[" + order_id, "]完成 奖金:", bonus, " 取消后用户余额:", after_amount)


def cancel(match_id):
    session = get_session()

    # 提交比赛比分
    the_match = session.query(Match).filter_by(MATCH_ID=match_id).one()
    the_match.HOST_TEAM_RESULT = 100
    the_match.GUEST_TEAM_RESULT = 100
    session.commit()

    order_q = session.query(Order).filter(Order.MATCH_ID == match_id)

    # 更新订单比分结果
    order_q.update({Order.BET_HOST_TEAM_RESULT: 100, Order.BET_GUEST_TEAM_RESULT: 100})
    session.commit()

    # 单笔佣金比例
    # single_ratio = int(MDict.query.filter_by(MDICT_ID="555").one().CONTENT) * 0.01

    # 查询所有单笔订单
    single_orders = order_q.filter(Order.IS_MIX == "0").all()
    # single_orders = [(order, single_ratio) for order in single_orders]
    # print("got single orders:", single_orders)
    start = time.time()
    # 多进程结算
    for order in single_orders:
        cancel_single(order.ID)

    session.commit()

    end = time.time()
    # print("---结算比赛ID为:[", match_id, "]的 单笔 单用时----:", end - start, "秒")

    start = time.time()

    # 1.查询出包含该比赛号,并且有效,混合注的订单
    blend_orders = order_q.filter(and_(Order.IS_MIX == "1", Order.STATUS != "0")).all()
    # 混合佣金比例
    blend_ratio = int(session.query(MDict).filter_by(MDICT_ID="666").one().CONTENT) * 0.01
    blend_order_ids = [(order.ID, blend_ratio) for order in blend_orders]

    # 多进程结算
    for order_id in blend_order_ids:
        deal_blend_order(order_id)
    session.commit()

    end = time.time()

    the_match.IS_GAME_OVER = "1"
    session.commit()
    session.close()

    compile_popen = Popen(app.config['SPHINX_COMMAND'], shell=True)
    compile_popen.wait()
    # print(compile_popen.stdout)

    # print("---结算比赛ID为:[", match_id, "]的 混合 单用时----:", end - start, "秒")
    return 1


def settle(match_id, host_team_result, guest_team_result):
    try:
        session = get_session()
        the_match = session.query(Match).filter_by(MATCH_ID=match_id).one_or_none()
        # print(the_match.to_dict())
        # time.sleep(1000)
        # 提交比赛比分
        # the_match = Match.query.filter_by(MATCH_ID=match_id).one_or_none()
        the_match.HOST_TEAM_RESULT = host_team_result
        the_match.GUEST_TEAM_RESULT = guest_team_result
        session.commit()

        # 单笔佣金比例
        single_ratio = int(session.query(MDict).filter_by(MDICT_ID="555").one().CONTENT) * 0.01

        order_q = session.query(Order).filter(Order.MATCH_ID == match_id)
        # 更新订单比分结果
        order_q.update({Order.BET_HOST_TEAM_RESULT: host_team_result, Order.BET_GUEST_TEAM_RESULT: guest_team_result})

        # 处理已结算混合订单的比分
        # cl = SphinxClient()
        # cl.SetServer('localhost', 9312)
        # res = cl.Query("@MATCH_ID %s" % match_id, 'order_history;order_history_add')
        # total_found = res['total_found']
        # cl.SetLimits(0, total_found, total_found)
        # res = cl.Query("@MATCH_ID %s" % match_id, 'order_history;order_history_add')
        # if res and len(res['matches']):
        #     whole = {w['id'] for w in res['matches']}
        #     session.query(OrderHistory).filter(OrderHistory.ID.in_(whole)).update({OrderHistory.BET_HOST_TEAM_RESULT: host_team_result, OrderHistory.BET_GUEST_TEAM_RESULT: guest_team_result}, synchronize_session=False)
        #     session.commit()
        session.query(OrderHistory).filter(OrderHistory.MATCH_ID == match_id).update({OrderHistory.BET_HOST_TEAM_RESULT: host_team_result, OrderHistory.BET_GUEST_TEAM_RESULT: guest_team_result})
        session.commit()

        # # 查询所有单笔订单
        single_orders = order_q.filter(Order.IS_MIX == "0", Order.STATUS != "0").all()
        print("got single orders:", single_orders)
        order_list = [(order.ID, single_ratio, order.ORDER_TYPE) for order in single_orders]

        start = time.time()
        pool = Pool(10)
        # 多进程结算
        pool.map(deal_single_order, order_list)

        end = time.time()
        print("---结算比赛ID为:[", match_id, "]的 单笔 单用时----:", end - start, "秒")

        start = time.time()

        # # 1.查询出包含该比赛号,并且有效,混合注的订单
        blend_orders = order_q.filter(and_(Order.IS_MIX == "1", Order.STATUS != "0")).all()
        # print("why repeating orders?", len(blend_orders), blend_orders)
        # 混合佣金比例
        blend_ratio = int(session.query(MDict).filter_by(MDICT_ID="666").one().CONTENT) * 0.01
        blend_order_ids = [(order.ID, blend_ratio) for order in blend_orders]

        # 多进程结算
        pool.map(deal_blend_order, blend_order_ids)
        end = time.time()

        the_match.IS_GAME_OVER = "1"
        print("u r not dealing it ?!", the_match, the_match.IS_GAME_OVER)
        session.commit()
        session.close()
        pool.close()
        pool.join()

        compile_popen = Popen(app.config['SPHINX_COMMAND'], shell=True)
        compile_popen.wait()
        print(compile_popen.stdout)

        print("---结算比赛ID为:[", match_id, "]的 混合 单用时----:", end - start, "秒")
    except Exception as e:
        print("settle error:", e)
        traceback.print_exc()

    return 1


def deal_user_money(li):
    session = get_session()
    li = [u for u in li if u[0]]
    opt_li = []
    print("the li:", li)
    # user_money = {}
    user_ids = {u[0] for u in li}
    users = session.query(AppUser).filter(AppUser.OPENID.in_(user_ids)).all()
    users = {u.OPENID: u for u in users}

    for user_id, bonus, order_id in li:
        user = users[user_id]
        if user:
            before_amount = user.TOTAL_MONEY

            user.TOTAL_MONEY = float(user.TOTAL_MONEY) + bonus
            opt = {
                "USER_ACCOUNT": user_id,
                "TYPE": AppOpType.SETTLEMENT,
                "AMOUNT": before_amount,
                "BALANCE": user.TOTAL_MONEY,
                "SOURCE_ID": order_id,
                "DESC": "%s do %s at %s make % amount change" % (user.NICK_NAME, AppOpType2Name[AppOpType.SETTLEMENT], str(datetime.datetime.now().replace(microsecond=0)), before_amount)
            }
            opt_li.append(opt)
    session.execute(
        AppOperation.__table__.insert(),
        opt_li
    )

    session.commit()
    session.close()


def new_do_app_record(user_id, nick_name, order_id, before_amount, after_amount, opt_type=AppOpType.SETTLEMENT):
    app_opt.send({
        "user_account": user_id,
        "user_name": nick_name,
        "type": opt_type,
        "amount": before_amount,
        "balance": after_amount,
        "source_id": order_id
    })


# def do_app_record(user, before_amount, order_id, opt_type=AppOpType.SETTLEMENT):
#     app_opt.send({
#         "user_account": user.OPENID,
#         "user_name": user.NICK_NAME,
#         "type": opt_type,
#         "amount": before_amount,
#         "balance": float(user.TOTAL_MONEY),
#         "source_id": order_id
#     })

if __name__ == '__main__':
    settle("1610001398317", 8, 0)
