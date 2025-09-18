from subprocess import Popen

from flask import jsonify
from management_server import app, db, auth, user_opt, Redis
from management_server.model import GameType
from management_server.model.AppOperationModel import AppOperation
from management_server.model.OrderModel import Order, OrderType
from management_server.model.OrderHistoryModel import OrderHistory
from flask import g, request, jsonify, Blueprint
from management_server.utils import OrmUttil
from management_server.model.AppUserModel import AppUser
from sqlalchemy import or_, func
from datetime import datetime

from management_server.utils.OrmUttil import AppOpType
from management_server.utils.sphinxapi import *
import sys
import time

r_order = Blueprint('order', __name__)


# 获取订单列表
@r_order.route('/get_history', methods=['GET'])
# @auth.login_required
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
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    order_type = request.args.get('order_type', type=int)
    bet_type = request.args.get('bet_type', type=int)
    is_mix = request.args.get('is_mix', type=int)
    is_win = request.args.get('is_win', type=int)
    is_group = request.args.get('is_group', type=int, default=0)

    # 游戏类型 0:所有 1:比赛 2:数字
    game_type = request.args.get('game_type', type=int, default=1)

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
    if bet_type:
        cl.SetFilter('BET_TYPE', [bet_type])
    if is_mix:
        cl.SetFilter('IS_MIX', [is_mix])
    if is_win:
        cl.SetFilter('IS_WIN', [is_win])
    if is_group:
        cl.SetGroupBy('ORDER_GROUP', SPH_GROUPBY_ATTR, 'bonus desc')
    if game_type:
        if game_type == GameType.Match:
            cl.SetFilter('ORDER_TYPE', [1, 2, 3, 4, 5, 6, 7, 10])
        if game_type == GameType.Digit:
            cl.SetFilter('ORDER_TYPE', [8, 9])

    # if g.user.AGENT_CODE:
    #     query_str += "@AGENT_CODE %s" % g.user.AGENT_CODE

    print("final query str:", query_str)
    print("------", start_time, end_time)

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

    print("------", start_time, end_time)

    res = cl.Query(query_str, 'order_history;order_history_add')

    whole = {}
    bet_sum_dict = {}
    bet_bonus_dict = {}
    total_found = 0
    if res:
        whole = set()
        for o in res['matches']:
            print("--", o)
            whole.add(o['id'])
            attrs = o['attrs']
            bet_sum = attrs['bet_money']
            count = attrs.get('@count')
            if count and game_type == GameType.Digit:
                bet_sum *= count / 2
            bet_sum_dict[attrs['order_group']] = bet_sum
            bet_bonus_dict[attrs['order_group']] = attrs['bonus']
        total_found = res['total_found']

    total_bet = 0
    total_bonus = 0
    if total_found:
        cl.SetLimits(0, total_found, total_found)
        res = cl.Query(query_str, 'order_history;order_history_add')
        print("real found:", res['total'])
        for o in res['matches']:
            attrs = o['attrs']
            bet_sum = attrs['bet_money']

            count = attrs.get('@count')
            if count and game_type == GameType.Digit:
                bet_sum *= count / 2
            total_bet += bet_sum
            total_bonus += attrs['bonus']

    print("got paged result:", len(whole), "total_found:", total_bet, total_bonus, total_found)
    order_list = OrderHistory.query.filter(OrderHistory.ID.in_(whole))

    order_list = order_list.all()
    result = []
    for u in order_list:
        temp = u.to_dict()
        temp['BET_MONEY'] = bet_sum_dict[u.ORDER_ID]
        temp['BONUS'] = bet_bonus_dict[u.ORDER_ID]
        result.append(temp)

    return jsonify({
        'code': 20000,
        'items': result,
        'total': total_found,
        'total_bet': str(total_bet),
        'total_bonus': str(total_bonus)
    })


