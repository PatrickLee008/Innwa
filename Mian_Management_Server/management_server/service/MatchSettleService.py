# -*- coding: utf-8 -*-
from management_server import db, app_opt
from management_server.utils.OrmUttil import AppOpType
from management_server.model.MatchModel import Match, MatchAttr
from management_server.model.OrderModel import Order
from management_server.model.AppUserModel import AppUser
from management_server.model.MDictModel import MDict
from management_server.model.SettleMentModel import Settlement
from sqlalchemy import and_
from management_server.model.AgentModel import Agent
from multiprocessing.dummy import Pool
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
def settle_type_win_lose(order, com_ration):
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
    user = AppUser.query.filter_by(OPENID=order.USER_ID).one_or_none()
    print("---用户ID:[" + user.USER_ID, "] 开始结算订单ID:[" + order.ORDER_ID, "] 结算前用户余额:", user.TOTAL_MONEY)

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
    # 1.计算并修改玩家剩余总金额
    before_amount = float(user.TOTAL_MONEY)
    user.TOTAL_MONEY = before_amount + bonus

    # 2.修改订单数据(奖金,状态,输赢)
    order.BONUS = bonus
    order.STATUS = 0
    order.IS_WIN = is_win
    order.HOST_TEAM_RESULT = host
    order.GUEST_TEAM_RESULT = guest

    # 3.插入结算记录
    settlement = Settlement(ID=str(uuid.uuid4()).replace("-", ""), TRAN_ID=order.ORDER_ID, USER_NICK_NAME=order.USER_NAME, TRAN_MONEY=bet_money, TRAN_CONTENT=order.REMARK, AGENT_PROFIT_BL=sodds, AGENT_PROFIT_MONEY=com_money, STATUS="1")
    db.session.add(settlement)
    settlement.ORDER_TYPE = order.ORDER_TYPE
    settlement.PROFIT_TYPE = "2"

    db.session.commit()

    do_app_record(user, before_amount, settlement.ID)

    # print("---用户ID:[" + user.USER_ID, "] 结算胜负订单ID:[" + order.ORDER_ID, "]完成, 奖金:", bonus, "结算后用户余额:", user.TOTAL_MONEY)


# 大小盘
def settle_type_big_small(order, commission_ratio):
    bet_money = int(order.BET_MONEY)  # 下注金额
    ballType = order.BALL_TYPE  # 大小球类型,1:大球,2:小球
    odds = float(order.BET_ODDS)  # 下注时赔率
    draw_bunko = order.DRAW_BUNKO  # 平球胜负0:+,1:-
    draw_odds = int(order.DRAW_ODDS) * 0.01  # 平球赔率 %

    lose_num = int(order.LOSE_BALL_NUM)  # 让球数
    host = int(order.BET_HOST_TEAM_RESULT)  # 主队比分
    guest = int(order.BET_GUEST_TEAM_RESULT)  # 客队比分
    result = host + guest  # 主队 - 客队 = result

    user = AppUser.query.filter_by(OPENID=order.USER_ID).one_or_none()
    print("---用户ID:[" + user.USER_ID, "] 开始结算大小球订单ID:[" + order.ORDER_ID, "] 结算前用户余额:", user.TOTAL_MONEY)

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
    # 1.计算并修改玩家剩余总金额
    before_amount = float(user.TOTAL_MONEY)
    user.TOTAL_MONEY = float(user.TOTAL_MONEY) + bonus
    # 2.修改订单数据(奖金,状态,输赢)
    order.BONUS = bonus
    order.STATUS = 0
    order.IS_WIN = is_win
    order.HOST_TEAM_RESULT = host
    order.GUEST_TEAM_RESULT = guest

    # 3.插入结算记录
    settlement = Settlement(ID=str(uuid.uuid4()).replace("-", ""), TRAN_ID=order.ORDER_ID, USER_NICK_NAME=order.USER_NAME, TRAN_MONEY=bet_money, TRAN_CONTENT=order.REMARK, AGENT_PROFIT_BL=sodds, AGENT_PROFIT_MONEY=com_money, STATUS="1")
    db.session.add(settlement)
    settlement.ORDER_TYPE = order.ORDER_TYPE
    settlement.PROFIT_TYPE = "2"

    db.session.commit()

    do_app_record(user, before_amount, settlement.ID)

    # print("---用户ID:[" + user.USER_ID, "] 结算大小球订单ID:[" + order.ORDER_ID, "]完成 奖金:", bonus, " 结算后用户余额:", user.TOTAL_MONEY)


