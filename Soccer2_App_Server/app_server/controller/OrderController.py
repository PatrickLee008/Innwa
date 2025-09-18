from app_server import db, auth, app_opt, Redis
from flask import g, request, jsonify, Blueprint
from app_server.model.MDictModel import MDict
from app_server.model.MatchModel import Match, MatchAttr, VipMatchAttr
from app_server.model import GameType
from app_server.model.OrderModel import Order, OrderType, BetType
from app_server.model.OrderHistoryModel import OrderHistory
from sqlalchemy import or_, func, and_
from app_server.utils.OrmUttil import AppOpType
from app_server.utils.sphinxapi import *
import ipaddress
import datetime
import time
import uuid

order = Blueprint('order', __name__)


@order.route('/check_odds', methods=['POST'])
@auth.login_required
def check_odds():
    """
        @@@
        #### Args:
                attrs: {attr_id:{"bet_type": 1, "DRAW_ODDS": 2.3, ...}, ...}
        #### Returns::
                {'code': 20000, 'message': "check success!", items: {attr_id:odds, ...}}
                {'code': 50001, 'message': "unknown error"}
    """
    args = request.get_json()
    attrs = args.get('attrs')
    print('attrs:', attrs)
    try:
        all_attr = MatchAttr.query.filter(MatchAttr.MATCH_ATTR_ID.in_(attrs)).all()
        change_list = []
        for attr in all_attr:
            remote_attr = attrs[attr.MATCH_ATTR_ID]
            if attr.DRAW_BUNKO != remote_attr['DRAW_BUNKO'] or attr.DRAW_ODDS != remote_attr[
                'DRAW_ODDS'] or attr.LOSE_BALL_NUM != remote_attr['LOSE_BALL_NUM']:
                change_list.append(attr)

        return jsonify({'code': 20000, 'message': "check success!", 'items': [u.to_dict() for u in change_list]})

    except Exception as e:
        print("check_odds error", e)
        return jsonify({'code': 50001, 'message': "unknown error"})