# 获取订单列表
@r_order.route('/get', methods=['GET'])
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

    order_list = Order.query.order_by(Order.CREATE_TIME.desc())

    if g.user.AGENT_CODE:
        users_under = AppUser.query.filter_by(AGENT_ID=g.user.AGENT_CODE).all()
        users_under = set([u.USER_ID for u in users_under])
        order_list = order_list.filter(Order.USER_ID.in_(users_under))

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
    if status:
        order_list = order_list.filter(Order.STATUS == status)
    if is_mix:
        order_list = order_list.filter(Order.IS_MIX == is_mix)
    if is_win:
        order_list = order_list.filter(Order.IS_WIN == is_win)
    if game_type:
        if game_type == GameType.Match:
            order_list = order_list.filter(Order.ORDER_TYPE.notin_(OrderType.AllDigit))
        if game_type == GameType.Digit:
            order_list = order_list.filter(Order.ORDER_TYPE.in_(OrderType.AllDigit))

    if start_time:
        start_time += " 00:00:00"
        order_list = order_list.filter(Order.CREATE_TIME >= start_time)

    if end_time:
        end_time += " 23:59:59"
        order_list = order_list.filter(Order.CREATE_TIME <= end_time)

    if is_group:
        order_list = order_list.group_by(Order.ORDER_ID)

    if not order_id and game_type == GameType.Digit:
        for o in order_list:
            bet_money_sum = Order.query.with_entities(func.sum(Order.BET_MONEY)).filter(Order.ORDER_ID == o.ORDER_ID).scalar() or 0
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


@r_order.route('/latest_list')
@auth.login_required
def latest_list():
    page_size = request.args.get("pageSize")
    # order_list = Order.query.order_by(Order.CREATE_TIME).group_by(Order.ORDER_ID).limit(page_size).all()
    order_list = Order.query.order_by(Order.CREATE_TIME).limit(page_size).all()

    return jsonify({'code': 20000, 'items': [u.to_dict() for u in order_list]})


@r_order.route('/remove', methods=['GET'])
@auth.login_required
def remove_order():
    """
                @@@
                #### Args:
                        remove_id = request.args.get('order_id')
                #### Returns::
                        {'code': 20000, 'message': "删除成功"}
                        {'code': 50001, 'message': "未知错误"}
            """
    remove_id = request.args.get('order_id')

    if remove_id:
        try:
            order = Order.query.filter_by(ID=remove_id).first_or_404()
            db.session.delete(order)
            db.session.commit()
            user_opt.send({
                "route": "订单管理",
                "operate": "删除订单",
                "key_word": remove_id,
                "user": g.user.ACCOUNT
            })
            return jsonify({'code': 20000, 'message': "删除成功"})
        except Exception as e:
            print("remove_bet_account del error: ", e)
    return jsonify({'code': 50001, 'message': "未知错误"})


@r_order.route('/refresh_sphinx_order', methods=['POST'])
@auth.login_required
def refresh_sphinx_order():
    """
        :author Li_sir
        :desc 手动刷新订单的sphinx缓存
    """
    import os
    # 防止频繁操作
    refresh = Redis.get("refresh")
    if refresh:
        return jsonify({'code': 50000, 'message': "请不要频繁操作"})
    else:
        os.system('/www/sphinx-3.1.1/bin/indexer -c /www/sphinx-3.1.1/etc/order_history.conf --all --rotate')
        Redis.set("refresh", 1, ex=60)
        return jsonify({'code': 20000, 'message': "操作成功"})


@r_order.route('/edit', methods=['GET'])
@auth.login_required
def edit_order():
    """
                "必填: edit_id 其他参数参照参考后台"
                @@@
                #### Args:
                        edit_id = request.args.get('order_id')

                        order_id = request.args.get('ORDER_ID')
                        user_id = request.args.get('USER_ID')
                        user_name = request.args.get('USER_NAME')
                        match_id = request.args.get('MATCH_ID')
                        order_type = request.args.get('ORDER_TYPE')
                        order_desc = request.args.get('ORDER_DESC')
                        bet_money = request.args.get('BET_MONEY')
                        bet_type = request.args.get('BET_TYPE')
                        remark = request.args.get('REMARK')
                        bet_host_team_result = request.args.get('BET_HOST_TEAM_RESULT')
                        bet_guest_team_result = request.args.get('BET_GUEST_TEAM_RESULT')
                        ball_type = request.args.get('BALL_TYPE')
                        status = request.args.get('STATUS')
                        is_mix = request.args.get('IS_MIX')
                        is_win = request.args.get('IS_WIN')
                        bonus = request.args.get('BONUS')
                        bet_odds = request.args.get('BET_ODDS')
                        draw_bunko = request.args.get('DRAW_BUNKO')
                        draw_odds = request.args.get('DRAW_ODDS')
                        lose_team = request.args.get('LOSE_TEAM')
                        lose_ball_num = request.args.get('LOSE_BALL_NUM')
                #### Returns::
                        {'code': 20000, 'message': "修改成功"}
                        {'code': 50001, 'message': "未知错误"}
            """
    edit_id = request.args.get('order_id')

    if edit_id:
        order = Order.query.filter_by(ID=edit_id).first_or_404()
        OrmUttil.set_field(order, request.args)
        db.session.commit()

        user_opt.send({
            "operate": "修改订单",
            "route": "订单管理",
            "key_word": edit_id,
            "user": g.user.ACCOUNT
        })
        return jsonify({'code': 20000, 'message': "修改成功"})
    else:
        return jsonify({'code': 50001, 'message': "未知错误"})


