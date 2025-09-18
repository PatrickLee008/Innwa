# -*- coding: utf-8 -*-
from management_server import app_opt, app
from management_server.utils.OrmUttil import AppOpType
from management_server.model.MatchModel import Match
from management_server.model.OrderModel import Order
from management_server.model.AppUserModel import AppUser
from management_server.model.MDictModel import MDict
from management_server.model.SettleMentModel import Settlement
from management_server.model.MatchSettleModel import MatchSettle, SettleStatus, SettleType, GameType
from management_server.model.OrderHistoryModel import OrderHistory
from management_server.utils.OrmUttil import set_field
from management_server.model.AppOperationModel import AppOperation
from management_server.utils.OrmUttil import AppOpType2Name
from management_server.utils import get_session
from multiprocessing.dummy import Pool
from subprocess import Popen
from sqlalchemy import and_, or_
import datetime
import time
import uuid
import traceback

HOST_WIN = 1
GUEST_WIN = 2
IN_DRAW = 3

BALL_BIG = 1
BALL_SMALL = 2
BALL_DRAW = 3

BALL_SINGLE = 1
BALL_DOUBLE = 2


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
    match_id = order.MATCH_ID
    user_id = order.USER_ID
    print("---用户ID:[" + order.USER_ID, "] 开始结算订单ID:[" + order.ORDER_ID, "]")

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
    user = session.query(AppUser).filter_by(OPENID=user_id).first()

    if user:
        main_id = user.MAJUSER_ID
        del user
        user = session.query(AppUser).filter_by(MAJUSER_ID=main_id).with_for_update().first()
        nick_name = user.NICK_NAME
        before_amount = float(user.TOTAL_MONEY)
        after_amount = before_amount + bonus
        user.TOTAL_MONEY = after_amount

        # 写入coin log
        opt = AppOperation(USER_ACCOUNT=user_id, TYPE=AppOpType.SETTLEMENT, AMOUNT=before_amount,
                           MATCH_ID=match_id, BALANCE=after_amount, SOURCE_ID=order.ORDER_ID)
        opt.DESC = "%s do %s at %s make % amount change" % (nick_name, AppOpType2Name[AppOpType.SETTLEMENT], str(datetime.datetime.now().replace(microsecond=0)), bonus)
        session.add(opt)

        session.commit()

    # print("---用户ID:[" + user.USER_ID, "] 结算胜负订单ID:[" + order.ORDER_ID, "]完成, 奖金:", bonus, "结算后用户余额:", user.TOTAL_MONEY)


# 独赢盘
def settle_type_wld(order, com_ration, session):
    # 此模式不用计算佣金
    order = session.query(Order).filter_by(ID=order).one()

    match_id = order.MATCH_ID
    bet_money = int(order.BET_MONEY)  # 下注金额
    bet_type = order.BET_TYPE  # 下注类型 1主胜,2客胜,3平局
    odds = float(order.BET_ODDS)  # 订单下注时赔率

    host = int(order.BET_HOST_TEAM_RESULT)  # 主队比分
    guest = int(order.BET_GUEST_TEAM_RESULT)  # 客队比分

    result = host - guest  # 主队 - 客队 = result
    user_id = order.USER_ID
    print("---用户ID:[" + order.USER_ID, "] 开始结算订单ID:[" + order.ORDER_ID, "]")

    # 一.首先判断出胜利方,以主队为标准
    # 1:主胜
    # 2:客胜
    # 3:平局
    match_result = HOST_WIN if result > 0 else GUEST_WIN
    if result == 0:
        match_result = IN_DRAW

    #  二.根据比赛胜负和用户购买的订单计算出用户的奖金(奖金算上下注金额)
    bonus = 0  # 订单奖金
    is_win = 0

    # 用户买主胜
    if bet_type == "1" and match_result == HOST_WIN or bet_type == "2" and match_result == GUEST_WIN or bet_type == "3" and match_result == IN_DRAW:
        is_win = 1

    #  计算平台佣金
    com_money = 0
    if is_win == 0:
        com_money = 0
    elif is_win == 1:
        bonus = bet_money * odds
    print("the bonus:", bonus, "from order:", order.ORDER_ID)

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

    # 用户信息加锁写入
    user = session.query(AppUser).filter_by(OPENID=user_id).first()
    main_id = user.MAJUSER_ID
    del user
    user = session.query(AppUser).filter_by(MAJUSER_ID=main_id).with_for_update().first()
    nick_name = user.NICK_NAME
    before_amount = float(user.TOTAL_MONEY)
    after_amount = before_amount + bonus
    user.TOTAL_MONEY = after_amount

    # 写入coin log
    opt = AppOperation(USER_ACCOUNT=user_id, TYPE=AppOpType.SETTLEMENT, AMOUNT=before_amount,
                       MATCH_ID=match_id, BALANCE=after_amount, SOURCE_ID=order.ORDER_ID)
    opt.DESC = "%s do %s at %s make % amount change" % (nick_name, AppOpType2Name[AppOpType.SETTLEMENT], str(datetime.datetime.now().replace(microsecond=0)), bonus)
    session.add(opt)

    session.commit()

    # print("---用户ID:[" + user.USER_ID, "] 结算胜负订单ID:[" + order.ORDER_ID, "]完成, 奖金:", bonus, "结算后用户余额:", user.TOTAL_MONEY)


