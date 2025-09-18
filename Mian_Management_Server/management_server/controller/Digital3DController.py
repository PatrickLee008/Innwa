from management_server import app, db, auth, user_opt
from flask import jsonify, Blueprint, request, g
from management_server.model.Digital3DModel import Digital3D, Digit3DStatus
from management_server.model.OrderModel import Order, OrderType
from management_server.model.OrderHistoryModel import OrderHistory
from management_server.utils.sphinxapi import *
from management_server.model.MatchSettleModel import MatchSettle, SettleStatus, SettleType, GameType
from sqlalchemy import or_, func
from management_server.utils import OrmUttil
import time
from datetime import datetime, timedelta

r_digital_3d = Blueprint('digital_3d', __name__)


@r_digital_3d.route('/get', methods=['GET'])
@auth.login_required
def get_digital_3d_list():
    """
                    @@@
                    #### Args:
                           {
                                current_page: "",
                                limit: "",
                                key_word: "",
                                start_time: "",
                                end_time: "",
                            }
                    #### Returns::
                            {
                                'code': 20000,
                                'items': [u.to_dict() for u in digital_3d_list],
                            }
                """
    current_page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)
    key_word = request.args.get('key_word')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    digital_3d_list = Digital3D.query.order_by(Digital3D.ID.desc())
    if key_word:
        digital_3d_list = digital_3d_list.filter(
            or_(Digital3D.ID.like('%{}%'.format(key_word)), Digital3D.TITLE.like('%{}%'.format(key_word)),
                Digital3D.CONTENT.like('%{}%'.format(key_word))))

    if start_time:
        digital_3d_list = digital_3d_list.filter(Digital3D.CREATE_TIME >= start_time)

    if end_time:
        end_time += ' 23:59:59'
        digital_3d_list = digital_3d_list.filter(Digital3D.CREATE_TIME <= end_time)

    total, total_bet_count, total_bet_sum, total_benefit = digital_3d_list.with_entities(func.count(Digital3D.ID),
                                                                                         func.sum(Digital3D.BET_NUM),
                                                                                         func.sum(Digital3D.BET_SUM),
                                                                                         func.sum(Digital3D.BENEFIT)).one()
    print("-----", total, total_bet_count, total_bet_sum, total_benefit)

    digital_3d_list = digital_3d_list.offset((current_page - 1) * limit).limit(limit).all()

    total_benefit = int(total_benefit or 0)
    print("the shit:", total_benefit, type(total_benefit))

    return jsonify({
        'code': 20000,
        'items': [u.to_dict() for u in digital_3d_list],
        'total': int(total),
        'total_bet_count': int(total_bet_count or 0),
        'total_bet_sum': int(total_bet_sum or 0),
        'total_benefit': int(total_benefit or 0)

    })


@r_digital_3d.route('/get_detail', methods=['GET'])
@auth.login_required
def get_digital_3d_detail():
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

    match_id = request.args.get('match_id')
    order_list = Order.query.filter(Order.STATUS == "1")

    digit_stage = Digital3D.query.filter_by(ID=match_id).first()

    if match_id:
        order_list = order_list.filter(Order.MATCH_ID == match_id)

    order_list = order_list.filter(Order.ORDER_TYPE == OrderType.Digit)

    order_list = order_list.group_by(Order.BET_TYPE)
    _sum = Order.query.filter(Order.ORDER_TYPE == OrderType.Digit,
                              Order.MATCH_ID == match_id).with_entities(Order.BET_TYPE,
                                                                        func.sum(Order.BET_MONEY)).group_by(
        Order.BET_TYPE).all()

    order_list = order_list.all()

    result = []
    sum_dict = {}

    for bet_type, bet_money in _sum:
        # print("---", type(bonus), type(bet_money), type(id_win))
        sum_dict[bet_type] = {
            "BET_MONEY": str(bet_money),
            "LIMIT_NUM": digit_stage.LIMIT_NUM
        }
    for u in order_list:
        temp = u.to_dict()
        if u.BET_TYPE in sum_dict:
            temp.update(sum_dict[u.BET_TYPE])
        result.append(temp)
    total = len(result)
    # print("the ret:", [u.to_dict() for u in order_list])

    return jsonify({
        'code': 20000,
        'items': result,
        'total': total
    })