# 波胆盘
def settle_type_bodan(order, com_ratio):
    pass


# 单双盘
def settle_type_single_double(order, commission_ratio):
    bet_money = int(order.BET_MONEY)  # 下注金额
    bet_type = order.BET_TYPE  # 大小球类型,1:单,2:双
    odds = float(order.BET_ODDS)  # 下注时赔率

    host = int(order.BET_HOST_TEAM_RESULT)  # 主队比分
    guest = int(order.BET_GUEST_TEAM_RESULT)  # 客队比分
    result = host + guest  # 主队 - 客队 = result

    user = AppUser.query.filter_by(OPENID=order.USER_ID).one_or_none()
    print("---用户ID:[" + user.USER_ID, "] 开始结算大小球订单ID:[" + order.ORDER_ID, "] 结算前用户余额:", user.TOTAL_MONEY)

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
    # 1.计算并修改玩家剩余总金额
    before_amount = float(user.TOTAL_MONEY)
    user.TOTAL_MONEY = float(user.TOTAL_MONEY) + bonus
    # 2.修改订单数据(奖金,状态,输赢)
    order.BONUS = bonus
    order.STATUS = 0
    order.IS_WIN = is_win
    order.HOST_TEAM_RESULT = host
    order.GUEST_TEAM_RESULT = guest

    # 3.插入结算记录
    settlement = Settlement(ID=str(uuid.uuid4()).replace("-", ""), TRAN_ID=order.ORDER_ID, USER_NICK_NAME=order.USER_NAME, TRAN_MONEY=bet_money, TRAN_CONTENT=order.REMARK, AGENT_PROFIT_BL=odds, AGENT_PROFIT_MONEY=com_money, STATUS="1")
    db.session.add(settlement)
    settlement.ORDER_TYPE = order.ORDER_TYPE
    settlement.PROFIT_TYPE = "2"

    db.session.commit()

    do_app_record(user, before_amount, settlement.ID)


def deal_single_order(args):
    order, com_ratio = args[0], args[1]
    if order.ORDER_TYPE == "1":
        settle_type_win_lose(order, com_ratio)
    elif order.ORDER_TYPE == "2":
        settle_type_big_small(order, com_ratio)
    elif order.ORDER_TYPE == "3":
        settle_type_bodan(order, com_ratio)
    elif order.ORDER_TYPE == "6":
        settle_type_single_double(order, com_ratio)


def deal_blend_order(args):
    order, com_ratio = args[0], args[1]
    order_id = order.ORDER_ID
    order_type = order.ORDER_TYPE
    bet_money = int(order.BET_MONEY)
    com_money = 0
    # 保存所有需要结算的订单
    need_settle_orders = []
    # if order_id != "1575800477932":
    #     return
    # 所有关联的订单
    link_orders = Order.query.filter_by(ORDER_ID=order_id).all()
    # link_matches = []

    match_to_order = {l_order.MATCH_ID: l_order for l_order in link_orders}
    # match_to_order = {}
    # 关联订单与比赛
    link_matches = Match.query.filter(Match.MATCH_ID.in_(match_to_order.keys())).all()

    # 2.根据订单的比赛号查询该混合下注的所有比赛
    running_matches = [match for match in link_matches if match.IS_GAME_OVER == "0" and match.MATCH_ID != order.MATCH_ID]
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
        is_win, sodds = count_match_bunko(link_order)

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
    print("明明有比赛未完成 我草:", running_matches, is_win)
    if len(running_matches) and is_win != "0":
        return

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
    # 1.计算并修改玩家剩余总金额
    user = AppUser.query.filter_by(OPENID=order.USER_ID).one_or_none()
    print('结算前余额:', user.TOTAL_MONEY)
    before_amount = float(user.TOTAL_MONEY)
    user.TOTAL_MONEY = float(user.TOTAL_MONEY) + odds_money

    # 2.修改订单数据(奖金,状态,输赢)
    for link_order in link_orders:
        link_order.BONUS = odds_money
        link_order.STATUS = 0
        link_order.IS_WIN = is_win

    # 3.插入结算记录
    settlement = Settlement(ID=str(uuid.uuid4()).replace("-", ""), TRAN_ID=order.ORDER_ID, IS_WIN=is_win, BONUS=odds_money, USER_NICK_NAME=order.USER_NAME, TRAN_MONEY=bet_money, TRAN_CONTENT="混合单结算", AGENT_PROFIT_BL=total_odds, AGENT_PROFIT_MONEY=com_money, STATUS="1")
    db.session.add(settlement)
    settlement.ORDER_TYPE = order_type
    settlement.PROFIT_TYPE = "2"

    print("订单:", order_id, '最终结算结果输赢:', is_win, "奖金:", odds_money, '结算后余额:', user.TOTAL_MONEY)

    db.session.commit()

    do_app_record(user, before_amount, settlement.ID)