# 大小盘
def settle_type_big_small(order, commission_ratio, session):
    order = session.query(Order).filter_by(ID=order).one()
    if not order.BET_HOST_TEAM_RESULT:
        print("出现订单没有比分情况", order.ORDER_ID)

    bet_money = int(order.BET_MONEY)  # 下注金额
    ballType = order.BALL_TYPE  # 大小球类型,1:大球,2:小球
    odds = float(order.BET_ODDS)  # 下注时赔率
    draw_bunko = order.DRAW_BUNKO  # 平球胜负0:+,1:-
    draw_odds = int(order.DRAW_ODDS) * 0.01  # 平球赔率 %
    match_id = order.MATCH_ID

    lose_num = int(order.LOSE_BALL_NUM)  # 让球数
    host = int(order.BET_HOST_TEAM_RESULT)  # 主队比分
    guest = int(order.BET_GUEST_TEAM_RESULT)  # 客队比分
    result = host + guest  # 主队 - 客队 = result
    user_id = order.USER_ID

    # user = session.query(AppUser).filter_by(OPENID=order.USER_ID).one_or_none()
    print("---用户ID:[" + order.USER_ID, "] 开始结算大小球订单ID:[" + order.ORDER_ID, "]")

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
    user = session.query(AppUser).filter_by(OPENID=user_id).first()
    main_id = user.MAJUSER_ID
    del user
    user = session.query(AppUser).filter_by(MAJUSER_ID=main_id).with_for_update().first()
    nick_name = user.NICK_NAME
    before_amount = float(user.TOTAL_MONEY)
    after_amount = before_amount + bonus
    user.TOTAL_MONEY = after_amount

    # 写入coin log
    opt = AppOperation(USER_ACCOUNT=user_id, TYPE=AppOpType.SETTLEMENT, AMOUNT=before_amount,
                       MATCH_ID=match_id, BALANCE=after_amount, SOURCE_ID=order.ORDER_ID)
    opt.DESC = "%s do %s at %s make % amount change" % (nick_name, AppOpType2Name[AppOpType.SETTLEMENT], str(datetime.datetime.now().replace(microsecond=0)), bonus)
    session.add(opt)

    session.commit()
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
    match_id = order.MATCH_ID

    host = int(order.BET_HOST_TEAM_RESULT)  # 主队比分
    guest = int(order.BET_GUEST_TEAM_RESULT)  # 客队比分
    result = host + guest  # 主队 - 客队 = result
    user_id = order.USER_ID

    # user = session.query(AppUser).filter_by(OPENID=order.USER_ID).one_or_none()
    # 单双盘 单独读取佣金比例
    commission_ratio = int(session.query(MDict).filter_by(MDICT_ID="554").one().CONTENT) * 0.01
    print("---用户ID:[" + order.USER_ID, "] 开始结算大小球订单ID:[" + order.ORDER_ID, "] ")

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

    # 用户信息加锁写入
    user = session.query(AppUser).filter_by(OPENID=user_id).first()
    main_id = user.MAJUSER_ID
    del user
    user = session.query(AppUser).filter_by(MAJUSER_ID=main_id).with_for_update().first()
    nick_name = user.NICK_NAME
    before_amount = float(user.TOTAL_MONEY)
    after_amount = before_amount + bonus
    user.TOTAL_MONEY = after_amount

    # 写入coin log
    opt = AppOperation(USER_ACCOUNT=user_id, TYPE=AppOpType.SETTLEMENT, AMOUNT=before_amount,
                       MATCH_ID=match_id, BALANCE=after_amount, SOURCE_ID=order.ORDER_ID)
    opt.DESC = "%s do %s at %s make % amount change" % (nick_name, AppOpType2Name[AppOpType.SETTLEMENT], str(datetime.datetime.now().replace(microsecond=0)), bonus)
    session.add(opt)

    session.commit()


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
    elif order_type == "10":
        settle_type_wld(order, com_ratio, session)
    session.close()