@order.route('/single_bet', methods=['POST'])
@auth.login_required
def single_bet():
    """
        @@@
        #### Args:
        #### Returns::
                {'code': 20000, 'message': "下注成功"}
                {'code': 50001, 'message': "unknown error"}
    """
    args = request.get_json()
    bets = args.get('bets')

    getter_key = "order_bet_%s_%s" % (g.user.USER_ID, str(args))
    if not Redis.exists(getter_key):
        Redis.set(getter_key, 0, ex=2)
    else:
        return jsonify({'code': 50003, "message": "same bet request in very short time"})

    try:
        total_amount = 0

        user = g.user
        main_id = user.MAJUSER_ID
        del user
        from app_server.model.AppUserModel import AppUser
        db.session.commit()
        user = AppUser.query.filter_by(MAJUSER_ID=main_id).with_for_update(of=AppUser).first()

        # 先行统计总下注额
        for bet in bets:
            total_amount += float(bet['amount'])

        if float(user.TOTAL_MONEY) < total_amount:
            return jsonify({
                'code': 50002, 'message': "Sorry, your credit is not enough"
            })
        single_limit = MDict.query.filter_by(MDICT_ID="888").one()
        single_min = single_limit.CODE
        single_max = single_limit.CONTENT

        for bet in bets:
            if float(bet['amount']) < float(single_min):
                return jsonify({
                    'code': 50002, 'message': "single_min"
                })
            if float(bet['amount']) > float(single_max):
                return jsonify({
                    'code': 50002, 'message': "single_max"
                })
            match = Match.query.filter_by(MATCH_ID=bet['matchId']).one_or_none()
            if not match:
                db.session.rollback()
                return jsonify({
                    'code': 50002, 'message': "Bet failed: match not exist."
                })
            if match.CLOSING_STATE == "1":
                db.session.rollback()
                return jsonify({
                    'code': 50002, 'message': "Bet failed: game has closed."
                })
            if match.CLOSING_TIME <= datetime.datetime.now():
                db.session.rollback()
                return jsonify({
                    'code': 50002, 'message': "Bet failed: match has started."
                })

            order_type = bet['attrType']
            attrs = MatchAttr.query.filter_by(MATCH_ID=bet['matchId']).all()
            vip_attrs = VipMatchAttr.query.filter_by(MATCH_ID=bet['matchId']).all()
            vip_attr_dict = {attr.MATCH_ATTR_TYPE: attr for attr in vip_attrs}
            attr_dict = {attr.MATCH_ATTR_TYPE: attr for attr in attrs}

            attr = None
            if order_type in attr_dict:
                attr = attr_dict[order_type]
            if user.IS_VIP and order_type in vip_attr_dict:
                attr = vip_attr_dict[order_type]

            if not attr:
                db.session.rollback()
                return jsonify({
                    'code': 50002, 'message': "Bet failed: order type error"
                })

            #   总限额
            single_order_total_limit = MDict.query.filter_by(MDICT_ID="889").one().CONTENT
            match_total_unsettled = Order.query.filter(
                and_(Order.USER_ID == user.USER_ID, Order.ORDER_TYPE == order_type, Order.STATUS == "1",
                     Order.MATCH_ID == bet['matchId'])).with_entities(func.sum(Order.BET_MONEY)).scalar() or 0
            print("------", order_type, match_total_unsettled, single_order_total_limit)
            if match_total_unsettled + total_amount > int(single_order_total_limit):
                db.session.rollback()
                return jsonify({
                    'code': 50002, 'message': "Bet failed: this match has reached the order limit."
                })

            order_id = "%s-%s" % (user.USER_ID, round(time.time() * 1000))

            new_order = Order(ID=str(uuid.uuid4()).replace("-", ""), ORDER_ID=order_id, USER_ID=user.OPENID,
                              USER_NAME=user.NICK_NAME,
                              MATCH_ID=bet['matchId'], ORDER_TYPE=order_type,
                              ORDER_DESC="%s || %s" % (match.HOST_TEAM, match.GUEST_TEAM),
                              BET_MONEY=bet['amount'], REMARK="暂无", STATUS="1", IS_MIX="0", IS_WIN="2", BONUS="",
                              BET_ODDS=attr.ODDS,
                              DRAW_BUNKO=attr.DRAW_BUNKO, DRAW_ODDS=attr.DRAW_ODDS, LOSE_BALL_NUM=attr.LOSE_BALL_NUM,
                              MATCH_TIME=match.MATCH_MD_TIME, IP=int(ipaddress.IPv4Address(request.remote_addr)))
            if user.AGENT_ID:
                new_order.AGENT_CODE = user.AGENT_ID
            if order_type == "1":
                new_order.BET_TYPE = bet['betType']
                new_order.LOSE_TEAM = attr.LOSE_TEAM
            elif order_type == "2":
                new_order.BALL_TYPE = bet['betType']

            if g.user.AGENT_ID:
                new_order.AGENT_CODE = g.user.AGENT_ID

            # 单双赔率另外赋值
            if order_type == '6':
                new_order.BET_TYPE = bet['betType']
                new_order.BET_ODDS = attr.ODDS if bet['betType'] == 1 else attr.ODDS_GUEST

            # 独赢赔率另外赋值
            if order_type == '10':
                new_order.BET_TYPE = bet['betType']
                print("got to set the odds:", bet['betType'])
                new_order.BET_ODDS = attr.ODDS if bet['betType'] == 1 else attr.ODDS_GUEST
                if bet['betType'] == 3:
                    new_order.BET_ODDS = attr.DRAW_ODDS
                print("set result", new_order.BET_ODDS)

            before_amount = float(user.TOTAL_MONEY)  # before_amount:321456.1125,bet_money:5003.0

            # print('before_amount:%s,bet_money:%s' % (before_amount, float(bet['amount'])))

            user.TOTAL_MONEY = before_amount - float(bet['amount'])
            after_amount = before_amount - float(bet['amount'])

            # print('after_money', float(user.TOTAL_MONEY))    # 输出  after_money：316453.1125

            db.session.add(new_order)
            db.session.commit()
            # print('after_money_commit', float(user.TOTAL_MONEY))  # 输出 after_money_commit：321456.1125

            app_opt.send({
                "user_account": user.OPENID,
                "user_name": user.NICK_NAME,
                "type": AppOpType.BET,
                "amount": before_amount,
                "balance": float(after_amount),
                "source_id": order_id,
                "match_id": bet['matchId']
            })

        return jsonify({'code': 20000, 'message': "Bet success!"})

    except Exception as e:
        print("single bet error", e)
        db.session.rollback()
        return jsonify({'code': 50001, 'message': "unknown error"})