@r_order.route('/cancel', methods=['POST'])
@auth.login_required
def cancel_order():
    """
                @@@
                #### Args:
                        remove_id = request.args.get('order_id')
                #### Returns::
                        {'code': 20000, 'message': "删除成功"}
                        {'code': 50001, 'message': "未知错误"}
            """
    args = request.get_json()
    remove_ids = args.get('remove_ids')
    print("----canceling orders------", args)

    if not remove_ids:
        return jsonify({'code': 50001, 'message': "order not selected."})

    try:
        # 查询符合条件的订单
        orders = Order.query.filter(Order.ID.in_(remove_ids)).all()

        print(f"找到 {len(orders)} 条订单记录")

        for _order in orders:
            if _order.IS_MIX == "1":
                # 混合过关订单，更改比分为 100:100
                _order.BET_HOST_TEAM_RESULT = 100
                _order.BET_GUEST_TEAM_RESULT = 100
            else:
                _order.BONUS = _order.BET_MONEY
                _order.STATUS = 0
                _order.IS_WIN = 1
                # 创建订单历史记录
                order_history = OrderHistory()
                order_history.set_by_order(_order)
                order_history.BET_GUEST_TEAM_RESULT = 100
                order_history.BET_HOST_TEAM_RESULT = 100
                db.session.add(order_history)

                # 处理用户金额（转换为整数）
                app_user = AppUser.query.filter(AppUser.USER_ID == _order.USER_ID).first()
                if not app_user:
                    continue
                main_id = app_user.MAJUSER_ID
                del app_user
                app_user = AppUser.query.filter_by(MAJUSER_ID=main_id).with_for_update().first()
                # 确保金额转换为整数
                print("处理订单%s" % _order.ID)
                before_amount = int(float(app_user.TOTAL_MONEY))  # 先转float再转int，确保安全转换
                bet_money = int(float(_order.BET_MONEY))

                print(f'用户 {app_user.USER_ID} 原金额: {before_amount}')

                # 计算新金额
                after_amount = before_amount + bet_money
                app_user.TOTAL_MONEY = str(after_amount)  # 如果需要存为字符串

                opt = AppOperation(USER_ACCOUNT=app_user.USER_ID, TYPE=AppOpType.CANCEL, AMOUNT=before_amount,
                                   MATCH_ID=_order.MATCH_ID, BALANCE=after_amount, SOURCE_ID=_order.ORDER_ID)
                opt.DESC = "%s do order cancel at %s make % amount change" % (app_user.NICK_NAME, str(datetime.now().replace(microsecond=0)), bet_money)
                db.session.add(opt)

                print(f'扣除 {bet_money} 后金额: {after_amount}')
                db.session.delete(_order)

        user_opt.send({
            "operate": "取消订单",
            "route": "订单管理",
            "key_word": ",".join(remove_ids),
            "user": g.user.ACCOUNT
        })

        # 提交所有更改
        db.session.commit()
        compile_popen = Popen(app.config['SPHINX_COMMAND'], shell=True)
        compile_popen.wait()
        print(compile_popen.stdout)
        print("操作成功完成")
        return jsonify({'code': 20000, 'message': "cancel success"})

    except Exception as e:
        db.session.rollback()
        print(f"发生错误: {str(e)}")
    finally:
        db.session.close()

    return jsonify({'code': 50001, 'message': "未知错误"})