def deal_blend_order(args):
    order_id, com_ratio = args[0], args[1]

    session = get_session()
    order = session.query(Order).filter_by(ID=order_id).one()

    match_id = order.MATCH_ID
    user_id = order.USER_ID
    user_name = order.USER_NAME
    order_id = order.ORDER_ID
    order_type = order.ORDER_TYPE
    the_match_id = order.MATCH_ID
    bet_money = int(order.BET_MONEY)
    com_money = 0
    # 保存所有需要结算的订单
    need_settle_orders = []
    # 所有关联的订单
    link_orders = session.query(Order).filter(Order.ORDER_ID == order_id, Order.STATUS != "0").all()
    match_to_order = {l_order.MATCH_ID: l_order for l_order in link_orders}
    # 关联订单与比赛
    link_matches = session.query(Match).filter(Match.MATCH_ID.in_(match_to_order.keys())).all()
    # 2.根据订单的比赛号查询该混合下注的所有比赛
    running_matches = [match for match in link_matches if match.IS_GAME_OVER == "0" and match.MATCH_ID != order.MATCH_ID]
    if order_id == "09457655802-1745919900654":
        print("--------", )
    print("订单:", order_id, '关联比赛共:', len(link_matches), "场, 其中正在进行比赛有:", len(running_matches), "场")
    # 已经完成的比赛
    fin_matches = [match for match in link_matches if match.IS_GAME_OVER == "1" or match.MATCH_ID == order.MATCH_ID]
    total_odds = 1  # 总赔率
    is_win = "0"
    for match in fin_matches:
        match_id = match.MATCH_ID
        print("开始计算订单:", order_id, "关联比赛:", match_id, "的输赢结果")
        # 与该比赛关联的订单
        link_order = match_to_order[match_id]
        need_settle_orders.append(link_order)
        if not match.HOST_TEAM_RESULT:
            print("已经结束的比赛却没有比分:", match.MATCH_ID)
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
        print("订单:", order_id, "关联比赛:", match_id, "的输赢结果为:", is_win, total_odds)

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
    print("订单:", order_id, '最终结算结果输赢:', is_win, "奖金:", odds_money)
    if odds_money > 0:
        print("---------此时一名乘客心态发生了变化:", user_id, odds_money)

    # 用户信息加锁写入
    user = session.query(AppUser).filter_by(OPENID=user_id).first()

    if user:
        MAJUSER_ID = user.MAJUSER_ID
        user = None
        user = session.query(AppUser).filter_by(MAJUSER_ID=MAJUSER_ID).with_for_update().first()
        nick_name = user.NICK_NAME
        before_amount = float(user.TOTAL_MONEY)
        after_amount = before_amount + odds_money
        user.TOTAL_MONEY = after_amount

        opt = AppOperation(USER_ACCOUNT=user_id, TYPE=AppOpType.SETTLEMENT, AMOUNT=before_amount,
                           MATCH_ID=match_id, BALANCE=after_amount, SOURCE_ID=order_id)
        opt.DESC = "%s do %s at %s make % amount change" % (nick_name, AppOpType2Name[AppOpType.SETTLEMENT], str(datetime.datetime.now().replace(microsecond=0)), before_amount)
        session.add(opt)

    t1 = time.time()
    # 放到最后删 这回不死锁了吧
    [session.delete(o) for o in link_orders]
    print("delete order to:", time.time() - t1)

    session.commit()
    session.close()