@order.route('/mix_bet', methods=['POST'])
@auth.login_required
def mix_bet():
    """
                @@@
                #### Args:
                        bets:[
                            {
                                matchId:
                                attrType:
                                betType:
                            }
                        ]
                        totalAmount
                #### Returns::
                        {'code': 20000, 'message': "Bet success!"}
                        {'code': 50001, 'message': "unknown error"}
            """
    args = request.get_json()
    bets = args.get('bets')
    # getter_key = "order_bet_%s_%s" % (g.user.USER_ID, str(args))

    getter_key = "order_bet_%s" % (g.user.USER_ID)
    success = Redis.setnx(getter_key, 1)  # SETNX命令
    if not success:
        return jsonify({'code': 50003, "message": "same bet request in very short time"})

    # 设置键的过期时间
    Redis.expire(getter_key, 2)

    # if not Redis.exists(getter_key):
    #     Redis.set(getter_key, 0, ex=2)
    # else:
    #     return jsonify({'code': 50003, "message": "same bet request in very short time"})

    order_id = int(round(time.time() * 1000))
    # 直接给出总金额
    total_amount = float(args.get('totalAmount'))
    print("about to bet:", order_id, bets)

    try:
        mix_limit = MDict.query.filter_by(MDICT_ID="999").one()
        bet_count_limit = MDict.query.filter_by(MDICT_ID="13").one()
        mix_min = mix_limit.CODE
        mix_max = mix_limit.CONTENT
        order_id = "%s-%s" % (g.user.USER_ID, round(time.time() * 1000))

        user = g.user
        main_id = user.MAJUSER_ID
        del user
        from app_server.model.AppUserModel import AppUser
        db.session.commit()
        user = AppUser.query.filter_by(MAJUSER_ID=main_id).with_for_update(of=AppUser).first()

        if total_amount < float(mix_min):
            return jsonify({
                'code': 50002, 'message': "mix_min"
            })
        if total_amount > float(mix_max):
            return jsonify({
                'code': 50002, 'message': "mix_max"
            })
        # match_ids = {bet['matchId'] for bet in bets}

        # 单场比赛混合下注判断
        # mix_orders = Order.query.with_entities(Order., Order.ORDER_ID).filter(Order.IS_MIX == "1", Order.STATUS == "1", Order.MATCH_ID.in_(match_ids), Order.USER_ID == user.USER_ID)

        match_to_orders = {}
        new_orders = []
        if len(bets) < int(bet_count_limit.CODE):
            return jsonify({
                'code': 50002, 'message': "Bet failed: Choose at least %s games." % bet_count_limit.CODE
            })
        if len(bets) > int(bet_count_limit.CONTENT):
            return jsonify({
                'code': 50002, 'message': "Bet failed: Choose most %s games." % bet_count_limit.CONTENT
            })

        if len(set([bet['matchId'] for bet in bets])) < len(bets):
            return jsonify({
                'code': 50002, 'message': "Repeat Match"
            })

        mix_type_dict = {}

        for bet in bets:
            match_id = bet['matchId']
            order_type = bet['attrType']

            already_bet = mix_type_dict.get(match_id)
            if not already_bet:
                mix_type_dict[match_id] = already_bet = set()

            if order_type in already_bet:
                print(">>>>illegal bet found:", g.user.USER_ID, datetime.datetime.now(), args, request.remote_addr)
                return jsonify({
                    'code': 50002, 'message': "Bet failed: bet data illegal."
                })

            mix_type_dict[match_id].add(order_type)

            match = Match.query.filter_by(MATCH_ID=bet['matchId']).one_or_none()
            if not match:
                db.session.rollback()
                return jsonify({
                    'code': 50002, 'message': "Bet failed: match not exist."
                })
            # arthur 如果匹配被隐藏且隐私原因非空，则不允许下注
            if match.hide == '1' and match.HIDE_REASON is not None and match.HIDE_REASON != "":
                return jsonify({
                    'code': 500020, 'message': "Bet failed: match is hidden."
                })
            if match.CLOSING_STATE == "1":
                db.session.rollback()
                return jsonify({
                    'code': 50002, 'message': "Bet failed: game has closed."
                })
            if match.CLOSING_TIME <= datetime.datetime.now():
                db.session.rollback()
                return jsonify({
                    'code': 50002, 'message': "Bet failed: match has started."
                })

            # 混合单31限制
            if user.HIGHER_LIMIT:
                mix_total_match_limit = MDict.query.filter_by(MDICT_ID="33").one()
            else:
                mix_total_match_limit = MDict.query.filter_by(MDICT_ID="31").one()

            link_orders = Order.query.filter(Order.MATCH_ID == bet['matchId'], Order.USER_ID == user.USER_ID,
                                             Order.STATUS == 1, Order.IS_MIX == "1").group_by(Order.ORDER_ID).all()
            match_already_bet = 0
            for link_order in link_orders:
                match_already_bet += int(link_order.BET_MONEY)

            if match_already_bet + total_amount > float(mix_total_match_limit.CONTENT):
                return jsonify({
                    'code': 50002, 'message': "Bet failed: this match has reached the order limit."
                })

            attrs = MatchAttr.query.filter_by(MATCH_ID=bet['matchId']).all()
            vip_attrs = VipMatchAttr.query.filter_by(MATCH_ID=bet['matchId']).all()
            vip_attr_dict = {attr.MATCH_ATTR_TYPE: attr for attr in vip_attrs}
            attr_dict = {attr.MATCH_ATTR_TYPE: attr for attr in attrs}

            attr = None
            if order_type in attr_dict:
                attr = attr_dict[order_type]
            if user.IS_VIP and order_type in vip_attr_dict:
                attr = vip_attr_dict[order_type]

            if not attr:
                db.session.rollback()
                return jsonify({
                    'code': 50002, 'message': "Bet failed: order type error"
                })

            new_order = Order(ID=str(uuid.uuid4()).replace("-", ""), ORDER_ID=order_id, USER_ID=user.OPENID,
                              USER_NAME=user.NICK_NAME,
                              MATCH_ID=bet['matchId'], ORDER_TYPE=order_type,
                              ORDER_DESC="%s || %s" % (match.HOST_TEAM, match.GUEST_TEAM),
                              BET_MONEY=total_amount, REMARK="%s串1" % len(bets), STATUS="1", IS_MIX="1", IS_WIN="2",
                              BONUS="", MATCH_TIME=match.MATCH_MD_TIME,
                              BET_ODDS=attr.ODDS, DRAW_BUNKO=attr.DRAW_BUNKO, DRAW_ODDS=attr.DRAW_ODDS,
                              LOSE_BALL_NUM=attr.LOSE_BALL_NUM, IP=int(ipaddress.IPv4Address(request.remote_addr)))
            print("mix bet ordering:", order_type, bet['betType'])
            if user.AGENT_ID:
                new_order.AGENT_CODE = user.AGENT_ID
            if order_type == "4":
                new_order.BET_TYPE = bet['betType']
                new_order.LOSE_TEAM = attr.LOSE_TEAM
            elif order_type == "5":
                new_order.BALL_TYPE = bet['betType']
            if g.user.AGENT_ID:
                new_order.AGENT_CODE = g.user.AGENT_ID

            # 单双赔率另外赋值
            if order_type == '7':
                new_order.BET_TYPE = bet['betType']
                new_order.BET_ODDS = attr.ODDS if bet['betType'] == '1' else attr.ODDS_GUEST

            new_orders.append(new_order)
            match_to_orders[bet['matchId']] = new_order
        if float(user.TOTAL_MONEY) < total_amount:
            db.session.rollback()
            return jsonify({
                'code': 50002, 'message': "Sorry, your credit is not enough"
            })

        # 统计同类混合单的注额 进行限制
        if user.HIGHER_LIMIT:
            mix_order_total_limit = MDict.query.filter_by(MDICT_ID="32").one()
        else:
            mix_order_total_limit = MDict.query.filter_by(MDICT_ID="30").one()
        mix_already = Order.query.with_entities(func.count(Order.ID), Order.ORDER_ID).filter(
            Order.USER_ID == user.USER_ID, Order.STATUS == 1, Order.IS_MIX == "1").group_by(Order.ORDER_ID).all()
        same_order_ids = []
        for length, o_id in mix_already:
            if length != len(bets):
                continue
            same_order_ids.append(o_id)

        print("got same:", same_order_ids)
        count_amount = 0
        for o_id in same_order_ids:
            orders = Order.query.filter_by(ORDER_ID=o_id).all()
            is_same = True
            for o in orders:
                if o.MATCH_ID not in match_to_orders:
                    is_same = False
                    break
                s = match_to_orders[o.MATCH_ID]

                is_same = compare(s.BET_TYPE, o.BET_TYPE) and compare(s.ORDER_TYPE, o.ORDER_TYPE) and compare(
                    s.BALL_TYPE, o.BALL_TYPE)
                if not is_same:
                    break
            print("order:", o_id, "compare result:", is_same)
            if is_same:
                count_amount += float(orders[0].BET_MONEY)

        print("we got same orders with order_id: %s bet_amount: %s others: " % (order_id, count_amount), same_order_ids)

        if count_amount + total_amount > float(mix_order_total_limit.CONTENT):
            print("reaching limit:", count_amount + total_amount, float(mix_order_total_limit.CONTENT))
            db.session.rollback()
            return jsonify({
                'code': 50002, 'message': "mix_order_total"
            })

        for o in new_orders:
            db.session.add(o)

        before_amount = float(user.TOTAL_MONEY)
        user.TOTAL_MONEY = before_amount - total_amount
        after_amount = before_amount - total_amount

        db.session.commit()

        app_opt.send({
            "user_account": user.OPENID,
            "user_name": user.NICK_NAME,
            "type": AppOpType.BET,
            "amount": before_amount,
            "balance": float(after_amount),
            "source_id": order_id
        })

        return jsonify({'code': 20000, 'message': "bet success!"})
    except Exception as e:
        print("mix bet error", e)
        return jsonify({'code': 50001, 'message': "unknown error"})