def count_match_bunko(order):
    orderType = order.ORDER_TYPE  # 订单类型:1胜负2大小3波胆,4混合胜负,5混合大小6单笔单双7混合单双
    bet_type = order.BET_TYPE  # 下注类型,1主胜,2客胜
    ball_type = order.BALL_TYPE  # 大小球类型,1:大球,2:小球
    odds = float(order.BET_ODDS)  # 订单下注时赔率
    draw_bunko = order.DRAW_BUNKO  # 平局胜负0: +, 1: -
    draw_odds = int(order.DRAW_ODDS or "0")  # 平局赔率 %
    lose_team = order.LOSE_TEAM  # 让球方1: 主队, 2: 客队
    lose_num = int(order.LOSE_BALL_NUM or '0')  # 让球数
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
    bet_money = float(order.BET_MONEY)  # 下注金额

    host = int(order.BET_HOST_TEAM_RESULT)  # 主队比分
    guest = int(order.BET_GUEST_TEAM_RESULT)  # 客队比分

    bonus = bet_money
    is_win = 1

    user = AppUser.query.filter_by(OPENID=order.USER_ID).one_or_none()
    print("---用户ID:[" + user.USER_ID, "] 开始取消订单ID:[" + order.ORDER_ID, "] 取消前用户余额:", user.TOTAL_MONEY)

    # 三.修改用户金额并保存结算记录
    # 1.计算并修改玩家剩余总金额
    before_amount = float(user.TOTAL_MONEY)
    user.TOTAL_MONEY = float(user.TOTAL_MONEY) + bonus

    # 2.修改订单数据(奖金,状态,输赢)
    order.BONUS = bonus
    order.STATUS = 0
    order.IS_WIN = is_win
    order.HOST_TEAM_RESULT = host
    order.GUEST_TEAM_RESULT = guest

    # 3.插入结算记录
    settlement = Settlement(ID=str(uuid.uuid4()).replace("-", ""), TRAN_ID=order.ORDER_ID, USER_NICK_NAME=order.USER_NAME, TRAN_MONEY=bet_money, TRAN_CONTENT=order.REMARK, AGENT_PROFIT_BL="1", AGENT_PROFIT_MONEY="0", STATUS="1")
    db.session.add(settlement)
    settlement.ORDER_TYPE = order.ORDER_TYPE
    settlement.PROFIT_TYPE = "2"

    db.session.commit()

    do_app_record(user, before_amount, settlement.ID, AppOpType.CANCEL)

    print("---用户ID:[" + user.USER_ID, "] 完成取消订单ID:[" + order.ORDER_ID, "]完成 奖金:", bonus, " 取消后用户余额:", user.TOTAL_MONEY)