def count_match_bunko(order, h_r, g_r):
    orderType = int(order.ORDER_TYPE)  # 订单类型:1胜负2大小3波胆,4混合胜负,5混合大小6单笔单双7混合单双
    bet_type = int(order.BET_TYPE or 0)  # 下注类型,1主胜,2客胜
    ball_type = int(order.BALL_TYPE or 0)  # 大小球类型,1:大球,2:小球
    odds = float(order.BET_ODDS)  # 订单下注时赔率
    draw_bunko = order.DRAW_BUNKO  # 平局胜负0: +, 1: -
    draw_odds = int(order.DRAW_ODDS or "0")  # 平局赔率 %
    lose_team = int(order.LOSE_TEAM or 0)  # 让球方1: 主队, 2: 客队
    lose_num = int(order.LOSE_BALL_NUM or '0')  # 让球数
    # print("正在统计订单%s 的混合胜负.." % order.ORDER_ID)
    if order.ORDER_ID == '09264300052-1745918900034' and order.MATCH_ID == "1745899396231":
        print("count_match_bunko -----", h_r, g_r, order.ORDER_DESC)

    if not order.BET_HOST_TEAM_RESULT:
        order.BET_HOST_TEAM_RESULT = h_r
    if not order.BET_GUEST_TEAM_RESULT:
        order.BET_GUEST_TEAM_RESULT = g_r

    host = int(order.BET_HOST_TEAM_RESULT or h_r)  # 主队比分
    guest = int(order.BET_GUEST_TEAM_RESULT or g_r)  # 客队比分

    real_odds = draw_odds * 0.01  # 结算赔率(插入结算表中数据,不做计算)
    is_win = "1"  # 输赢状态0输1赢   3输半4赢半
    result = 0
    bunko_result = 1
    if host == 100 and guest == 100:
        real_odds = 1
        return is_win, real_odds
    # 胜负盘
    if orderType == 1 or orderType == 4:
        result = host - guest
        # 计算比分结果
        if lose_team == 1:
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
            real_odds = odds
        # 计算买主胜负
        # 用户买主胜
        if bet_type == 1:
            # 结果为 主胜
            if bunko_result == HOST_WIN:
                is_win = "1"
            # 结果为 平局
            elif bunko_result == IN_DRAW:
                # 主队让球
                if lose_team == 1:
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
                if lose_team == 1:
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
    elif orderType == 2 or orderType == 5:
        result = host + guest  # 总球数: 主队 + 客队
        # 一.首先判断出大小球
        if result > lose_num:
            bunko_result = BALL_BIG
        elif result == lose_num:
            bunko_result = BALL_DRAW
        else:
            bunko_result = BALL_SMALL
        if bunko_result == BALL_BIG or bunko_result == BALL_SMALL:
            real_odds = odds
        if ball_type == 1:
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
    elif orderType == 3:  # 波胆
        pass
    # 单双盘
    elif orderType == 6 or orderType == 7:  # 单双
        # 一.首先判断出大小球
        # 1: 单
        # 2: 双
        sd_result = BALL_DOUBLE if (host + guest) % 2 == 0 else BALL_SINGLE

        is_win = "1" if int(bet_type) == sd_result else "0"
        real_odds = odds
    elif orderType == 11:
        match_result = host - guest
        is_win = "0"
        # 用户买主胜
        if bet_type == "1" and match_result == HOST_WIN or bet_type == "2" and match_result == GUEST_WIN or bet_type == "3" and match_result == IN_DRAW:
            is_win = "1"
        real_odds = odds

    return is_win, float(real_odds)


def cancel_single(order):
    session = get_session()
    order = session.query(Order).filter_by(ID=order).one()
    order_id = order.ORDER_ID
    user_id = order.USER_ID
    match_id = order.MATCH_ID

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
    # 用户信息加锁写入
    user = session.query(AppUser).filter_by(OPENID=user_id).first()
    main_id = user.MAJUSER_ID
    del user
    user = session.query(AppUser).filter_by(MAJUSER_ID=main_id).with_for_update().first()
    nick_name = user.NICK_NAME
    before_amount = float(user.TOTAL_MONEY)
    after_amount = before_amount + bonus
    user.TOTAL_MONEY = after_amount

    # 写入coin log
    opt = AppOperation(USER_ACCOUNT=user_id, TYPE=AppOpType.CANCEL, AMOUNT=before_amount,
                       MATCH_ID=match_id, BALANCE=after_amount, SOURCE_ID=order.ORDER_ID)
    opt.DESC = "%s do %s at %s make % amount change" % (nick_name, AppOpType2Name[AppOpType.SETTLEMENT], str(datetime.datetime.now().replace(microsecond=0)), bonus)
    session.add(opt)

    session.commit()
    session.close()
    print("---用户ID:[" + user_id, "] 完成取消订单ID:[" + order_id, "]完成 奖金:", bonus, " 取消后用户余额:", after_amount)


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
    print("got single orders:", single_orders)
    start = time.time()
    # 多进程结算
    for order in single_orders:
        cancel_single(order.ID)

    session.commit()

    end = time.time()
    print("---取消比赛ID为:[", match_id, "]的 单笔 单用时----:", end - start, "秒")

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
    print(compile_popen.stdout)

    print("---取消比赛ID为:[", match_id, "]的 混合 单用时----:", end - start, "秒")
    return 1