def compare(a, b):
    if a and b:
        return str(a) == str(b)
    return a == b


# 获取订单列表
@order.route('/get_history', methods=['GET'])
@auth.login_required
def get_order_history():
    """
                @@@
                #### Args:
                        current_page = request.args.get('page', type=int, default=1)
                        limit = request.args.get('limit', type=int, default=20)
                        order_id = request.args.get('order_id')

                        key_word = request.args.get('key_word')
                        start_time = request.args.get('start_time')
                        end_time = request.args.get('end_time')

                        order_type = request.args.get('order_type')    订单类型:1胜负(让球)2大小球3波胆 无参表示全部
                        order_types = request.args.get('order_types')  订单类型多选
                        bet_type = request.args.get('bet_type')        下注类型:1主胜,2客胜   无参表示全部
                        status = request.args.get('status')            订单状态:0无效,1有效   无参表示全部
                        is_mix = request.args.get('is_mix')            是否混合过关:0否，1是  无参表示全部
                        is_win = request.args.get('is_win')            订单结果:0、输，1、赢,  2未出结果    无参表示全部
                #### Returns::
                        {
                            'code': 20000,
                            'items': [u.to_dict() for u in order_list],
                            'total': total,
                            'total_bet': total_bet,       下注总金额
                            'total_bonus': total_bonus    总奖金
                        }
            """
    # return jsonify({'code': 50001, "message": "under maintence"})
    repeat_key = 'query_history_%s' % g.user.USER_ID
    Redis.get(repeat_key)
    is_detail = request.args.get('is_detail', type=bool, default=False)
    if Redis.get(repeat_key) and not is_detail:
        return jsonify({'code': 50001, "message": "Please wait for 60 second"})
    else:
        Redis.set(repeat_key, 1, ex=3)
    current_page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)
    order_id = request.args.get('order_id')

    match_id = request.args.get('match_id')

    key_word = request.args.get('key_word')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    order_type = request.args.get('order_type')
    order_types = request.args.get('order_types')
    # 游戏类型 0:所有 1:比赛 2:数字
    game_type = request.args.get('game_type', type=int, default=1)
    bet_type = request.args.get('bet_type')
    is_mix = request.args.get('is_mix')
    is_win = request.args.get('is_win')

    cl = SphinxClient()
    cl.SetServer('localhost', 9312)
    cl.SetLimits((current_page - 1) * limit, limit)
    print("????", (current_page - 1) * limit)
    cl.SetSortMode(SPH_SORT_ATTR_DESC, "id")
    print("getting order_history with:", request.args)

    total = 0

    query_str = "@USER_ID %s" % g.user.USER_ID

    if key_word:
        query_str += key_word

    if order_id:
        query_str += "@ORDER_ID %s" % order_id
    if match_id:
        query_str += "@MATCH_ID %s" % match_id
    if order_type:
        cl.SetFilter('ORDER_TYPE', [int(order_type)])
    if bet_type:
        cl.SetFilter('BET_TYPE', [bet_type])
    if is_mix:
        cl.SetFilter('IS_MIX', [int(is_mix)])
    if is_win:
        cl.SetFilter('IS_WIN', [int(is_win)])
    if not is_detail:
        cl.SetGroupBy('ORDER_GROUP', SPH_GROUPBY_ATTR, 'id desc')
    if game_type:
        if game_type == GameType.Match:
            cl.SetFilter('ORDER_TYPE', [1, 2, 3, 4, 5, 6, 7, 10])
        if game_type == GameType.Digit:
            cl.SetFilter('ORDER_TYPE', [8])

    if start_time:
        start_time += " 00:00:00"
        time_array = time.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        now_ts = int(time.time())
        start_time = int(time.mktime(time_array))
        cl.SetFilterRange('CREATE_TIME', start_time, now_ts)

    if end_time:
        end_time += " 23:59:59"
        time_array = time.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        ts = int(time.mktime(time_array))
        cl.SetFilterRange('CREATE_TIME', start_time or 0, ts)

    print("filter str:", query_str)

    res = cl.Query(query_str, 'order_history;order_history_add')

    whole = {}
    order_ids = {}
    if res:
        whole = {w['id'] for w in res['matches']}
        order_ids = {w["attrs"]['order_group'] for w in res['matches']}
        total = res['total_found']
        print("order_history:", (current_page - 1) * limit, res['total_found'], res['total'])

    print("got result:", len(whole))
    order_list = OrderHistory.query.filter(OrderHistory.ID.in_(whole))

    result = []
    if not is_detail:
        order_list = order_list.group_by(OrderHistory.ORDER_ID).all()
        # _sum = OrderHistory.query.filter(OrderHistory.ORDER_TYPE == '8',
        #                                  OrderHistory.ORDER_ID.in_(order_ids)).with_entities(func.sum(OrderHistory.BONUS),
        #                                                                                      func.sum(OrderHistory.BET_MONEY), OrderHistory.ORDER_ID,
        #                                                                                      func.sum(OrderHistory.IS_WIN)).group_by(OrderHistory.ORDER_ID).all()
        # sum_dict = {}
        # for bonus, bet_money, order_id, id_win in _sum:
        #     # print("---", type(bonus), type(bet_money), type(id_win))
        #     # print("---", bonus, bet_money, id_win, order_ids)
        #     sum_dict[order_id] = {
        #         "BONUS": str(bonus),
        #         "BET_MONEY": str(bet_money),
        #         "IS_WIN": int(id_win),
        #     }
        for u in order_list:
            temp = u.to_dict()
            # if u.ORDER_ID in sum_dict:
            #     temp.update(sum_dict[u.ORDER_ID])
            result.append(temp)
        return jsonify({
            'code': 20000,
            'items': result,
            'total': total

        })

    order_list = order_list.all()
    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in order_list],
        'total': total

    })