@r_digital_3d.route('/get_history_detail', methods=['GET'])
@auth.login_required
def get_digital_3d_history_detail():
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

    # order_type = request.args.get('order_type', type=int)
    order_type = 8

    cl = SphinxClient()
    cl.SetServer('localhost', 9312)
    cl.SetConnectTimeout(10.0)
    cl.SetLimits((current_page - 1) * limit, limit)
    cl.SetSortMode(SPH_SORT_ATTR_DESC, "id")

    query_str = ""

    if key_word:
        query_str += key_word

    if order_id:
        query_str += "@ORDER_ID %s" % order_id
    if match_id:
        query_str += "@MATCH_ID %s" % match_id
    if order_type:
        cl.SetFilter('ORDER_TYPE', [order_type])

    if g.user.AGENT_CODE:
        query_str += "@AGENT_CODE %s" % g.user.AGENT_CODE

    print("final query str:", query_str)

    res = cl.Query(query_str, 'order_history;order_history_add')

    whole = {}
    if res:
        whole = {w['id'] for w in res['matches']}

    order_list = OrderHistory.query.filter(OrderHistory.ID.in_(whole)).all()
    _sum = OrderHistory.query.filter(OrderHistory.ID.in_(whole)).with_entities(OrderHistory.BET_TYPE, func.sum(
        OrderHistory.BET_MONEY)).group_by(OrderHistory.BET_TYPE).all()

    result = []
    sum_dict = {}
    for bet_type, bet_money in _sum:
        # print("---", type(bonus), type(bet_money), type(id_win))
        sum_dict[bet_type] = {
            "BET_MONEY": str(bet_money),
        }
    for u in order_list:
        temp = u.to_dict()
        if u.BET_TYPE in sum_dict:
            temp.update(sum_dict[u.BET_TYPE])
        result.append(temp)
    total = len(result)

    return jsonify({
        'code': 20000,
        'items': result,
        'total': total,
    })


# 结算比赛
@r_digital_3d.route('/settle', methods=['POST'])
# @auth.login_required
def settle_digit():
    """
        @@@
        #### Args:
                digit_id
        #### Returns::
                {'code': 20000, 'message': "添加成功"}
                {'code': 50001, 'message': "未知错误"}
        """

    args = request.get_json()
    digit_id = args.get("digit_id")
    print("settle_digit", args)

    try:
        digit = Digital3D.query.filter_by(ID=digit_id).first()

        if not digit:
            return jsonify({'code': 50002, 'message': "digit3d does not exist"})
        if digit.STATUS == Digit3DStatus.Settled:
            return jsonify({'code': 50002, 'message': "digit3d is game over."})
        settle = MatchSettle.query.filter(MatchSettle.MATCH_ID == digit_id,
                                          MatchSettle.SETTLE_TYPE == SettleType.SETTLE,
                                          MatchSettle.STATUS != SettleStatus.FINISHED).first()
        if settle:
            return jsonify({'code': 50002, 'message': "digit3d is already under settle."})

        settle = MatchSettle(MATCH_ID=digit_id, STATUS=SettleStatus.WAIT, SETTLE_TYPE=SettleType.SETTLE,
                             GAME_TYPE=GameType.Digit3D)

        db.session.add(settle)
        db.session.commit()
        return jsonify({'code': 20000, 'message': "添加成功"})
    except Exception as e:
        print("add digit_settle error:", e)

    return jsonify({'code': 50001, 'message': "未知错误"})