def settle(match_id):
    try:
        print("---开始结算ID为:[", match_id, "]的比赛----:")
        session = get_session()
        the_match = session.query(Match).filter_by(MATCH_ID=match_id).one_or_none()
        session.commit()

        # 单笔佣金比例
        single_ratio = int(session.query(MDict).filter_by(MDICT_ID="555").one().CONTENT) * 0.01

        order_q = session.query(Order).filter(Order.MATCH_ID == match_id)
        order_q = order_q

        # 更新订单比分结果
        # 配合订单取消功能, 已经设置比分为100:100的订单不需要更新比分
        order_q.filter(or_(Order.BET_HOST_TEAM_RESULT != "100", Order.BET_HOST_TEAM_RESULT.is_(None)),
                       or_(Order.BET_GUEST_TEAM_RESULT != "100", Order.BET_GUEST_TEAM_RESULT.is_(None))).update({Order.BET_HOST_TEAM_RESULT: the_match.HOST_TEAM_RESULT, Order.BET_GUEST_TEAM_RESULT: the_match.GUEST_TEAM_RESULT})

        session.query(OrderHistory).filter(OrderHistory.MATCH_ID == match_id, OrderHistory.BET_HOST_TEAM_RESULT != 100,
                                           OrderHistory.BET_GUEST_TEAM_RESULT != 100).update({OrderHistory.BET_HOST_TEAM_RESULT: the_match.HOST_TEAM_RESULT, OrderHistory.BET_GUEST_TEAM_RESULT: the_match.GUEST_TEAM_RESULT})
        session.commit()
        time.sleep(0.5)

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
        # 混合佣金比例
        blend_ratio = int(session.query(MDict).filter_by(MDICT_ID="666").one().CONTENT) * 0.01
        blend_order_list = [(order.ID, blend_ratio) for order in blend_orders]

        # 多进程结算
        pool.map(deal_blend_order, blend_order_list)
        end = time.time()

        the_match.IS_GAME_OVER = "1"
        print("u r not dealing it ?!", the_match, the_match.IS_GAME_OVER)
        session.commit()
        session.close()
        pool.close()
        pool.join()

        # compile_popen = Popen(app.config['SPHINX_COMMAND'], shell=True)
        # compile_popen.wait()
        # print(compile_popen.stdout)

        print("---结算比赛ID为:[", match_id, "]的 混合 单用时----:", end - start, "秒")

    except Exception as e:
        print("settle error:", e)
        traceback.print_exc()

    return 1


def reverse_single(match_id):
    print("???????????")
    start = time.time()
    session = get_session()
    single_orders = session.query(OrderHistory).filter(OrderHistory.MATCH_ID == match_id, OrderHistory.IS_MIX == "0").all()

    print("got single orders:", single_orders)

    # 多进程结算
    for order_history in single_orders:
        order_id = order_history.ORDER_ID

        # 用户信息加锁写入
        user = session.query(AppUser).filter_by(OPENID=order_history.USER_ID).first()
        # 用户信息加锁写入
        main_id = user.MAJUSER_ID
        del user
        user = session.query(AppUser).filter_by(MAJUSER_ID=main_id).with_for_update().first()
        user_id = user.USER_ID
        nick_name = user.NICK_NAME

        before_amount = float(user.TOTAL_MONEY)
        after_amount = before_amount - float(order_history.BONUS)

        user.TOTAL_MONEY = after_amount
        print("---用户ID:[" + order_history.USER_ID, "] 开始撤回订单ID:[" + order_id, "] 撤回前用户余额:", before_amount)
        # order = Order(order_history.to_order())
        order = Order(ID=str(uuid.uuid4()).replace("-", ""))
        set_field(order, order_history.to_order())

        session.add(order)
        session.delete(order_history)

        # 写入coin log
        opt = AppOperation(USER_ACCOUNT=user_id, TYPE=AppOpType.REVERSE, AMOUNT=before_amount,
                           MATCH_ID=match_id, BALANCE=after_amount, SOURCE_ID=order.ORDER_ID)
        opt.DESC = "%s do %s at %s make % amount change" % (nick_name, AppOpType2Name[AppOpType.SETTLEMENT], str(datetime.datetime.now().replace(microsecond=0)), order_history.BONUS)
        session.add(opt)
    session.commit()
    session.close()
    # new_do_app_record(user_id, nick_name, order_id, before_amount, after_amount, AppOpType.REVERSE)
    # print("---用户ID:[" + user_id, "] 完成撤回订单ID:[" + order_id, "]完成 奖金:", bet_money, " 取消后用户余额:", after_amount)
    # 撤回比赛状态
    session.commit()

    end = time.time()
    print("---撤回比赛ID为:[", match_id, "]的 单笔 单用时----:", end - start, "秒")