# 获取订单列表
@order.route('/get', methods=['GET'])
@auth.login_required
def get_order_list():
    """
                @@@
                #### Args:
                        current_page = request.args.get('page', type=int, default=1)
                        limit = request.args.get('limit', type=int, default=20)
                        order_id = request.args.get('order_id')

                        key_word = request.args.get('key_word')
                        start_time = request.args.get('start_time')
                        end_time = request.args.get('end_time')

                        order_type = request.args.get('order_type')    订单类型:1胜负(让球)2大小球3波胆 无参表示全部
                        order_types = request.args.get('order_types')  订单类型多选
                        bet_type = request.args.get('bet_type')        下注类型:1主胜,2客胜   无参表示全部
                        status = request.args.get('status')            订单状态:0无效,1有效   无参表示全部
                        is_mix = request.args.get('is_mix')            是否混合过关:0否，1是  无参表示全部
                        is_win = request.args.get('is_win')            订单结果:0、输，1、赢,  2未出结果    无参表示全部
                #### Returns::
                        {
                            'code': 20000,
                            'items': [u.to_dict() for u in order_list],
                            'total': total,
                            'total_bet': total_bet,       下注总金额
                            'total_bonus': total_bonus    总奖金
                        }
            """

    current_page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)
    order_id = request.args.get('order_id')

    match_id = request.args.get('match_id')
    is_detail = request.args.get('is_detail')

    key_word = request.args.get('key_word')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    order_type = request.args.get('order_type')
    order_types = request.args.get('order_types')
    bet_type = request.args.get('bet_type')
    status = request.args.get('status')
    is_mix = request.args.get('is_mix')
    is_win = request.args.get('is_win')
    # 游戏类型 0:所有 1:比赛 2:数字
    game_type = request.args.get('game_type', type=int, default=1)

    order_list = Order.query.filter(Order.USER_ID == g.user.OPENID, Order.STATUS == "1")

    # if g.user.AGENT_CODE:
    #     users_under = AppUser.query.filter_by(AGENT_ID=g.user.AGENT_CODE).all()
    #     users_under = set([u.USER_ID for u in users_under])
    #     order_list = order_list.filter(Order.USER_ID.in_(users_under))

    if order_id:
        order_list = order_list.filter(Order.ORDER_ID == order_id)

    if key_word:
        order_list = order_list.filter(
            or_(Order.ORDER_ID.like('%{}%'.format(key_word)), Order.USER_ID.like('%{}%'.format(key_word)),
                Order.USER_NAME.like('%{}%'.format(key_word)), Order.MATCH_ID.like('%{}%'.format(key_word)),
                Order.ORDER_DESC.like('%{}%'.format(key_word)), Order.REMARK.like('%{}%'.format(key_word))))

    if match_id:
        order_list = order_list.filter(Order.MATCH_ID == match_id)
    if order_type:
        order_list = order_list.filter(Order.ORDER_TYPE == order_type)
    if bet_type:
        order_list = order_list.filter(Order.BET_TYPE == bet_type)
    if order_types:
        order_list = order_list.filter(Order.BET_TYPE.in_(order_types.split(",")))
    if status:
        order_list = order_list.filter(Order.STATUS == status)
    if is_mix:
        order_list = order_list.filter(Order.IS_MIX == is_mix)
    if is_win:
        order_list = order_list.filter(Order.IS_WIN == is_win)
    if game_type:
        if game_type == GameType.Match:
            order_list = order_list.filter(Order.ORDER_TYPE != OrderType.Digit)
        if game_type == GameType.Digit:
            order_list = order_list.filter(Order.ORDER_TYPE == OrderType.Digit)

    if start_time:
        start_time += " 00:00:00"
        order_list = order_list.filter(Order.CREATE_TIME >= start_time)

    if end_time:
        end_time += " 23:59:59"
        order_list = order_list.filter(Order.CREATE_TIME <= end_time)

    if not is_detail:
        order_list = order_list.group_by(Order.ORDER_ID)
        if game_type and game_type == GameType.Digit:
            order_list = order_list.with_entities(Order, func.sum(Order.BET_MONEY))
            order_list = order_list.offset((current_page - 1) * limit).limit(limit).all()
            result = []
            for u in order_list:
                temp = u[0].to_dict()
                temp['BET_MONEY'] = int(u[1])
                result.append(temp)
            return jsonify({
                'code': 20000,
                'items': result,
                'total': len(result)
            })

    order_list = order_list.offset((current_page - 1) * limit).limit(limit).all()
    total = len(order_list)
    # print("the ret:", [u.to_dict() for u in order_list])

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in order_list],
        'total': total
    })
