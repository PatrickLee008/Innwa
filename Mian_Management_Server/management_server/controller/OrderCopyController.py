from flask import jsonify
from management_server import app, db, auth, user_opt, Redis
from management_server.model import GameType
from management_server.model.OrderCopyModel import OrderCopy
from management_server.model.OrderModel import Order, OrderType
from management_server.model.OrderHistoryModel import OrderHistory
from flask import g, request, jsonify, Blueprint
from management_server.utils import OrmUttil
from management_server.model.AppUserModel import AppUser
from sqlalchemy import or_, func
from datetime import datetime
from management_server.utils.sphinxapi import *
import sys
import time

r_order_copy = Blueprint('order_copy', __name__)


# 获取订单列表
@r_order_copy.route('/get', methods=['GET'])
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
                        bet_type = request.args.get('bet_type')        下注类型:1主胜,2客胜   无参表示全部
                        status = request.args.get('status')            订单状态:0无效,1有效   无参表示全部
                        is_mix = request.args.get('is_mix')            是否混合过关:0否，1是  无参表示全部
                        is_win = request.args.get('is_win')            订单结果:0、输，1、赢,  2未出结果    无参表示全部

                        is_group 0: 不需要分组 1:按order_id分组
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

    key_word = request.args.get('key_word')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    order_type = request.args.get('order_type')
    bet_type = request.args.get('bet_type')
    status = request.args.get('status')
    is_mix = request.args.get('is_mix')
    is_win = request.args.get('is_win')
    is_group = request.args.get('is_group', type=int, default=0)
    # 游戏类型 0:所有 1:比赛 2:数字
    game_type = request.args.get('game_type', type=int, default=1)

    order_list = OrderCopy.query.order_by(OrderCopy.CREATE_TIME.desc())

    if g.user.AGENT_CODE:
        users_under = AppUser.query.filter_by(AGENT_ID=g.user.AGENT_CODE).all()
        users_under = set([u.USER_ID for u in users_under])
        order_list = order_list.filter(OrderCopy.USER_ID.in_(users_under))

    if order_id:
        order_list = order_list.filter(OrderCopy.ORDER_ID == order_id)

    if key_word:
        order_list = order_list.filter(
            or_(OrderCopy.ORDER_ID.like('%{}%'.format(key_word)), OrderCopy.USER_ID.like('%{}%'.format(key_word)),
                OrderCopy.USER_NAME.like('%{}%'.format(key_word)), OrderCopy.MATCH_ID.like('%{}%'.format(key_word)),
                OrderCopy.ORDER_DESC.like('%{}%'.format(key_word)), OrderCopy.REMARK.like('%{}%'.format(key_word))))

    if match_id:
        order_list = order_list.filter(OrderCopy.MATCH_ID == match_id)
    if order_type:
        order_list = order_list.filter(OrderCopy.ORDER_TYPE == order_type)
    if bet_type:
        order_list = order_list.filter(OrderCopy.BET_TYPE == bet_type)
    if status:
        order_list = order_list.filter(OrderCopy.STATUS == status)
    if is_mix:
        order_list = order_list.filter(OrderCopy.IS_MIX == is_mix)
    if is_win:
        order_list = order_list.filter(OrderCopy.IS_WIN == is_win)
    if game_type:
        if game_type == GameType.Match:
            order_list = order_list.filter(OrderCopy.ORDER_TYPE != OrderType.Digit)
        if game_type == GameType.Digit:
            order_list = order_list.filter(OrderCopy.ORDER_TYPE == OrderType.Digit)

    if start_time:
        start_time += " 00:00:00"
        order_list = order_list.filter(OrderCopy.CREATE_TIME >= start_time)

    if end_time:
        end_time += " 23:59:59"
        order_list = order_list.filter(OrderCopy.CREATE_TIME <= end_time)

    if is_group:
        order_list = order_list.group_by(OrderCopy.ORDER_ID)

    if not order_id and game_type == GameType.Digit:
        for o in order_list:
            bet_money_sum = OrderCopy.query.with_entities(func.sum(OrderCopy.BET_MONEY)).filter(OrderCopy.ORDER_ID == o.ORDER_ID).scalar() or 0
            o.BET_MONEY = bet_money_sum

    total_bet = 0
    total_bonus = 0
    for o in order_list.all():
        total_bet += int(o.BET_MONEY)

    total = order_list.count()
    order_list = order_list.offset((current_page - 1) * limit).limit(limit).all()



    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in order_list],
        'total': total,
        'total_bet': total_bet,
        'total_bonus': total_bonus
    })