def reverse_mix(match_id):
    start = time.time()
    session = get_session()
    origin_match = session.query(Match).get({'MATCH_ID': match_id})
    mix_history_orders = session.query(OrderHistory).filter(OrderHistory.MATCH_ID == match_id, OrderHistory.IS_MIX == "1").all()
    current_match_orders = {o.ORDER_ID: o for o in mix_history_orders}
    link_orders = session.query(OrderHistory).filter(OrderHistory.ORDER_ID.in_(current_match_orders), OrderHistory.IS_MIX == "1").all()

    win_orders = set()
    order_history_dict = {}
    for link_order in link_orders:
        if link_order.ORDER_ID not in order_history_dict:
            order_history_dict[link_order.ORDER_ID] = []
        order_history_dict[link_order.ORDER_ID].append(link_order)
        if link_order.IS_WIN:
            win_orders.add(link_order.ORDER_ID)
    for order_id, link_orders in order_history_dict.items():
        need_reverse = False
        if order_id in win_orders:
            # 订单结果为赢 则全部订单为胜或平 需要恢复整单
            need_reverse = True
        else:
            # 订单结果为输 则需要根据当前比赛已结结果进行判断
            current_match_order = current_match_orders[order_id]
            win, odds = count_match_bunko(current_match_order, origin_match.HOST_TEAM_RESULT, origin_match.GUEST_TEAM_RESULT)
            if win == "1":
                # 整单结果为输 则单笔订单为赢不影响结果
                # 如果每一单都未出结果 则整单需要回退
                all_valid = True
                for o in link_orders:
                    if o.MATCH_ID == match_id:
                        continue
                    if not (o.BET_HOST_TEAM_RESULT == -1 and o.BET_GUEST_TEAM_RESULT == -1):
                        all_valid = False
                        break
                if all_valid:
                    need_reverse = True
                else:
                    continue
            else:
                # 判断是否有别的已输订单
                has_other_lose = False
                for link_order in link_orders:
                    if link_order.MATCH_ID == match_id:
                        continue
                    # 未出结果比赛无需计算
                    if link_order.BET_HOST_TEAM_RESULT == -1 and link_order.BET_GUEST_TEAM_RESULT == -1:
                        continue
                    o_match = session.query(Match).get({'MATCH_ID': link_order.MATCH_ID})
                    win, odds = count_match_bunko(link_order, o_match.HOST_TEAM_RESULT, o_match.GUEST_TEAM_RESULT)
                    if win == "0":
                        has_other_lose = True
                        break

                if has_other_lose:
                    # 当存在别的已输订单时 当前比赛不影响最终结果
                    continue
                else:
                    # 不存在别的已输订单时 需要恢复整单
                    # print("整单输 单笔输")
                    need_reverse = True
        if need_reverse:
            # 当未结算订单表存在此关联订单时 删除订单
            session.query(Order).filter(Order.ORDER_ID == current_match_orders[order_id].ORDER_ID).delete()
            session.commit()
            session.execute(
                Order.__table__.insert(),
                [o.to_order() for o in link_orders]
                # Creator需要修改
            )
            [session.delete(oh) for oh in link_orders]
            user_id = link_orders[0].USER_ID
            user = session.query(AppUser).filter_by(OPENID=user_id).first()
            if user:
                # 用户信息加锁写入
                main_id = user.MAJUSER_ID
                del user
                user = session.query(AppUser).filter_by(MAJUSER_ID=main_id).with_for_update().first()

                nick_name = user.NICK_NAME
                before_amount = float(user.TOTAL_MONEY)
                after_amount = before_amount - float(link_orders[0].BONUS)
                user.TOTAL_MONEY = after_amount
                # 写入coin log
                opt = AppOperation(USER_ACCOUNT=user_id, TYPE=AppOpType.REVERSE, AMOUNT=before_amount,
                                   MATCH_ID=match_id, BALANCE=after_amount, SOURCE_ID=link_orders[0].ORDER_ID)
                opt.DESC = "%s do %s at %s make % amount change" % (nick_name, AppOpType2Name[AppOpType.SETTLEMENT], str(datetime.datetime.now().replace(microsecond=0)), link_orders[0].BONUS)
                session.add(opt)

    session.commit()
    session.query(Order).filter(Order.MATCH_ID == match_id, Order.IS_MIX == "1", Order.STATUS == "1").update({Order.BET_HOST_TEAM_RESULT: "", Order.BET_GUEST_TEAM_RESULT: ""})
    session.query(OrderHistory).filter(OrderHistory.MATCH_ID == match_id, OrderHistory.IS_MIX == "1").update({OrderHistory.BET_HOST_TEAM_RESULT: -1, OrderHistory.BET_GUEST_TEAM_RESULT: -1})
    session.commit()
    print("---撤回比赛ID为:[", match_id, "] 混合单用时----:", time.time() - start, "秒")