def cancel(match_id):
    # 提交比赛比分
    the_match = Match.query.filter_by(MATCH_ID=match_id).one_or_none()
    the_match.HOST_TEAM_RESULT = 100
    the_match.GUEST_TEAM_RESULT = 100
    db.session.commit()

    order_q = Order.query.filter(Order.MATCH_ID == match_id)

    # 更新订单比分结果
    order_q.update({Order.BET_HOST_TEAM_RESULT: 100, Order.BET_GUEST_TEAM_RESULT: 100})
    db.session.commit()

    # 单笔佣金比例
    # single_ratio = int(MDict.query.filter_by(MDICT_ID="555").one().CONTENT) * 0.01

    # 查询所有单笔订单
    single_orders = order_q.filter(Order.IS_MIX == "0").all()
    # single_orders = [(order, single_ratio) for order in single_orders]
    print("got single orders:", single_orders)
    start = time.time()
    # 多进程结算
    for order in single_orders:
        cancel_single(order)

    db.session.commit()

    end = time.time()
    print("---结算比赛ID为:[", match_id, "]的 单笔 单用时----:", end - start, "秒")

    start = time.time()

    # 1.查询出包含该比赛号,并且有效,混合注的订单
    blend_orders = order_q.filter(and_(Order.IS_MIX == "1", Order.STATUS != "0")).all()
    # 混合佣金比例
    blend_ratio = int(MDict.query.filter_by(MDICT_ID="666").one().CONTENT) * 0.01
    blend_order_list = [(order, blend_ratio) for order in blend_orders]

    # 多进程结算
    for order in blend_order_list:
        deal_blend_order(order)
    db.session.commit()

    end = time.time()

    the_match.IS_GAME_OVER = "1"
    db.session.commit()

    print("---结算比赛ID为:[", match_id, "]的 混合 单用时----:", end - start, "秒")
    return 1


def settle(match_id, host_team_result, guest_team_result):
    try:
        # 提交比赛比分
        the_match = Match.query.filter_by(MATCH_ID=match_id).one_or_none()
        the_match.HOST_TEAM_RESULT = host_team_result
        the_match.GUEST_TEAM_RESULT = guest_team_result
        db.session.commit()

        # 单笔佣金比例
        single_ratio = int(MDict.query.filter_by(MDICT_ID="555").one().CONTENT) * 0.01

        order_q = Order.query.filter(Order.MATCH_ID == match_id)
        # 更新订单比分结果
        order_q.update({Order.BET_HOST_TEAM_RESULT: host_team_result, Order.BET_GUEST_TEAM_RESULT: guest_team_result})
        db.session.commit()

        # 查询所有单笔订单
        single_orders = order_q.filter(Order.IS_MIX == "0").all()
        print("got single orders:", single_orders)
        order_list = [(order, single_ratio) for order in single_orders]
        start = time.time()
        for order in order_list:
            deal_single_order(order)
        # 多进程结算
        # pool = Pool(4)
        # li = pool.map(deal_single_order, order_list)
        db.session.commit()

        end = time.time()
        print("---结算比赛ID为:[", match_id, "]的 单笔 单用时----:", end - start, "秒")

        start = time.time()

        # 1.查询出包含该比赛号,并且有效,混合注的订单
        blend_orders = order_q.filter(and_(Order.IS_MIX == "1", Order.STATUS != "0")).all()
        # 混合佣金比例
        blend_ratio = int(MDict.query.filter_by(MDICT_ID="666").one().CONTENT) * 0.01
        blend_order_list = [(order, blend_ratio) for order in blend_orders]

        # 多进程结算
        for order in blend_order_list:
            deal_blend_order(order)
        # pool.map(deal_blend_order, blend_order_list)
        db.session.commit()
        end = time.time()

        the_match.IS_GAME_OVER = "1"
        print("u r not dealing it ?!", the_match, the_match.IS_GAME_OVER)
        db.session.commit()
        print("---结算比赛ID为:[", match_id, "]的 混合 单用时----:", end - start, "秒")
    except Exception as e:
        print("settle error:", e)
        traceback.print_exc()
        db.session.rollback()

    return 1


def do_app_record(user, before_amount, settle_id, opt_type=AppOpType.SETTLEMENT):
    app_opt.send({
        "user_account": user.OPENID,
        "user_name": user.NICK_NAME,
        "type": opt_type,
        "amount": before_amount,
        "balance": float(user.TOTAL_MONEY),
        "source_id": settle_id
    })