@r_digital_3d.route('/edit', methods=['POST'])
@auth.login_required
def edit_digital_3d():
    """
    @@@
    #### Args:
            {
               "ID": '1553335644871',
               "TITLE": "",
               "CONTENT": "",
            }
    #### Returns::
            {'code': 20000, 'message': "修改成功"}
            {'code': 50001, 'message': "未知错误"}
    """
    args = request.get_json()
    edit_id = args.get('ID')
    print("edit_digital_3d", args)
    try:
        digital_3d = Digital3D.query.filter_by(ID=edit_id).one_or_none()
        if 'OPEN_TIME' in args:
            args['OPEN_TIME'] = datetime.strptime(args['OPEN_TIME'], "%Y-%m-%d %H:%M:%S") + timedelta(hours=1.5)
        if 'CLOSE_TIME' in args:
            args['CLOSE_TIME'] = datetime.strptime(args['CLOSE_TIME'], "%Y-%m-%d %H:%M:%S") + timedelta(hours=1.5)
        OrmUttil.set_field(digital_3d, args)
        print("whose doing this shit?", g.user.ACCOUNT)
        digital_3d.UPDATER = g.user.ACCOUNT
        db.session.commit()
        user_opt.send({
            "operate": "修改3d数字盘",
            "route": "3d数字盘管理",
            "key_word": edit_id,
            "user": g.user.ACCOUNT
        })
        return jsonify({'code': 20000, 'message': "修改成功"})
    except Exception as e:
        print(e)
        return jsonify({
            'code': 50001,
            'message': "未知错误"
        })


@r_digital_3d.route('/add', methods=['POST'])
@auth.login_required
def add_digital_3d():
    """
    @@@
    #### Args:
            {
               "TITLE": "",
               "CONTENT": "",
            }
    #### Returns::
            {'code': 20000, 'message': "添加成功"}
            {'code': 50001, 'message': "未知错误"}
    """

    args = request.get_json()
    stage = args.get('STAGE')

    try:
        old_digit = Digital3D.query.filter_by(STAGE=stage).first()
        if old_digit:
            return jsonify({'code': 50002, 'message': "stage repeated."})
        digital_3d = Digital3D()
        if 'RESULT' in args:
            args.pop('RESULT')
        if 'OPEN_TIME' in args:
            args['OPEN_TIME'] = datetime.strptime(args['OPEN_TIME'], "%Y-%m-%d %H:%M:%S") + timedelta(hours=1.5)
        if 'CLOSE_TIME' in args:
            args['CLOSE_TIME'] = datetime.strptime(args['CLOSE_TIME'], "%Y-%m-%d %H:%M:%S") + timedelta(hours=1.5)
        OrmUttil.set_field(digital_3d, args)
        digital_3d.CREATOR = g.user.NAME
        db.session.add(digital_3d)
        db.session.commit()
        user_opt.send({
            "operate": "添加3d数字盘",
            "route": "3d数字盘管理",
            "key_word": digital_3d.ID,
            "user": g.user.ACCOUNT
        })
        return jsonify({'code': 20000, 'message': "添加成功"})
    except Exception as e:
        print("add digit error:", e)

    return jsonify({'code': 50001, 'message': "未知错误"})


@r_digital_3d.route('/remove', methods=['POST'])
@auth.login_required
def remove_digital_3d():
    """
        @@@
        #### Args:
                {
                   "ID": '1553335644871',
                }
        #### Returns::
                {'code': 20000, 'message': "删除成功"}
                {'code': 50001, 'message': "未知错误"}
        """
    args = request.get_json()
    remove_id = args.get('ID')
    try:
        Digital3D.query.filter_by(ID=remove_id).delete()
        db.session.commit()
        user_opt.send({
            "operate": "删除3d数字盘",
            "route": "3d数字盘管理",
            "key_word": remove_id,
            "user": g.user.ACCOUNT
        })
        return jsonify({'code': 20000, 'message': "删除成功"})
    except Exception as e:
        print(e)
        return jsonify({
            'code': 50001,
            'message': "未知错误"
        })