def reverse(match_id):
    start = time.time()
    session = get_session()

    reverse_single(match_id)
    reverse_mix(match_id)

    session.query(Match).filter_by(MATCH_ID=match_id).update({Match.HOST_TEAM_RESULT: "", Match.GUEST_TEAM_RESULT: "", Match.IS_GAME_OVER: 0})
    session.commit()

    end = time.time()
    print("---撤回比赛ID为:[", match_id, "] 总用时----:", end - start, "秒")
    return 1


def queue_settle():
    session = get_session()
    settle_on = session.query(MDict).get({'MDICT_ID': '27'}).CONTENT == "1"
    # print(session.query(Order).filter(Order.MATCH_ID == "1745903690287", or_(Order.BET_HOST_TEAM_RESULT != "100", Order.BET_HOST_TEAM_RESULT.is_(None)),
    #                                   or_(Order.BET_GUEST_TEAM_RESULT != "100", Order.BET_GUEST_TEAM_RESULT.is_(None))).all())
    if not settle_on:
        return
    settling_match = session.query(MatchSettle).filter(MatchSettle.STATUS == SettleStatus.SETTLING).one_or_none()
    if settling_match:
        return

    next_settle = session.query(MatchSettle).filter(MatchSettle.STATUS == SettleStatus.WAIT).first()
    if not next_settle:
        return

    try:
        next_settle.STATUS = SettleStatus.SETTLING
        session.commit()
        print("got to settle:", next_settle.ID, next_settle.STATUS)
        if next_settle.GAME_TYPE == GameType.Digit:
            from management_server.service.DigitSettle import Digit
            digit = Digit(next_settle)
            digit.execute()
        elif next_settle.GAME_TYPE == GameType.Digit3D:
            from management_server.service.Digit3DSettle import Digit3DSettle
            digit3d = Digit3DSettle(next_settle)
            digit3d.execute()
        else:
            if next_settle.SETTLE_TYPE == SettleType.SETTLE:
                settle(next_settle.MATCH_ID)
            elif next_settle.SETTLE_TYPE == SettleType.CANCEL:
                cancel(next_settle.MATCH_ID)
            elif next_settle.SETTLE_TYPE == SettleType.REVERSE:
                reverse(next_settle.MATCH_ID)
        # session.delete(next_settle)
        next_settle.STATUS = SettleStatus.FINISHED
        session.commit()
        session.close()

        compile_popen = Popen(app.config['SPHINX_COMMAND'], shell=True)
        compile_popen.wait()
        print(compile_popen.stdout)
    except Exception as e:
        next_settle.STATUS = SettleStatus.PAUSE
        session.commit()
        session.close()
        print("settle error:", e)
        traceback.print_exc()


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


if __name__ == '__main__':
    # print("开始撤回啊:", sys.argv[1])
    # reverse(sys.argv[1])
    while True:
        try:
            print("循环操作开始:", datetime.datetime.now())
            queue_settle()
            time.sleep(3)
        except Exception as e:
            print("cycle run error:", e)
            traceback.print_stack()
